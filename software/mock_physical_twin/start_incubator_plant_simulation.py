import logging
from datetime import datetime
from time import time

from oomodelling import Model

from communication.server.rabbitmq import Rabbitmq
from digital_twin.models.controller_models.controller_model4 import ControllerModel4
from digital_twin.models.plant_models.four_parameters_model.best_parameters import four_param_model_params
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant
from mock_physical_twin.mock_connection import MOCK_HEATER_ON, MOCK_TEMP_T1, MOCK_TEMP_T2, MOCK_TEMP_T3
from mock_physical_twin.real_time_model_solver import RTModelSolver


class SampledRealTimeIncubator(Model):
    def __init__(self, C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 lower_bound=10, heating_time=0.2, heating_gap=2.0,
                 desired_temperature=35,
                 initial_box_temperature=21,
                 comm=Rabbitmq(ip="localhost"), temperature_difference=6):
        super().__init__()

        self.ctrl = ControllerModel4(desired_temperature=desired_temperature, heating_time=heating_time,
                                     heating_gap=heating_gap,
                                     lower_bound=lower_bound)
        self.plant = FourParameterIncubatorPlant(initial_box_temperature=initial_box_temperature,
                                                 C_air=C_air,
                                                 G_box=G_box,
                                                 C_heater=C_heater,
                                                 G_heater=G_heater)
        self.cached_heater_on = False
        self.heater_on = self.var(lambda: self.cached_heater_on)

        self.plant.in_heater_on = self.heater_on

        self.comm = comm
        self.comm.connect_to_server()
        self.comm.declare_queue(queue_name=MOCK_HEATER_ON, routing_key=MOCK_HEATER_ON)

        self.temperature_difference = temperature_difference

        self.simulation_start_time = 0.0

        print("{:13}{:15}{:10}{:10}{:10}".format("time","heater_on", "t1", "t2", "t3"))

        self.save()

    def discrete_step(self):
        # Read heater setting from rabbitmq, and store it.
        heater_on = self.comm.get_message(queue_name=MOCK_HEATER_ON)
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

        print("{:%H:%M:%S}     {:15}{:<10.2f}{:<10.2f}{:<10.2f}".format(datetime.fromtimestamp(time()), str(self.cached_heater_on), t1, t2, t3), flush=True)
        return super().discrete_step()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # logging.getLogger("RTModelSolver").setLevel(logging.DEBUG)
    # logging.getLogger("RabbitMQClass").setLevel(logging.DEBUG)

    C_air_num = four_param_model_params[0]
    G_box_num = four_param_model_params[1]
    C_heater_num = four_param_model_params[2]
    G_heater_num = four_param_model_params[3]
    model = SampledRealTimeIncubator(C_air=C_air_num,
                                     G_box=G_box_num,
                                     C_heater=C_heater_num,
                                     G_heater=G_heater_num)

    solver = RTModelSolver()
    solver.start_simulation(model, h=3.0)
