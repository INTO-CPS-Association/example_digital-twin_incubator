import sys
import time

sys.path.append("../communication/shared")
sys.path.append("../communication/server")
try:
    from connection_parameters import *
    from protocol import *
    from rabbitmq import TEST
except:
    raise
# from rabbitmq import Rabbitmq
print(PIKA_EXCHANGE)
# test_send = Rabbitmq()
# test_send.connect_to_server()
# test_send.send_message(routing_key="test", queue_name='test_queue', message="321")
#
# test_receive = Rabbitmq()
# test_receive.connect_to_server()
#
# test_receive.get_message(queue_name="test_queue", binding_key="test")
# print("received message 1st is", test_receive.body)
# # print(test_receive.body)
#
# # test_send.send_message(routing_key="asd", message="321")
# test_receive.get_message(queue_name="test_queue", binding_key="test")
# print("received message 2nd is", test_receive.body)
#
# test_receive.get_message(queue_name="test_queue", binding_key="test")
# print("received message 3rd is", test_receive.body)
#
# test_send.queue_delete('test_queue')

# class ControllerPhysical():
#     def __init__(self, desired_temperature=35.0, lower_bound=5, heating_time=0.2, heating_gap=0.3):
#         self.T_desired = desired_temperature
#
#         self.lower_bound = lower_bound
#
#         self.heating_time = heating_time
#         self.heating_gap = heating_gap
#
#         self.box_air_temperature = None
#
#         self.current_state = "CoolingDown"
#         self.next_time = -1.0
#
#         self.heater_on = None
#
#         self.rabbitmq = Rabbitmq()
#
#     def connect_server(self):
#         self.rabbitmq.connect_to_server()







# def ctrl_step(self):
#     if self.current_state == "CoolingDown":
#         # print("current state is: CoolingDown")
#         self.cached_heater_on = False
#         if self.in_temperature() <= self.T_desired - self.lower_bound:
#             self.current_state = "Heating"
#             self.next_time = self.time() + self.heating_time
#         return
#     if self.current_state == "Heating":
#         # print("current state is: Heating")
#         self.cached_heater_on = True
#         if 0 < self.next_time <= self.time():
#             self.current_state = "Waiting"
#             self.next_time = self.time() + self.heating_gap
#         return
#     if self.current_state == "Waiting":
#         # print("current state is: Waiting")
#         self.cached_heater_on = False
#         if 0 < self.next_time <= self.time():
#             if self.in_temperature() <= self.T_desired:
#                 self.current_state = "Heating"
#                 # print("next state is heating from waiting")
#                 self.next_time = self.time() + self.heating_time
#             else:
#                 self.current_state = "CoolingDown"
#                 self.next_time = -1
#         return
