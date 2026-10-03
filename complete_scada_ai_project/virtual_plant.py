import datetime
import random
import numpy as np

class VirtualPlant:
    def __init__(self, tag="LT_101"):
        self.tag = tag
        self.reset_plant()

    def reset_plant(self):
        """Resets plant state back to normal operational baseline."""
        self.baseline_ma = 12.4  # Represents ~52.5% process level
        self.history = [12.4 + random.uniform(-0.02, 0.02) for _ in range(10)]
        self.plc_value = 52.5

    def get_timestamp(self):
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    def generate_payload(self, scenario: str) -> dict:
        timestamp = self.get_timestamp()
        
        if scenario == "NORMAL":
            self.reset_plant()
            ma = 12.4
            self.history.append(ma)
            self.history = self.history[-10:]
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": list(self.history),
                "plc_value": 52.5
            }

        elif scenario == "LOOP_LOSS":
            ma = 0.1
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": [0.1] * 10,
                "plc_value": 0.0
            }

        elif scenario == "UNDERRANGE":
            ma = 3.2
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": [3.2] * 10,
                "plc_value": -5.0
            }

        elif scenario == "OVERRANGE":
            ma = 21.8
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": [21.8] * 10,
                "plc_value": 111.25
            }

        elif scenario == "STUCK_SIGNAL":
            self.reset_plant()
            ma = 12.4
            stuck_history = [12.4] * 10
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": stuck_history,
                "plc_value": 52.5
            }

        elif scenario == "NOISY_SIGNAL":
            self.reset_plant()
            noisy_hist = [12.4 + random.uniform(-1.5, 1.5) for _ in range(10)]
            ma = noisy_hist[-1]
            eng_value = 0.0 + ((ma - 4.0) / 16.0) * 100.0
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": noisy_hist,
                "plc_value": round(eng_value, 2)
            }

        elif scenario == "PROCESS_HIGH":
            ma = 18.8
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": [18.8] * 10,
                "plc_value": 92.5
            }

        elif scenario == "PROCESS_LOW":
            ma = 5.2
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": [5.2] * 10,
                "plc_value": 7.5
            }

        elif scenario == "PLC_DCS_SCALING_MISMATCH":
            self.reset_plant()
            ma = 12.4
            return {
                "tag": self.tag,
                "current_ma": ma,
                "timestamp": timestamp,
                "history": list(self.history),
                "plc_value": 85.0
            }

        else:
            raise ValueError(f"Unknown scenario: {scenario}")
