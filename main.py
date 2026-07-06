from connection.receiver import Receiver
from connection.parser import TelemetryParser
from brain.race_state import RaceState

def main():
    receiver = Receiver()
    parser = TelemetryParser()
    race_state = RaceState()

    receiver.start()
    print("Telemetry System Initialised. Waiting for data...")

    try:
        while True:
            raw_packet = receiver.receive()

            if not raw_packet:
                continue

            parsed_telemetry = parser.parse(raw_packet)

            # Update race state
            if parsed_telemetry:
                race_state.update(parsed_telemetry)
    
    except KeyboardInterrupt:
        print("\nStopping telemetry application...")

    finally:
        receiver.stop()
        print("Application Stopped")

if __name__ == "__main__":
    main()