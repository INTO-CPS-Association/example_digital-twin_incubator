import logging
from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from calibration.calibrator import Calibrator
from digital_twin.communication.rabbitmq_protocol import ROUTING_KEY_KF_PLANT_STATE, ROUTING_KEY_KF_UPDATE_PARAMETERS, \
    ROUTING_KEY_SELF_ADAPTATION_STATE, ROUTING_KEY_SELF_ADAPTATION_TRIGGER
from digital_twin.data_access.dbmanager.incubator_data_query import query_convert_aligned_data, query_most_recent_fields
from digital_twin.simulator.plant_simulator import PlantSimulator4Params
from incubator.communication.server.rabbitmq import Rabbitmq
from incubator.communication.shared.protocol import ROUTING_KEY_STATE, ROUTING_KEY_UPDATE_CTRL_PARAMS, from_s_to_ns, \
    from_ns_to_s
from interfaces.database import IDatabase
from interfaces.parametric_controller import IParametricController
from interfaces.updateable_kalman_filter import IUpdateableKalmanFilter
from models.physical_twin_models.system_model4_open_loop import SystemModel4ParametersOpenLoopSimulator
from self_adaptation.controller_optimizer import ControllerOptimizer, NoOPControllerOptimizer
from self_adaptation.self_adaptation_manager import SelfAdaptationManager


class SelfAdaptationManagerServer:

    def __init__(self, rabbit_config, influxdb_config, pt_config, dt_config):
        self._l = logging.getLogger("SelfAdaptationManagerServer")
        self.filter = None
        self.rabbitmq = Rabbitmq(**rabbit_config)
        self.dbclient = InfluxDBClient(**influxdb_config)
        self._influxdb_bucket = influxdb_config["bucket"]
        self._influxdb_org = influxdb_config["org"]

        # TODO: Move to config files.
        anomaly_threshold = 2.0
        # Time spent before declaring that there is an self_adaptation_manager, after the first time the self_adaptation_manager occurred.
        ensure_anomaly_timer = 1
        # Time spent, after the self_adaptation_manager was declared as detected, just so enough data about the system is gathered.
        # The data used for recalibration will be in interval [time_first_occurrence, time_data_gathered]
        gather_data_timer = 10
        cool_down_timer = 5
        conv_xatol = 0.1
        conv_fatol = 0.1
        max_iterations = 200
        desired_temperature = 41
        max_t_heater = 60
        restrict_T_heater = True
        optimize_controller = True

        database = DatabaseFacade(self.dbclient, self._influxdb_bucket, self._influxdb_org,
                                  dt_config["models"]["plant"]["param4"], pt_config["controller_open_loop"])

        # TODO: Invoke actual calibrator service, when the system is working.
        plant_simulator = PlantSimulator4Params()
        calibrator = Calibrator(database, plant_simulator, conv_xatol, conv_fatol, max_iterations)

        updateable_kalman_filter = UpdateableKalmanFilterFacade(self.rabbitmq)
        ctrl = ParametricControllerFacade(self.rabbitmq)

        pt_simulator = SystemModel4ParametersOpenLoopSimulator()

        if optimize_controller:
            ctrl_optimizer = ControllerOptimizer(database, pt_simulator, ctrl, conv_xatol, conv_fatol, max_iterations, restrict_T_heater, desired_temperature, max_t_heater)
        else:
            ctrl_optimizer = NoOPControllerOptimizer()

        self.self_adaptation_manager = SelfAdaptationManager(anomaly_threshold,
                                                             ensure_anomaly_timer, gather_data_timer, cool_down_timer,
                                                             calibrator, updateable_kalman_filter, ctrl_optimizer)
        self.sm = SelfAdaptationSignalCollectorSM(self.step_self_adaptation)

        self.next_step_is_self_adaptation = False

    def setup(self):
        self.rabbitmq.connect_to_server()

        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_STATE,
                                on_message_callback=self.consume_state_message)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_KF_PLANT_STATE,
                                on_message_callback=self.consume_kalmanfilter_message)
        self.rabbitmq.subscribe(routing_key=ROUTING_KEY_SELF_ADAPTATION_TRIGGER,
                                on_message_callback=self.trigger_self_adaptation)

    def start(self):
        self.rabbitmq.start_consuming()

    def consume_state_message(self, ch, method, properties, body_json):
        self._l.debug("State message received: ")
        self._l.debug(body_json)
        self.sm.step(body_json)

    def consume_kalmanfilter_message(self, ch, method, properties, body_json):
        self._l.debug("Kalman Filter message received: ")
        self._l.debug(body_json)
        self.sm.step(body_json)

    def trigger_self_adaptation(self, ch, method, properties, body_json):
        self._l.debug("Triggering self adaptation.")
        self.next_step_is_self_adaptation = True

    def step_self_adaptation(self, timestamp_ns, lld_measurement, kf_measurement):
        self._l.debug("Adaptation step")
        real_temperature = lld_measurement["fields"]["average_temperature"]
        predicted_temperature = kf_measurement["fields"]["average_temperature"]
        time_s = from_ns_to_s(timestamp_ns)
        self.self_adaptation_manager.step(real_temperature, predicted_temperature, time_s, self.next_step_is_self_adaptation)

        if self.next_step_is_self_adaptation:
            self.next_step_is_self_adaptation = False

        message = {
            "measurement": "self_adaptation_manager",
            "time": timestamp_ns,
            "tags": {
                "source": "self_adaptation_manager"
            },
            "fields": {
                "current_state": self.self_adaptation_manager.current_state,
                "anomaly_threshold": self.self_adaptation_manager.anomaly_threshold,
                "gather_data_timer": self.self_adaptation_manager.gather_data_timer,
                "ensure_anomaly_timer": self.self_adaptation_manager.ensure_anomaly_timer,
                "temperature_residual_abs": self.self_adaptation_manager.temperature_residual_abs,
                "anomaly_detected": self.self_adaptation_manager.anomaly_detected,
            }
        }
        self.rabbitmq.send_message(ROUTING_KEY_SELF_ADAPTATION_STATE, message)


class UpdateableKalmanFilterFacade(IUpdateableKalmanFilter):

    def __init__(self, rabbitmq):
        self._l = logging.getLogger("SelfAdaptationManagerServer")
        self.rabbitmq = rabbitmq

    def update_parameters(self, C_air, G_box, C_heater, G_heater):
        self._l.debug(f"Updating kalman filter parameters to: {C_air, G_box, C_heater, G_heater}")
        self.rabbitmq.send_message(ROUTING_KEY_KF_UPDATE_PARAMETERS, {
            "C_air": C_air,
            "G_box": G_box,
            "C_heater": C_heater,
            "G_heater": G_heater
        })


class ParametricControllerFacade(IParametricController):
    def __init__(self, rabbitmq):
        self._l = logging.getLogger("SelfAdaptationManagerServer")
        self.rabbitmq = rabbitmq

    def set_new_parameters(self, n_samples_heating_new, n_samples_period_new):
        self._l.debug(f"Updating open loop controller parameters to: {n_samples_heating_new, n_samples_period_new}")
        self.rabbitmq.send_message(ROUTING_KEY_UPDATE_CTRL_PARAMS, {
            "n_samples_heating": n_samples_heating_new,
            "n_samples_period": n_samples_period_new
        })


class DatabaseFacade(IDatabase):

    def __init__(self, dbclient, bucket, org, plant_params, ctrl_params):
        self._l = logging.getLogger("DatabaseFacade")
        self.dbclient = dbclient
        self.db_bucket = bucket
        self.db_org = org
        self.start_date_ns = from_s_to_ns(datetime.now().timestamp())
        self.plant_params = plant_params
        self.ctrl_params = ctrl_params

    def get_plant_signals_between(self, t_start_s, t_end_s):
        query_api = self.dbclient.query_api()

        start_date_ns = from_s_to_ns(t_start_s)
        end_date_ns = from_s_to_ns(t_end_s)

        time_seconds, results = query_convert_aligned_data(query_api, self.db_bucket, start_date_ns, end_date_ns,
                                                           {
                                                               "low_level_driver": ["t1",
                                                                                    "heater_on",
                                                                                    "average_temperature"],
                                                               "kalman_filter_plant": ["T_heater"]
                                                           })

        average_temperature_data = results["low_level_driver"]["average_temperature"]
        heater_data = results["low_level_driver"]["heater_on"]
        heater_temperature_data = results["kalman_filter_plant"]["T_heater"]
        room_temp_data = results["low_level_driver"]["t1"]

        self._l.debug("Converting data to lists.")
        time_seconds_list = list(time_seconds)
        average_temperature = average_temperature_data.tolist()
        heater_on = heater_data.tolist()
        heater_temperature = heater_temperature_data.tolist()
        room_temperature = room_temp_data.tolist()

        # Construct data structures to return:
        t_start_idx = 0
        t_end_idx = len(time_seconds_list)
        signals = {
            "time": time_seconds_list,
            "T": average_temperature,
            "in_heater_on": heater_on,
            "T_heater": heater_temperature,
            "in_room_temperature": room_temperature
        }
        return signals, t_start_idx, t_end_idx

    def store_calibrated_trajectory(self, times, calibrated_sol):
        # TODO
        pass

    def store_new_plant_parameters(self, start_time_s, C_air, G_box, C_heater, G_heater):
        self._l.debug(f"Sending new parameters to database: {C_air, G_box, C_heater, G_heater}")

        start_date_ns = from_s_to_ns(start_time_s)

        point = {
            "measurement": "plant_calibrator",
            "time": start_date_ns,
            "tags": {
                "source": "plant_calibrator",
                "variability": "parameter"
            },
            "fields": {
                "C_air": C_air,
                "G_box": G_box,
                "C_heater": C_heater,
                "G_heater": G_heater,
            }
        }
        write_api = self.dbclient.write_api(write_options=SYNCHRONOUS)
        write_api.write(self.db_bucket, self.db_org, point)

    def get_plant4_parameters(self):
        # Try to get the information from the influxdb
        query_api = self.dbclient.query_api()

        results = query_most_recent_fields(query_api, self.db_bucket, self.start_date_ns, 1,
                                                     ["plant_calibrator"],
                                                     ["C_air", "G_box", "C_heater", "G_heater"])

        if results.empty:
            # If that fails, return the default configuration
            C_air = self.plant_params["C_air"]
            G_box = self.plant_params["G_box"]
            C_heater = self.plant_params["C_heater"]
            G_heater = self.plant_params["G_heater"]
        else:
            C_air = results[results["_field"] == "C_air"]["_value"].iloc[0]
            G_box = results[results["_field"] == "G_box"]["_value"].iloc[0]
            C_heater = results[results["_field"] == "C_heater"]["_value"].iloc[0]
            G_heater = results[results["_field"] == "G_heater"]["_value"].iloc[0]

        return C_air, G_box, C_heater, G_heater

    def get_plant_snapshot(self):
        query_api = self.dbclient.query_api()
        results = query_most_recent_fields(query_api, self.db_bucket, self.start_date_ns, 1,
                                           ["low_level_driver", "kalman_filter_plant"],
                                           ["t1", "average_temperature", "T_heater"])
        T_heater = results[results["_field"] == "T_heater"]["_value"].iloc[0]
        T = results[(results["_field"] == "average_temperature") & (results["_measurement"] == "low_level_driver")]["_value"].iloc[0]
        room_T = results[results["_field"] == "t1"]["_value"].iloc[0]
        time_s = results["_time"].iloc[0].timestamp()

        return time_s, T, T_heater, room_T

    def get_ctrl_parameters(self):
        """
        Tries to get parameters from DB.
        If not there, then returns parameters from config
        """
        query_api = self.dbclient.query_api()

        results_int = query_most_recent_fields(query_api, self.db_bucket, self.start_date_ns, 1,
                                                     ["supervisor"],
                                                     ["n_samples_heating", "n_samples_period"])
        results_float = query_most_recent_fields(query_api, self.db_bucket, self.start_date_ns, 1,
                                                     ["supervisor"],
                                                     ["controller_step_size"])


        if results_int.empty or results_float.empty:
            # If that fails, return the default configuration
            n_samples_heating = self.ctrl_params["n_samples_heating"]
            n_samples_period = self.ctrl_params["n_samples_period"]
            # TODO: Replace this "magic" number with the value from the startup config file. Apply this all over the code.
            controller_step_size = 3.0
        else:
            # Conversion to int is necessary because these are int64, which cannot be encoded in JSON.
            n_samples_heating = int(results_int[results_int["_field"] == "n_samples_heating"]["_value"].iloc[0])
            n_samples_period = int(results_int[results_int["_field"] == "n_samples_period"]["_value"].iloc[0])
            controller_step_size = results_float[results_float["_field"] == "controller_step_size"]["_value"].iloc[0]

        return n_samples_heating, n_samples_period, controller_step_size

    def store_new_ctrl_parameters(self, start_time_s, n_samples_heating, n_samples_period, controller_step_size):
        self._l.debug(
            f"Sending new ctrl parameters to database: {n_samples_heating, n_samples_period, controller_step_size}")

        start_date_ns = from_s_to_ns(start_time_s)

        point = {
            "measurement": "supervisor",
            "time": start_date_ns,
            "tags": {
                "source": "supervisor",
                "variability": "parameter"
            },
            "fields": {
                "n_samples_heating": n_samples_heating,
                "n_samples_period": n_samples_period,
                "controller_step_size": controller_step_size,
            }
        }
        write_api = self.dbclient.write_api(write_options=SYNCHRONOUS)
        write_api.write(self.db_bucket, self.db_org, point)

    def store_controller_optimal_policy(self, times, T, T_heater, heater_on):
        # TODO
        pass


class SelfAdaptationSignalCollectorSM:

    def __init__(self, process_complete_system_snapshot_fun):
        self.state = "Initial"
        self.lld_measurement = None
        self.kf_measurement = None
        self.process_complete_system_snapshot_fun = process_complete_system_snapshot_fun

    def step(self, body_json):
        assert body_json["measurement"] == "low_level_driver" or body_json["measurement"] == "kalman_filter_plant"

        if self.state == "Initial":
            assert self.lld_measurement is None and self.kf_measurement is None
            if body_json["measurement"] == "low_level_driver":
                self.lld_measurement = body_json
                self.state = 'ExpectingKF'
            elif body_json["measurement"] == "kalman_filter_plant":
                self.kf_measurement = body_json
                self.state = 'ExpectingLLD'
        if self.state == "ExpectingKF":
            assert self.lld_measurement is not None
            assert self.kf_measurement is None
            if body_json["measurement"] == "low_level_driver":
                self.lld_measurement = body_json
            elif body_json["measurement"] == "kalman_filter_plant":
                """
                Three scenarios can happen:
                - [Past] The new KF measurements is older than the LLD measurement
                - [Present] The new KF measurement matches the LLD measurement
                - [Future] The new KF measurement is newer the LLD measurement
                """
                if body_json["time"] < self.lld_measurement["time"]:
                    # [Past]: Disregard KF measurement and stay in the same state (ie, do nothing)
                    pass
                elif body_json["time"] == self.lld_measurement["time"]:
                    # [Present]: We have a complete picture of the system, so we move to the next stage.
                    self.kf_measurement = body_json
                    self.process_complete_system_snapshot()
                elif body_json["time"] > self.lld_measurement["time"]:
                    # [Future]: Disregard LLD measurement and to go corresponding state
                    self.kf_measurement = body_json
                    self.lld_measurement = None
                    self.state = 'ExpectingLLD'
            return
        if self.state == "ExpectingLLD":
            assert self.lld_measurement is None
            assert self.kf_measurement is not None
            if body_json["measurement"] == "low_level_driver":
                """
                Three scenarios can happen:
                - [Past] The new LLD measurements is older than the KF measurement
                - [Present] The new LLD measurement matches the KF measurement
                - [Future] The new LLD measurement is newer the KF measurement
                """
                if body_json["time"] < self.kf_measurement["time"]:
                    # [Past]: Disregard LLD measurement and stay in the same state (ie, do nothing)
                    pass
                elif body_json["time"] == self.kf_measurement["time"]:
                    # [Present]: We have a complete picture of the system, so we move to the next stage.
                    self.lld_measurement = body_json
                    self.process_complete_system_snapshot()
                elif body_json["time"] > self.kf_measurement["time"]:
                    # [Future]: Disregard LLD measurement and to go corresponding state
                    self.lld_measurement = body_json
                    self.kf_measurement = None
                    self.state = 'ExpectingKF'
            elif body_json["measurement"] == "kalman_filter_plant":
                self.kf_measurement = body_json
            return

    def process_complete_system_snapshot(self):
        assert self.kf_measurement["time"] == self.lld_measurement["time"]
        self.process_complete_system_snapshot_fun(self.kf_measurement["time"], self.lld_measurement,
                                                  self.kf_measurement)
        self.kf_measurement = None
        self.lld_measurement = None
        self.state = "Initial"
