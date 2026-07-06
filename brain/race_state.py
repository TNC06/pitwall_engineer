class RaceState:

    def __init__(self):
        self.reset()

    def update(self, telemetry: dict):
     if not telemetry or "packet_id" not in telemetry:
        return
     
     packet_id = telemetry["packet_id"]
     data = telemetry.get("telemetry")

     # Packet 6: Car Telemetry Updates
     if packet_id == 6:
        self.speed = data.get("speed", self.speed)
        self.gear = data.get("gear", self.gear)
        self.throttle = data.get("throttle", self.throttle)
        self.brake = data.get("brake", self.brake)

     # Packet 7: Car Status Updates
     elif packet_id == 7:
        self.fuel = data.get("fuel_kilograms", self.fuel)

     # Packet 10: Car Damage Updates
     elif packet_id == 10:
        self.tyre_wear = data.get("tyre_degradation", self.tyre_wear)

     # Packet 2: Lap Data Updates
     elif packet_id == 2:
      self.position = data.get("car_position", self.position)
      new_lap = data.get("current_lap_num")
      
      # Capture active sector information continuously
      self.last_lap_time_ms = data.get("last_lap_time_ms", self.last_lap_time_ms)
      self.sector_1_time_ms = data.get("sector_1_time_ms", self.sector_1_time_ms)
      self.sector_2_time_ms = data.get("sector_2_time_ms", self.sector_2_time_ms)

      # Detect line crossing / lap change
      if (
        self.current_lap is not None
        and new_lap is not None
        and new_lap > self.current_lap
        ):
       self.complete_lap()
       if new_lap is not None:
          self.current_lap = new_lap

    def complete_lap(self):
       tyre_snapshot = (
            self.tyre_wear.copy() if isinstance(self.tyre_wear, dict) else {}
        )

       lap_record = {
            "lap_number": self.current_lap,
            "position": self.position,
            "lap_time_ms": self.last_lap_time_ms,
            "sector_1_ms": self.sector_1_time_ms,
            "sector_2_ms": self.sector_2_time_ms,
            # Calculate Sector 3 if game hasn't explicitly supplied it yet
            "sector_3_ms": (
                (self.last_lap_time_ms - self.sector_1_time_ms - self.sector_2_time_ms)
                if self.last_lap_time_ms and self.sector_1_time_ms and self.sector_2_time_ms
                else None
            ),
            "remaining_fuel_kg": self.fuel,
            "tyre_wear_snapshot": tyre_snapshot,
        }

       self.lap_history.append(lap_record)

       # Clean print log for terminal monitoring
       lap_s = lap_record["lap_time_ms"] / 1000.0
       print(f" Lap {self.current_lap} saved! Time: {lap_s:.3f}s")

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

       # Temporary variables to accurately hold individual sectors before archival
       self.last_lap_time_ms = None
       self.sector_1_time_ms = None
       self.sector_2_time_ms = None