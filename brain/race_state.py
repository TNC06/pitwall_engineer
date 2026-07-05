class RaceState:

    def __init__(self):
        self.reset()

    def update(self):
     return

    def complete_lap(self):
       return

    def reset(self):
       self.current_lap=None
       self.speed=0
       self.gear = None
       self.throttle = 0.0
       self.brake = 0.0
       self.fuel = None
       self.tyre_wear = None
       self.position = None
       self.lap_history = []