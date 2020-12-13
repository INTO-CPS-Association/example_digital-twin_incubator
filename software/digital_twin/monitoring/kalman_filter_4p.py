from oomodelling import Model


class KalmanFilter4P(Model):
    def __init__(self, step_size, initial_room_temperature=25.0, initial_box_temperature=25.0):
        super().__init__()

        self.in_heater_on = self.input(lambda: False)
        self.in_room_T = self.input(lambda: initial_room_temperature)
        self.in_T = self.input(lambda: initial_box_temperature)

        self.cached_T = initial_box_temperature

        self.outT = self.var(lambda: self.cached_T)

        self.save()

    def kalman_step(self, in_heater, in_room_T, in_T):
        return in_T

    def discrete_step(self):
        self.cached_T = self.kalman_step(self.in_heater_on(), self.in_room_T(), self.in_T())
        return super().discrete_step()
