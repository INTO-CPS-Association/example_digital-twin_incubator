import logging

from oomodelling import Model

from communication.server.rabbitmq import Rabbitmq
from digital_twin.models.controller_models.controller_model4 import ControllerModel4
from digital_twin.models.plant_models.four_parameters_model.four_parameter_model import FourParameterIncubatorPlant


class SampledRealTimeIncubator(Model):
    def __init__(self, C_air,
                 G_box,
                 C_heater,
                 G_heater,
                 lower_bound=10, heating_time=0.2, heating_gap=2.0,
                 desired_temperature=35,
                 initial_box_temperature=35,
                 comm=Rabbitmq(ip_raspberry="localhost")):
        super().__init__()

        self.ctrl = ControllerModel4(desired_temperature=desired_temperature, heating_time=heating_time, heating_gap=heating_gap,
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
        self.comm.declare_queue(queue_name='mock_plant_heater_in', routing_key="incubator.mock.hw.heater.on")

        self.save()



    def discrete_step(self):
        """
        Read heater setting from rabbitmq, and store it.
        Read plant temperature and upload it to rabbitmq.
        """


        return super().discrete_step()



if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)

    receiver = Rabbitmq(ip_raspberry="localhost")
    receiver.connect_to_server()
    receiver.declare_queue(queue_name='test_queue', routing_key="test")
