
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Installer Economics – v2", layout="wide")

st.title("Wirtschaftlichkeit pro Woche – Mehr-Mitarbeiter & Auto-Planung")

# ------------------ Defaults ------------------
def default_inputs():
    return {
        "Mitarbeiter": 1,
        "Stunden pro Woche je Mitarbeiter": 40.0,
        "Stunden pro Tag": 8.0,
        "Stundenlohn (€/h)": 28.0,
        "Kilometerpauschale (€/km)": 0.30,
        "km pro Mitarbeiter und Woche": 0.0,
        "Extra 1 (Bezeichnung)": "Spesen",
        "Extra 1 (€/Woche je Mitarbeiter)": 0.0,
        "Extra 2 (Bezeichnung)": "Hotel",
        "Extra 2 (€/Woche je Mitarbeiter)": 0.0,
    }

def default_rates():
    rows = [
        ("Wasserzähler","UP-MK Zähler",0.33,12.00),
        ("Wasserzähler","Aufputzzähler, Zapfhahnzähler + Zählwerkkopf",0.33,15.00),
        ("Wasserzähler","Hauswasserzähler (bis Q3=16)",0.50,20.00),
        ("Wasserzähler","Funkmodule WZ",0.17,5.00),
        ("Wasserzähler","Funkmodule WMZ",0.17,5.00),
        ("Wärmezähler / Kältezähler","Split WMZ bis QN 10,0 m³/h",0.75,75.00),
        ("Wärmezähler / Kältezähler","Split WMZ QN 15,0 - QN 40,0 m³/h",0.92,120.00),
        ("Wärmezähler / Kältezähler","Split WMZ größer QN 40,0 m³/h",1.01,170.00),
        ("Wärmezähler / Kältezähler","MK- und Verschraubungszähler bis QN 2,5m³/h",0.50,30.00),
        ("AMR","Montage Gateway",0.50,30.00),
        ("AMR","Montage Netzwerkknoten",0.42,30.00),
        ("HKVE","Neuausstattung und Austausch",0.75,7.50),
        ("HKVE","Neuasstattung und Austausch Fernfühler",0.50,15.00),
        ("Rauchmelder","Neuausstattung und Austausch",0.25,8.00),
    ]
    df = pd.DataFrame(rows, columns=["Kategorie","Gerät","Montageaufwand (h)","Vergütung pro Gerät (€)"])
    df["Einheiten/Woche"] = 0
    return df

def default_mix(rates_df):
    # gleichmäßige Verteilung je Kategorie
    rows = []
    for cat, sub in rates_df.groupby("Kategorie"):
        n = len(sub)
        share = 1.0/n if n>0 else 0.0
        for _, r in sub.iterrows():
            rows.append((cat, r["Gerät"], share))
    return pd.DataFrame(rows, columns=["Kategorie","Gerät","Anteil (0..1)"])

def default_projects():
    rows = [
        ("Berlin","Kleine Kurstraße",28,28,3,None),
        ("Berlin","Humboldhafen H3",306,114,16,None),
        ("Berlin","Humboldhafen H4",439,167,11,None),
        ("München","Residenzstraße",13,None,None,77),
        ("München","Sky Tower",50,105,79,24),
        ("München","Star Tower",29,54,41,34),
        ("München","Barthstraße",60,64,25,None),
        ("München","Montgelasstraße",None,None,None,None),
        ("München","Bayerstraße",100,114,31,None),
        ("München","Lyonel-Feiniger-Str.",None,None,None,None),
        ("Frankfurt","Edmund-Rumpler",56,100,None,None),
        ("Frankfurt","Börsenstraße",14,29,13,None),
        ("Frankfurt","Hanauer-Landstraße",265,153,7,None),
        ("Frankfurt","Bockenheimer-Lanstraße","15-20",None,None,None),
        ("Hamburg","Lindenstraße",426,335,None,None),
        ("Hamburg","Domstraße",None,None,None,None),
        ("Hamburg","Neuer Dovenhof",None,None,None,None),
        ("Frankfurt Projekt","Großgewerbe Zeil Frankfurt",297,336,346,None),
        ("Frankfurt Projekt","Hochhaus Frankfurt - Wohnungszähler",147,147,147,None),
        ("Frankfurt Projekt","Hochhaus Frankfurt - Bürozähler",None,66,66,None),
    ]
    return pd.DataFrame(rows, columns=["Stadt","Objekt","Wasserzähler","WMZ","KMZ","HKV"])

# ------------------ Sidebar: Inputs ------------------
st.sidebar.header("Basiswerte")
inp = default_inputs()
# editable inputs
inp["Mitarbeiter"] = int(st.sidebar.number_input("Mitarbeiter", value=inp["Mitarbeiter"], min_value=1, step=1))
inp["Stunden pro Woche je Mitarbeiter"] = float(st.sidebar.number_input("Stunden pro Woche je Mitarbeiter", value=float(inp["Stunden pro Woche je Mitarbeiter"]), min_value=0.0, step=1.0))
inp["Stunden pro Tag"] = float(st.sidebar.number_input("Stunden pro Tag", value=float(inp["Stunden pro Tag"]), min_value=0.0, step=0.5))
inp["Stundenlohn (€/h)"] = float(st.sidebar.number_input("Stundenlohn (€/h)", value=float(inp["Stundenlohn (€/h)"]), min_value=0.0, step=0.1, format="%.2f"))
inp["Kilometerpauschale (€/km)"] = float(st.sidebar.number_input("Kilometerpauschale (€/km)", value=float(inp["Kilometerpauschale (€/km)"]), min_value=0.0, step=0.01, format="%.2f"))
inp["km pro Mitarbeiter und Woche"] = float(st.sidebar.number_input("km pro Mitarbeiter und Woche", value=float(inp["km pro Mitarbeiter und Woche"]), min_value=0.0, step=1.0))
inp["Extra 1 (Bezeichnung)"] = st.sidebar.text_input("Extra 1 (Bezeichnung)", value=inp["Extra 1 (Bezeichnung)"])
inp["Extra 1 (€/Woche je Mitarbeiter)"] = float(st.sidebar.number_input("Extra 1 (€/Woche je Mitarbeiter)", value=float(inp["Extra 1 (€/Woche je Mitarbeiter)"]), min_value=0.0, step=1.0))
inp["Extra 2 (Bezeichnung)"] = st.sidebar.text_input("Extra 2 (Bezeichnung)", value=inp["Extra 2 (Bezeichnung)"])
inp["Extra 2 (€/Woche je Mitarbeiter)"] = float(st.sidebar.number_input("Extra 2 (€/Woche je Mitarbeiter)", value=float(inp["Extra 2 (€/Woche je Mitarbeiter)"]), min_value=0.0, step=1.0))

st.sidebar.caption("Alle Basiswerte gelten **pro Mitarbeiter** – App skaliert automatisch auf die gesamte Mannschaft.")

# ------------------ Tabs ------------------
tab1, tab2, tab3, tab4 = st.tabs(["1) Gerätekatalog", "2) Mix (Projekt→Gerät)", "3) Projekte", "4) Planung & KPIs"])

with tab1:
    st.subheader("Geräte, Zeiten & Vergütung")
    rates = default_rates()
    rates = st.data_editor(rates, num_rows="dynamic", use_container_width=True, hide_index=True, key="rates")

with tab2:
    st.subheader("Verteilungsschlüssel je Kategorie")
    if "mix" not in st.session_state:
        st.session_state["mix"] = default_mix(rates)
    # adjust mix if new devices/categories appear
    existing_pairs = set((a,b) for a,b in zip(st.session_state["mix"]["Kategorie"], st.session_state["mix"]["Gerät"]))
    for _, r in rates.iterrows():
        pair = (r["Kategorie"], r["Gerät"])
        if pair not in existing_pairs:
            st.session_state["mix"] = pd.concat([st.session_state["mix"], pd.DataFrame([{"Kategorie": r["Kategorie"], "Gerät": r["Gerät"], "Anteil (0..1)": 0.0}])], ignore_index=True)
    mix = st.data_editor(st.session_state["mix"], num_rows="dynamic", use_container_width=True, hide_index=True, key="mix_editor")
    st.caption("Hinweis: Die Summe der Anteile pro Kategorie sollte 1.0 (100%) ergeben.")

with tab3:
    st.subheader("Projektpipeline (Summen je Kategorie)")
    projects = default_projects()
    projects = st.data_editor(projects, num_rows="dynamic", use_container_width=True, hide_index=True, key="projects")
    # compute project totals per category
    def _to_num(x):
        if isinstance(x,str) and "-" in x:
            a,b = x.split("-",1)
            try:
                return (float(a)+float(b))/2.0
            except:
                return np.nan
        try:
            return float(x)
        except:
            return np.nan
    cats = ["Wasserzähler","WMZ","KMZ","HKV"]
    totals = {}
    for i,c in enumerate(cats, start=0):
        if c in projects.columns:
            totals[c] = pd.to_numeric(projects[c].apply(_to_num), errors="coerce").sum(skipna=True)
        else:
            totals[c] = 0.0
    st.write("**Projektsummen (über alle Zeilen):**", {k:int(v) for k,v in totals.items()})

with tab4:
    st.subheader("Planung")
    # compute available units per device from projects & mix
    mix_ok = mix.copy()
    # normalize shares per category to sum to 1 (robust)
    for cat, sub in mix_ok.groupby("Kategorie"):
        s = sub["Anteil (0..1)"].sum()
        if s > 0:
            mix_ok.loc[sub.index, "Anteil (0..1)"] = sub["Anteil (0..1)"] / s

    available = []
    for _, r in rates.iterrows():
        cat = r["Kategorie"]
        device = r["Gerät"]
        share = mix_ok[(mix_ok["Kategorie"]==cat) & (mix_ok["Gerät"]==device)]["Anteil (0..1)"]
        share = float(share.iloc[0]) if len(share)>0 else 0.0
        if cat == "Wasserzähler":
            base = totals.get("Wasserzähler", 0.0)
        elif cat == "Wärmezähler / Kältezähler":
            base = totals.get("WMZ", 0.0)
        elif cat == "AMR":
            base = totals.get("KMZ", 0.0)
        elif cat == "HKVE":
            base = totals.get("HKV", 0.0)
        elif cat == "Rauchmelder":
            base = totals.get("HKV", 0.0)  # falls vorhanden, sonst 0
        else:
            base = 0.0
        avail = np.floor(share * base)
        available.append(avail)
    plan_df = rates.copy()
    plan_df["Verfügbar (aus Projekten)"] = available
    plan_df["Einheiten/Woche"] = 0

    st.write("**Verfügbare Einheiten (abgeleitet aus Projekten × Mix):**")
    st.dataframe(plan_df[["Kategorie","Gerät","Montageaufwand (h)","Vergütung pro Gerät (€)","Verfügbar (aus Projekten)"]], use_container_width=True)

    # Capacity
    capacity_hours = inp["Mitarbeiter"] * inp["Stunden pro Woche je Mitarbeiter"]
    st.write(f"**Kapazität:** {capacity_hours:.2f} h pro Woche ({inp['Mitarbeiter']} MA × {inp['Stunden pro Woche je Mitarbeiter']} h)")

    if st.button("Auto-Plan (max. Umsatz pro Stunde, begrenzt durch Kapazität)"):
        df = plan_df.copy()
        # Sort by € per hour descending
        df["€ pro h"] = df["Vergütung pro Gerät (€)"] / df["Montageaufwand (h)"].replace(0,np.nan)
        df = df.sort_values(by="€ pro h", ascending=False)
        remaining_hours = capacity_hours
        units = []
        for _, r in df.iterrows():
            if r["Montageaufwand (h)"] <= 0:
                units.append(0)
                continue
            max_units_by_hours = np.floor(remaining_hours / r["Montageaufwand (h)"])
            max_units_by_supply = r["Verfügbar (aus Projekten)"]
            u = int(min(max_units_by_hours, max_units_by_supply))
            units.append(u)
            remaining_hours -= u * r["Montageaufwand (h)"]
            if remaining_hours <= 0:
                break
        # Map back
        df.loc[df.index[:len(units)], "Einheiten/Woche"] = units
        # merge back to original order
        plan_df = df.sort_index()
        st.session_state["autoplan"] = plan_df[["Kategorie","Gerät","Montageaufwand (h)","Vergütung pro Gerät (€)","Einheiten/Woche","Verfügbar (aus Projekten)"]]

    # Editable plan (start from autoplan if exists)
    if "autoplan" in st.session_state:
        editable_plan = st.data_editor(st.session_state["autoplan"], use_container_width=True, hide_index=True, key="plan_editor")
    else:
        editable_plan = st.data_editor(plan_df[["Kategorie","Gerät","Montageaufwand (h)","Vergütung pro Gerät (€)","Einheiten/Woche","Verfügbar (aus Projekten)"]],
                                       use_container_width=True, hide_index=True, key="plan_editor")

    # Calculations
    calc = editable_plan.copy()
    calc["Zeitbedarf (h)"] = calc["Montageaufwand (h)"] * calc["Einheiten/Woche"]
    calc["Umsatz (€)"] = calc["Vergütung pro Gerät (€)"] * calc["Einheiten/Woche"]
    total_hours = calc["Zeitbedarf (h)"].sum()
    total_rev = calc["Umsatz (€)"].sum()

    paid_hours_total = inp["Mitarbeiter"] * inp["Stunden pro Woche je Mitarbeiter"]
    labor_cost_fixed = paid_hours_total * inp["Stundenlohn (€/h)"]
    travel_cost = inp["Mitarbeiter"] * inp["Kilometerpauschale (€/km)"] * inp["km pro Mitarbeiter und Woche"]
    extra1 = inp["Mitarbeiter"] * inp["Extra 1 (€/Woche je Mitarbeiter)"]
    extra2 = inp["Mitarbeiter"] * inp["Extra 2 (€/Woche je Mitarbeiter)"]
    total_cost = labor_cost_fixed + travel_cost + extra1 + extra2
    profit = total_rev - total_cost
    margin = (profit / total_rev) if total_rev > 0 else 0.0
    util = (total_hours / paid_hours_total) if paid_hours_total > 0 else 0.0

    st.markdown("### KPIs gesamt")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Umsatz/Woche (gesamt)", f"{total_rev:,.2f} €")
    c2.metric("Gesamtkosten/Woche", f"{total_cost:,.2f} €")
    c3.metric("Gewinn/Woche", f"{profit:,.2f} €")
    c4.metric("Auslastung", f"{util:.1%}")
    c5, c6, c7 = st.columns(3)
    c5.metric("Arbeitskosten (fix)", f"{labor_cost_fixed:,.2f} €")
    c6.metric("Fahrtkosten", f"{travel_cost:,.2f} €")
    c7.metric("Marge", f"{margin:.1%}")

    st.markdown("### Detailtabelle (Plan)")
    st.dataframe(calc, use_container_width=True)

    st.markdown("### Visualisierung")
    fig, ax = plt.subplots()
    labels = ["Umsatz", "Gesamtkosten", "Gewinn"]
    values = [total_rev, total_cost, profit]
    ax.bar(labels, values)
    ax.set_ylabel("€ pro Woche (gesamt)")
    st.pyplot(fig)

    # -------- Export --------
    st.markdown("### Export")
    if st.button("Export Excel (aktueller Stand)"):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # Inputs per employee plus derived totals
            inputs_df = pd.DataFrame(list(inp.items()), columns=["Parameter","Wert"])
            inputs_df.to_excel(writer, sheet_name="Inputs", index=False)

            rates.to_excel(writer, sheet_name="Rates", index=False)
            mix.to_excel(writer, sheet_name="Mix", index=False)
            projects.to_excel(writer, sheet_name="Projects", index=False)
            editable_plan.to_excel(writer, sheet_name="WeeklyPlan", index=False)

            summary = pd.DataFrame({
                "Kennzahl": ["Mitarbeiter","Kapazität (h)","Geplante Stunden (h)","Umsatz","Gesamtkosten","Gewinn","Marge","Auslastung","Arbeitskosten (fix)","Fahrtkosten", inp["Extra 1 (Bezeichnung)"], inp["Extra 2 (Bezeichnung)"]],
                "Wert": [inp["Mitarbeiter"], paid_hours_total, total_hours, total_rev, total_cost, profit, margin, util, labor_cost_fixed, travel_cost, extra1, extra2],
            })
            summary.to_excel(writer, sheet_name="Summary", index=False)
        st.download_button("Excel herunterladen", data=output.getvalue(),
                           file_name="Installer_Economics_v2_Export.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
