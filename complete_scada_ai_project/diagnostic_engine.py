import datetime
import numpy as np

INSTRUMENT_CONFIG = {
    "LT_101": {
        "name": "Tank Level Transmitter",
        "unit": "%",
        "lrv": 0.0,
        "urv": 100.0,
        "low_alarm": 10.0,
        "high_alarm": 90.0,
    },
    "PT_101": {
        "name": "Pressure Transmitter",
        "unit": "bar",
        "lrv": 0.0,
        "urv": 10.0,
        "low_alarm": 1.0,
        "high_alarm": 8.5,
    },
    "TT_101": {
        "name": "Temperature Transmitter",
        "unit": "°C",
        "lrv": 0.0,
        "urv": 150.0,
        "low_alarm": 15.0,
        "high_alarm": 120.0,
    },
    "FT_101": {
        "name": "Flow Transmitter",
        "unit": "m³/h",
        "lrv": 0.0,
        "urv": 50.0,
        "low_alarm": 5.0,
        "high_alarm": 45.0,
    },
}


def ma_to_engineering(current_ma: float, lrv: float, urv: float) -> float:
    """Converts 4-20 mA signal to engineering units linearly."""
    return lrv + ((current_ma - 4.0) / 16.0) * (urv - lrv)


def analyze_history(history: list):
    """Analyzes historical current_ma array for stuck signal or high noise."""
    if not history or len(history) < 5:
        return {"stuck": False, "noisy": False, "std_dev": 0.0}

    arr = np.array(history)
    std_dev = float(np.std(arr))
    is_stuck = std_dev < 0.001
    is_noisy = std_dev > 0.40

    return {"stuck": is_stuck, "noisy": is_noisy, "std_dev": std_dev}


def evaluate_diagnostics(payload: dict) -> dict:
    """Processes Virtual Plant payload and outputs deterministic fault details."""
    tag = payload.get("tag")
    current_ma = payload.get("current_ma", 0.0)
    history = payload.get("history", [])
    plc_val = payload.get("plc_value", None)

    config = INSTRUMENT_CONFIG.get(tag, INSTRUMENT_CONFIG["LT_101"])
    eng_val = ma_to_engineering(current_ma, config["lrv"], config["urv"])
    hist_analysis = analyze_history(history)

    # Calculate PLC/DCS scaling delta
    plc_mismatch = False
    if plc_val is not None:
        delta = abs(plc_val - eng_val)
        if delta > (0.05 * (config["urv"] - config["lrv"])):
            plc_mismatch = True

    # Deterministic Decision Matrix (Priority Ordered)
    if current_ma <= 0.5:
        return {
            "status": "FAULT",
            "fault_code": "LOOP_LOSS",
            "diagnosis": f"Loop power loss detected on {tag}.",
            "probable_causes": [
                "Blown fuse on PLC I/O card",
                "Wire disconnection or open circuit",
                "Power supply failure",
            ],
            "troubleshooting_steps": [
                "Check 24V DC loop power supply voltage.",
                "Verify loop wiring continuity.",
                "Check terminal connection blocks.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "LOOP_LOSS",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": plc_mismatch},
        }

    if current_ma < 3.6:
        return {
            "status": "FAULT",
            "fault_code": "TRANSMITTER_UNDERRANGE",
            "diagnosis": f"Current signal ({current_ma} mA) below NAMUR NE43 lower threshold (3.6 mA).",
            "probable_causes": [
                "Sensor calibration drift below zero",
                "Hardware component failure",
            ],
            "troubleshooting_steps": [
                "Perform zero-point calibration using HART communicator.",
                "Check sensing element for physical damage.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "UNDERRANGE",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": plc_mismatch},
        }

    if current_ma > 21.0:
        return {
            "status": "FAULT",
            "fault_code": "TRANSMITTER_OVERRANGE",
            "diagnosis": f"Current signal ({current_ma} mA) exceeds upper safety bound (21.0 mA).",
            "probable_causes": [
                "Transmitter saturation",
                "Internal electronics short circuit",
            ],
            "troubleshooting_steps": [
                "Inspect sensor diaphragm/element for blockage.",
                "Verify transmitter range settings against process specification.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "OVERRANGE",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": plc_mismatch},
        }

    # Priority Check: Stuck or Noisy evaluated before scaling mismatch
    if hist_analysis["stuck"]:
        return {
            "status": "FAULT",
            "fault_code": "SIGNAL_STUCK",
            "diagnosis": f"Signal remains completely frozen at {current_ma} mA across history window.",
            "probable_causes": [
                "Transmitter firmware freeze",
                "Stuck ADC module",
                "Mechanical sense line blockage",
            ],
            "troubleshooting_steps": [
                "Power cycle the field transmitter.",
                "Check mechanical sensing line / impulse line for blockages.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "STUCK",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": plc_mismatch},
        }

    if hist_analysis["noisy"]:
        return {
            "status": "FAULT",
            "fault_code": "SIGNAL_UNSTABLE",
            "diagnosis": f"Excessive noise detected on signal (StdDev: {round(hist_analysis['std_dev'], 3)}).",
            "probable_causes": [
                "EMI / Ground loop interference",
                "Loose wiring terminal connection",
            ],
            "troubleshooting_steps": [
                "Check cable shielding and grounding point continuity.",
                "Inspect terminals for loose connections or corrosion.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "UNSTABLE",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": plc_mismatch},
        }

    if plc_mismatch:
        return {
            "status": "FAULT",
            "fault_code": "PLC_DCS_SCALING_MISMATCH",
            "diagnosis": f"Engineering value mismatch between field loop ({round(eng_val,2)}) and PLC tag value ({plc_val}).",
            "probable_causes": [
                "Incorrect raw scaling parameters (LRV/URV) configured in PLC I/O map",
                "Uncalibrated analog input channel card",
            ],
            "troubleshooting_steps": [
                "Verify 4-20 mA scaling parameters in PLC tag configuration.",
                "Cross-check I/O card calibration tables.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "SCALING_MISMATCH",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": True},
        }

    if eng_val > config["high_alarm"]:
        return {
            "status": "FAULT",
            "fault_code": "PROCESS_HIGH",
            "diagnosis": f"Process value {round(eng_val,2)} {config['unit']} exceeds high alarm boundary ({config['high_alarm']} {config['unit']}).",
            "probable_causes": [
                "Process disturbance or valve closure",
                "Inflow rate surge",
            ],
            "troubleshooting_steps": [
                "Check downstream valve positions and control loop setpoints.",
                "Inspect inlet control loop stability.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "HIGH_ALARM",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": False},
        }

    if eng_val < config["low_alarm"]:
        return {
            "status": "FAULT",
            "fault_code": "PROCESS_LOW",
            "diagnosis": f"Process value {round(eng_val,2)} {config['unit']} below low alarm boundary ({config['low_alarm']} {config['unit']}).",
            "probable_causes": [
                "Drain valve leak or pump overspeed",
                "Supply starvation",
            ],
            "troubleshooting_steps": [
                "Inspect outlet pump performance and valve position.",
                "Check upstream tank level and supply lines.",
            ],
            "engineering_value": round(eng_val, 2),
            "signal_status": "LOW_ALARM",
            "history_analysis": hist_analysis,
            "plc_dcs_comparison": {"mismatch": False},
        }

    return {
        "status": "NORMAL",
        "fault_code": None,
        "diagnosis": "Instrument operating normally within standard specifications.",
        "probable_causes": [],
        "troubleshooting_steps": [],
        "engineering_value": round(eng_val, 2),
        "signal_status": "NORMAL",
        "history_analysis": hist_analysis,
        "plc_dcs_comparison": {"mismatch": False},
    }
