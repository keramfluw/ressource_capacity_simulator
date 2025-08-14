
# Installer Economics – v2

Erweiterte Streamlit-App für die **Wochen-Wirtschaftlichkeit** mit:
- **Mehr-Mitarbeiter-Support** (Kosten & Kapazität skalieren automatisch)
- **Projekt→Gerät-Verteilung** via `Mix`-Tabelle (Anteile je Kategorie)
- **Auto-Planung**: füllt die Wochenkapazität (h) mit Einheiten nach maximalem **€ pro Stunde** unter Beachtung der **Verfügbarkeit** aus Projekten
- **Editierbarer Plan**, KPIs, Matplotlib-Chart und **Excel-Export**

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Start
```bash
streamlit run app.py
```

## Bedienlogik
1. **Gerätekatalog** pflegen (Zeiten, Vergütung, neue Geräte).
2. **Mix** festlegen: Anteile je Kategorie müssen in Summe ≈ 1,0 sein (App normalisiert robust).
3. **Projekte** pflegen: Summen je Kategorie (Wasserzähler, WMZ, KMZ, HKV).
4. Unter **Planung & KPIs**:
   - Kapazität = *Mitarbeiter* × *Stunden/Woche je Mitarbeiter*.
   - **Auto-Plan** priorisiert nach `€ pro h` (Vergütung / Montagezeit) und begrenzt durch verfügbare Mengen aus Projekten.
   - Manuelle Feinanpassung der geplanten Einheiten möglich.
   - KPIs (Umsatz, Kosten, Gewinn, Marge, Auslastung) und Diagramm.
   - **Export** erzeugt eine Excel mit allen Tabellen.

## Hinweise
- Lohnkosten gelten als **fix** (bezahlte Stunden), daher maximiert die Auto-Planung die **Umsatzdichte**.
- Zusatzkosten (km, Extras) und Lohn werden **pro Mitarbeiter** angesetzt.
- Wenn du statt Umsatz die **Deckungsbeiträge je Stunde** maximieren willst (Vergütung – Lohnzeitanteil), kann die Heuristik umgestellt werden.
