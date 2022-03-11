from oomodelling import Model

from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.config.config import config_logger, load_config
from incubator.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from mock_plant.mock_connection import MOCK_HEATER_ON, MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3, MOCK_G_BOX
from mock_plant.real_time_model_solver import RTModelSolver
from models.plant_models.room_temperature_model import room_temperature
from physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL


class SampledRealTimePlantModel(Model):
    def __init__(self, C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 initial_box_temperature=21,
                 initial_heat_temperature=21,
                 comm=None, temperature_difference=6):
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

        # Wire G_box to the plant.G_box input, so that it can be changed from rabbitmq messages
        self.cached_G_box = G_box
        self.G_box = self.var(lambda: self.cached_G_box)
        self.plant.G_box = self.G_box

        # self.room_temperature = self.var(lambda: room_temperature(self.time()))
        # self.plant.in_room_temperature = self.room_temperature

        self.comm = comm
        self.comm.connect_to_server()
        self.heater_queue_name = self.comm.declare_local_queue(routing_key=MOCK_HEATER_ON)
        self.gbox_queue_name = self.comm.declare_local_queue(routing_key=MOCK_G_BOX)

        self.temperature_difference = temperature_difference

        # print("{:13}{:15}{:10}{:10}{:10}".format("time","heater_on", "t1", "t2", "t3"))

        self.save()

    def discrete_step(self):
        # Read G_box setting from rabbitmq, and store it.
        g_msg = self.comm.get_message(queue_name=self.gbox_queue_name)
        if g_msg is not None:
            self.cached_G_box = g_msg["G_box"]

        # Read heater setting from rabbitmq, and store it.
        heater_on = self.comm.get_message(queue_name=self.heater_queue_name)
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


def start_incubator_realtime_mockup(ok_queue=None, step_size=CTRL_EXEC_INTERVAL):
    config_logger("logging.conf")
    config = load_config("startup.conf")

    model = SampledRealTimePlantModel(**(config["digital_twin"]["models"]["plant"]["param4"]),
                                      comm=Rabbitmq(**(config["rabbitmq"])))

    solver = RTModelSolver()
    if ok_queue is not None:
        ok_queue.put("OK")
    solver.start_simulation(model, h=step_size, rt_factor=0.1)


if __name__ == '__main__':
    start_incubator_realtime_mockup()
