# Industrial Process SCADA & Autonomous AI Diagnostics

An end-to-end industrial telemetry simulation, deterministic diagnostic engine, Stage 2 RUL prognostics engine, and Streamlit SCADA dashboard for process control instruments (LT-101, PT-101, TT-101, FT-101).

## Project Structure
```
├── app.py                  # Main Streamlit SCADA Application
├── dashboard.py            # Plotly Charts & Interactive Tank T-101 SVG Schematic
├── diagnostic_engine.py    # 4-20 mA Signal Processing & Deterministic Fault Engine
├── prognostics_engine.py   # Stage 2 RUL Mathematics & Safety SOP Generator
├── virtual_plant.py        # Process Physics & 9 Fault Injection Simulator
├── requirements.txt        # Python Dependencies
├── agents/
│   └── groq_client.py     # AI Field Technician Briefing Agent
└── README.md
```

## Setup & Execution

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```
