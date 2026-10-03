import os

class DiagnosticAgent:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def format_technician_briefing(self, diagnostic_data: dict) -> str:
        status = diagnostic_data.get("status")
        fault_code = diagnostic_data.get("fault_code")
        eng_val = diagnostic_data.get("engineering_value")
        diag = diagnostic_data.get("diagnosis")
        causes = diagnostic_data.get("probable_causes", [])
        steps = diagnostic_data.get("troubleshooting_steps", [])

        if status == "NORMAL":
            return f"✅ **System Normal**: The instrument is operating within target parameters at **{eng_val}**."

        causes_formatted = "\n".join([f"  - {c}" for c in causes])
        steps_formatted = "\n".join([f"  {idx+1}. {s}" for idx, s in enumerate(steps)])

        return (
            f"🛠 **FIELD TECHNICIAN ACTION BRIEFING**\n\n"
            f"**Status:** `{status}` | **Fault Code:** `{fault_code}`\n\n"
            f"**Current Reading:** {eng_val}\n\n"
            f"**Diagnosis:** {diag}\n\n"
            f"**Probable Causes:**\n{causes_formatted}\n\n"
            f"**Recommended Action Steps:**\n{steps_formatted}"
        )
