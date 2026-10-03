import numpy as np

class PrognosticsEngine:
    def __init__(self, baseline_health: float = 100.0):
        self.baseline_health = baseline_health

    def calculate_rul(self, tag: str, current_ma: float, history: list, operating_hours: float = 5000.0) -> dict:
        if not history or len(history) < 2:
            return {
                "tag": tag,
                "health_index_pct": 100.0,
                "estimated_rul_days": 365,
                "degradation_rate": 0.0,
                "degradation_stage": "STAGE_1_HEALTHY",
                "recommended_sop": "Continue routine operational inspection."
            }

        arr = np.array(history)
        noise_level = float(np.std(arr))
        mean_val = float(np.mean(arr))
        drift_rate = abs(mean_val - 12.4) / (operating_hours + 1e-5)

        degradation_score = (noise_level * 15.0) + (drift_rate * 500.0)
        health_index = max(0.0, min(100.0, 100.0 - degradation_score))

        base_rul_days = 365.0
        rul_days = round(max(0.0, base_rul_days * (health_index / 100.0) ** 1.5), 1)

        if health_index > 80.0:
            stage = "STAGE_1_HEALTHY"
            sop = "Normal operation. Schedule standard annual calibration."
        elif health_index > 50.0:
            stage = "STAGE_2_MODERATE_DEGRADATION"
            sop = "Schedule preventative maintenance check within 30 days. Inspect loop terminal seals."
        elif health_index > 20.0:
            stage = "STAGE_3_SEVERE_DEGRADATION"
            sop = "High risk of failure. Order replacement instrument and schedule calibration immediately."
        else:
            stage = "STAGE_4_CRITICAL_IMMINENT_FAILURE"
            sop = "CRITICAL SAFETY RISK: Initiate bypass or controlled shutdown procedure and replace field transmitter immediately."

        return {
            "tag": tag,
            "health_index_pct": round(health_index, 2),
            "estimated_rul_days": rul_days,
            "degradation_rate": round(drift_rate, 6),
            "degradation_stage": stage,
            "recommended_sop": sop
        }
