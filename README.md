
# Installer Economics – v2 (fix, repacked)

- Headless Matplotlib (Backend **Agg**), automatischer Fallback auf Streamlit `bar_chart`.
- Enthält: **Auto-Plan** (40h-Optimierung), **Projekt→Gerät**-Verteilung, **Mehr-Mitarbeiter**-Dashboard, Excel-Export.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
