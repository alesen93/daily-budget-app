import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
from streamlit_calendar import calendar

# Configurazione della pagina
st.set_page_config(page_title="Daily Budget App", page_icon="💰", layout="wide")
plt.style.use('ggplot')

# ✅ CSS: sidebar visibile, badge nascosti
st.markdown("""
    <style>
    footer {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    [data-testid="stSidebar"] { display: block !important; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "budget_data.csv"

# Stato iniziale
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False

VALID_CODES = ["IMPERO-DIGITALE-2024"]

# Carica dati se esistono
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Scadenza"])
else:
    df = pd.DataFrame(columns=["Categoria", "Importo", "Scadenza"])

# Sidebar
st.sidebar.title("💰 Menu")
pagina = st.sidebar.radio("📂 Sezioni", ["🏠 Home", "📈 Grafici", "🗓️ Agenda", "📁 Esporta", "🗑️ Reset dati", "🔐 Premium"])

# Funzione per salvare dati
def salva_df(df):
    df.to_csv(DATA_FILE, index=False)

# --- Premium ---
if pagina == "🔐 Premium":
    st.title("🔐 Sblocca la versione Premium")
    if not st.session_state.is_premium:
        codice = st.text_input("Inserisci codice premium")
        if st.button("Sblocca"):
            if codice in VALID_CODES:
                st.session_state.is_premium = True
                st.success("✅ Accesso Premium attivato!")
            else:
                st.error("❌ Codice non valido.")
    else:
        st.success("✅ Premium già attivo!")

# --- Home ---
elif pagina == "🏠 Home":
    st.title("🏠 Gestione Budget Mensile")

    reddito = st.number_input("💼 Reddito mensile (€)", min_value=0.0, step=100.0)
    spesa_fissa = st.number_input("🧾 Spese fisse (€)", min_value=0.0, step=10.0)

    st.subheader("➕ Aggiungi spese variabili")

    if "righe" not in st.session_state:
        st.session_state.righe = 1

    with st.form("form_spese"):
        nuove_spese = []
        for i in range(st.session_state.righe):
            cols = st.columns([2, 1, 1])
            catego




