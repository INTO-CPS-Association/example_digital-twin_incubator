from oomodelling import Model

from communication.server.rabbitmq import Rabbitmq
from config.config import config_logger, load_config
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from digital_twin.models.plant_models.room_temperature_model import room_temperature
from mock_plant.mock_connection import MOCK_HEATER_ON, MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3
from mock_plant.real_time_model_solver import RTModelSolver


class SampledRealTimePlantModel(Model):
    def __init__(self, C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 initial_box_temperature=21,
                 initial_heat_temperature=21,
                 comm=Rabbitmq(ip="localhost"), temperature_difference=6):
        super().__init__()

        self.plant = FourParameterIncubatorPlant(initial_box_temperature=initial_box_temperature,
                                                 initial_heat_temperature=initial_heat_temperature,
                                                 C_air=C_air,
                                                 G_box=G_box,
                                                 C_heater=C_heater,
                                                 G_heater=G_heater)
        self.cached_heater_on = False
        self.heater_on = self.var(lambda: self.cached_heater_on)

        self.plant.in_heater_on = self.heater_on

        self.room_temperature = self.var(lambda: room_temperature(self.time()))
        self.plant.in_room_temperature = self.room_temperature

        self.comm = comm
        self.comm.connect_to_server()
        self.queue_name = self.comm.declare_local_queue(routing_key=MOCK_HEATER_ON)

        self.temperature_difference = temperature_difference

        # print("{:13}{:15}{:10}{:10}{:10}".format("time","heater_on", "t1", "t2", "t3"))

        self.save()

    def discrete_step(self):
        # Read heater setting from rabbitmq, and store it.
        heater_on = self.comm.get_message(queue_name=self.queue_name)
        if heater_on is not None:
            self.cached_heater_on = heater_on["heater"]

        # Read plant temperature and upload it to rabbitmq.
        t1 = self.plant.in_room_temperature()
        avg_temp = self.plant.T()
        t2 = avg_temp - self.temperature_difference / 2
        t3 = avg_temp + self.temperature_difference / 2
        self.comm.send_message(routing_key=MOCK_TEMP_T1, message=t1)
        self.comm.send_message(routing_key=MOCK_TEMP_T2, message=t2)
        self.comm.send_message(routing_key=MOCK_TEMP_T3, message=t3)

        # print("{:%H:%M:%S}     {:15}{:<10.2f}{:<10.2f}{:<10.2f}".format(datetime.fromtimestamp(time()), str(self.cached_heater_on), t1, t2, t3), flush=True)
        return super().discrete_step()


def start_incubator_realtime_mockup(ok_queue=None):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    model = SampledRealTimePlantModel(**(config["digital_twin"]["models"]["plant"]["param4"]))

    solver = RTModelSolver()
    if ok_queue is not None:
        ok_queue.put("OK")
    solver.start_simulation(model, h=3.0)


if __name__ == '__main__':
    start_incubator_realtime_mockup()
