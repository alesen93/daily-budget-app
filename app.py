import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Daily Budget App", page_icon="💰", layout="wide")
plt.style.use('ggplot')

# 🔒 Nascondi footer e GitHub corner
st.markdown("""
    <style>
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    .viewerBadge_container__1QSob {display: none;}
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "budget_data.csv"

if "is_premium" not in st.session_state:
    st.session_state.is_premium = False

VALID_CODES = ["IMPERO-DIGITALE-2024"]

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE, parse_dates=["Scadenza"])
else:
    df = pd.DataFrame(columns=["Categoria", "Importo", "Scadenza"])

st.sidebar.title("💰 Menu")
pagina = st.sidebar.radio("📂 Sezioni", ["🏠 Home", "📈 Grafici", "🗓️ Agenda", "📁 Esporta", "🗑️ Reset dati", "🔐 Premium"])

def salva_df(df):
    df.to_csv(DATA_FILE, index=False)

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

if pagina == "🏠 Home":
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
            categoria = cols[0].text_input(f"Categoria {i+1}", key=f"cat_{i}")
            importo = cols[1].number_input(f"Importo {i+1} (€)", min_value=0.0, step=1.0, key=f"imp_{i}")
            scadenza = cols[2].date_input(f"Scadenza {i+1}", key=f"scad_{i}")
            if categoria and importo > 0:
                nuove_spese.append({
                    "Categoria": categoria,
                    "Importo": importo,
                    "Scadenza": pd.to_datetime(scadenza)
                })

        col_add, col_submit = st.columns([1, 2])
        if col_add.form_submit_button("➕ Aggiungi riga"):
            st.session_state.righe += 1
        salva = col_submit.form_submit_button("✅ Salva spese")

    if salva and nuove_spese:
        df = pd.concat([df, pd.DataFrame(nuove_spese)], ignore_index=True)
        salva_df(df)
        st.success("✅ Spese aggiunte!")

    spese_var = df["Importo"].sum()
    tot_spese = spesa_fissa + spese_var
    rimanente = reddito - tot_spese
    giornaliero = rimanente / 30 if rimanente > 0 else 0

    st.markdown(f"### 💸 Totale spese: **€{tot_spese:.2f}**")
    st.markdown(f"### 💰 Budget rimanente: **€{rimanente:.2f}**")
    st.markdown(f"### 📆 Spesa giornaliera consigliata: **€{giornaliero:.2f}**")

    if not df.empty:
        st.subheader("📊 Spese registrate")
        st.dataframe(df.sort_values("Scadenza").style.format({"Importo": "€{:.2f}"}), use_container_width=True)

elif pagina == "📈 Grafici":
    if st.session_state.is_premium:
        st.title("📈 Analisi delle Spese Premium")

        if not df.empty:
            tipo_grafico = st.selectbox("📊 Seleziona tipo di grafico", ["Torta", "Barre", "Linea"])
            grouped = df.groupby("Categoria")["Importo"].sum()

            fig, ax = plt.subplots()
            if tipo_grafico == "Torta":
                ax.pie(grouped, labels=grouped.index, autopct='%1.1f%%')
                ax.set_aspect("equal")
            elif tipo_grafico == "Barre":
                grouped.plot(kind="bar", ax=ax)
            elif tipo_grafico == "Linea":
                df_agg = df.groupby("Scadenza")["Importo"].sum().sort_index()
                df_agg.plot(kind="line", ax=ax, marker='o')

            st.pyplot(fig)
        else:
            st.warning("⚠️ Nessuna spesa disponibile.")
    else:
        st.warning("🔒 Solo utenti Premium possono vedere i grafici. Vai nella sezione 🔐 Premium per sbloccare.")

elif pagina == "🗓️ Agenda":
    if st.session_state.is_premium:
        st.title("🗓️ Calendario Scadenze Premium")

        if not df.empty:
            eventi = []
            for _, row in df.iterrows():
                eventi.append({
                    "title": f"{row['Categoria']} - €{row['Importo']:.2f}",
                    "start": row["Scadenza"].strftime("%Y-%m-%d"),
                    "end": row["Scadenza"].strftime("%Y-%m-%d")
                })

            calendar_options = {
                "initialView": "dayGridMonth",
                "editable": False,
                "selectable": False,
                "locale": "it"
            }

            calendar(events=eventi, options=calendar_options)
        else:
            st.info("🔍 Nessuna scadenza da mostrare.")
    else:
        st.warning("🔒 Solo utenti Premium possono accedere al calendario. Vai nella sezione 🔐 Premium per sbloccare.")

elif pagina == "📁 Esporta":
    st.title("📁 Esporta dati")

    if not df.empty:
        st.dataframe(df)
        st.download_button("⬇️ Scarica CSV", df.to_csv(index=False), file_name="budget_data.csv")

        st.subheader("📊 Esporta Grafico")

        tipo_grafico = st.selectbox("Tipo di grafico", ["Torta", "Barre", "Linea"], key="export_grafico")
        grouped = df.groupby("Categoria")["Importo"].sum()

        fig, ax = plt.subplots()
        if tipo_grafico == "Torta":
            ax.pie(grouped, labels=grouped.index, autopct='%1.1f%%')
            ax.set_aspect("equal")
        elif tipo_grafico == "Barre":
            grouped.plot(kind="bar", ax=ax)
        elif tipo_grafico == "Linea":
            df_agg = df.groupby("Scadenza")["Importo"].sum().sort_index()
            df_agg.plot(kind="line", ax=ax, marker='o')

        grafico_path = "grafico_spese.png"
        fig.savefig(grafico_path)
        st.image(grafico_path, caption="Grafico delle spese")

        with open(grafico_path, "rb") as f:
            st.download_button("⬇️ Scarica grafico PNG", f, file_name="grafico_spese.png")

        st.subheader("📆 Esporta calendario (in tabella)")

        scadenze_tabella = df[["Categoria", "Importo", "Scadenza"]].sort_values("Scadenza")
        calendario_path = "scadenze_tabella.png"

        fig2, ax2 = plt.subplots(figsize=(8, len(scadenze_tabella) * 0.5 + 1))
        ax2.axis("off")
        tabella = pd.plotting.table(ax2, scadenze_tabella, loc="center", cellLoc="center")
        tabella.scale(1, 1.5)
        fig2.tight_layout()
        fig2.savefig(calendario_path)

        st.image(calendario_path, caption="Calendario delle scadenze")

        with open(calendario_path, "rb") as f:
            st.download_button("⬇️ Scarica calendario PNG", f, file_name="calendario_scadenze.png")

    else:
        st.info("📭 Nessuna spesa da esportare.")

elif pagina == "🗑️ Reset dati":
    st.title("🗑️ Elimina tutti i dati")
    if st.button("❌ Cancella tutto"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        df = pd.DataFrame(columns=["Categoria", "Importo", "Scadenza"])
        st.session_state.righe = 1
        st.success("✅ Tutti i dati sono stati eliminati!")






