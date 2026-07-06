import struct

class TelemetryParser:

    def __init__(self):
        
        pass

    def parse(self, raw_packet):
        """
        Main entry point.
        """
        header = self._parse_header(raw_packet)
        if not header:
            return None
        
        packet_id = header["packet_id"]

        parsed_data = None
        if packet_id == 6:  # Car Telemetry Packet
            parsed_data = self._parse_car_telemetry(raw_packet, header)
        elif packet_id == 1:  # Session Packet
            parsed_data = self._parse_session(raw_packet)
        elif packet_id == 2:  # Lap Data Packet
            parsed_data = self._parse_lap(raw_packet, header)
        elif packet_id == 7:  # Car Status Packet (ERS data lives here)
            parsed_data = self._parse_car_status(raw_packet, header)
        elif packet_id == 10:  # Car Damage Packet (Tyre degradation lives here)
            parsed_data = self._parse_car_damage(raw_packet, header)

        return {
            "header": header,
            "packet_id": packet_id,
            "telemetry": parsed_data,
        }


    def _parse_header(self, raw_packet):
        """
        Decode the packet header.
        """
        if len(raw_packet) < 29:
            return None
        unpacked_header = struct.unpack(self._HEADER_STRUCT, raw_packet[:29])

        return {
            "packet_format": unpacked_header[0],  
            "game_year": unpacked_header[1],  
            "game_major_version": unpacked_header[2],
            "game_minor_version": unpacked_header[3],
            "packet_version": unpacked_header[4],
            "packet_id": unpacked_header[5],  
            "session_uid": unpacked_header[6],
            "session_time": unpacked_header[7],
            "frame_identifier": unpacked_header[8],
            "overall_loop_counter": unpacked_header[9],
            "player_car_index": unpacked_header[10], 
        }


    def _parse_car_telemetry(self, raw_packet, header):
        """
        Decode telemetry packet.
        """
        player_idx = header["player_car_index"]
        car_telemetry_size = 64
        car_offset = 29 + (player_idx * car_telemetry_size)

        if len(raw_packet) < (car_offset + 14):
            return None
        
        car_bytes = raw_packet[car_offset : car_offset + 9]
        speed, throttle, steer, brake, gear, rpm, drs = struct.unpack(
            "<HBBbBHB", car_bytes
        )

        return {
            "speed": speed,  
            "throttle": throttle / 100.0, 
            "brake": brake / 100.0,
            "gear": gear - 1, 
            "rpm": rpm, 
            "drs": bool(drs),  
        }

    def _parse_car_status(self, raw_packet, header):
        """
        Decode car status packet to extract ERS battery percentages.
        """
        player_idx = header["player_car_index"]
        car_status_size = 47
        car_offset = 29 + (player_idx * car_status_size)

        try:
            ers_energy_offset = car_offset + 25
            ers_store_energy = struct.unpack(
                "<f", raw_packet[ers_energy_offset : ers_energy_offset + 4]
            )[0]
            ers_battery_percentage = (ers_store_energy / 4000000.0) * 100.0

            return {"ers_battery_percentage": round(ers_battery_percentage, 1)}
        except Exception:
            return None

    def _parse_car_damage(self, raw_packet, header):
        """
        Decode car damage packet to extract tyre degradation levels.
        """
        player_idx = header["player_car_index"]
        car_damage_size = 42
        car_offset = 29 + (player_idx * car_damage_size)

        # The first 4 bytes of the car damage block contain tyre wear percentages
        # 4 x 'f' (float) values representing: Rear Left, Rear Right, Front Left, Front Right
        try:
            tyre_wear_bytes = raw_packet[car_offset : car_offset + 16]
            rl, rr, fl, fr = struct.unpack("<ffff", tyre_wear_bytes)
            return {
                "tyre_degradation": {
                    "rear_left": round(rl, 1),  # Percentage (0.0 to 100.0)
                    "rear_right": round(rr, 1),
                    "front_left": round(fl, 1),
                    "front_right": round(fr, 1),
                }
            }
        except Exception:
            return None

    def _parse_session(self, raw_packet):
        """
        Decode session packet.
        """
        if len(raw_packet) < 36:
            return None

        # Extract primary environment blocks: B=weather, b=track_temp, b=air_temp, H=total_laps
        session_bytes = raw_packet[29:34]
        weather, track_temp, air_temp, total_laps = struct.unpack(
            "<BbbH", session_bytes
        )

        return {
            "weather": weather,  # 0=Clear, 1=Light Cloud, 2=Overcast etc.
            "track_temperature": track_temp,  
            "air_temperature": air_temp,  
            "total_laps": total_laps,
        }

    def _parse_lap(self, raw_packet,header):
        """
        Decode lap packet.
        """
        player_idx = header["player_car_index"]
        lap_offset = 29 + (player_idx * 53)

        if len(raw_packet) < (lap_offset + 53):
            return None

        # Unpack first timing variables: I=last_lap, I=current_lap, H=sector1
        last_lap, curr_lap, s1 = struct.unpack("<IIH", raw_packet[lap_offset : lap_offset + 10])
        car_pos = struct.unpack("<B", raw_packet[lap_offset + 41 : lap_offset + 42])[0]
        lap_num = struct.unpack("<B", raw_packet[lap_offset + 43 : lap_offset + 44])[0]

        return {
            "last_lap_time_ms": last_lap,
            "current_lap_time_ms": curr_lap,
            "sector_1_time_ms": s1,
            "car_position": car_pos, 
            "current_lap_num": lap_num,  
        }