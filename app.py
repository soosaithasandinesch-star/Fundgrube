# Fundgrube
# Startseite

import streamlit as st

# Seite-Konfiguration setzen (Titel und Icon im Browser-Tab)
st.set_page_config(
    page_title="Schul-Fundbüro",
    page_icon="📦",
    layout="centered"
)

# Custom CSS zur optischen Anpassung an deinen Screenshot
st.markdown("""
    <style>
    /* Hintergrundfarbe der App sanft anpassen */
    .stApp {
        background-color: #f4f8fb;
    }
    
    /* Haupt-Container begrenzen und als Karte / Smartphone-Form stylen */
    .block-container {
        max-width: 400px;
        background-color: #ffffff;
        padding: 40px 25px;
        margin-top: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        border: 1px solid #dbe5f1;
        text-align: center;
    }

    /* Überschriften-Design */
    .title-text {
        font-family: 'Arial', sans-serif;
        font-weight: 800;
        font-size: 24px;
        color: #1a1a1a;
        margin-top: 15px;
        margin-bottom: 10px;
        line-height: 1.2;
    }

    /* Untertitel / Anweisungstext */
    .sub-text {
        font-family: 'Arial', sans-serif;
        font-size: 14px;
        color: #4a4a4a;
        margin-bottom: 25px;
    }

    /* Button-Design anpassen */
    .stButton > button {
        width: 100%;
        background-color: #3b719f;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 16px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #2c567a;
        color: white;
    }

    /* Input-Feld zentrieren */
    div[data-baseweb="input"] {
        border-radius: 12px;
    }
    input {
        text-align: center !important;
        font-weight: bold !important;
        letter-spacing: 1px;
    }
    </style>
""", unsafe_allow_html=True)

# Session State für den App-Zustand initialisieren
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'school_code' not in st.session_state:
    st.session_state.school_code = ""


# ---------------------------------------------------------
# SEITE 1: LOGIN / STARTSEITE
# ---------------------------------------------------------
if not st.session_state.logged_in:
    # 1. Icon (Paket-Box)
    st.markdown("<div style='font-size: 70px; text-align: center; margin-bottom: -10px;'>📦</div>", unsafe_allow_html=True)
    
    # 2. Überschrift & Hinweistext
    st.markdown("<div class='title-text'>Willkommen im<br>Schul-Fundbüro</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-text'>Bitte gib den Zugangscode<br>deiner Schule ein:</div>", unsafe_allow_html=True)
    
    # 3. Eingabefeld
    code_input = st.text_input(
        label="Zugangscode",
        placeholder="SCHULE-2026-X",
        label_visibility="collapsed"
    )
    
    # 4. Start-Button
    if st.button("App Starten"):
        if code_input.strip() != "":
            # Logik beim Klicken: Code speichern und einloggen
            st.session_state.school_code = code_input
            st.session_state.logged_in = True
            st.rerun() # Seite neu laden
        else:
            st.error("Bitte gib einen gültigen Zugangscode ein.")

# ---------------------------------------------------------
# SEITE 2: FUNDGRUBE (Nach erfolgreicher Eingabe)
# ---------------------------------------------------------
else:
    st.success(f"Angemeldet mit Code: **{st.session_state.school_code}**")
    st.title("🔍 Fundgrube")
    
    st.write("Hier sind die aktuell gefundenen Gegenstände deiner Schule:")
    
    # Beispiel-Interaktion in der App:
    search_item = st.text_input("Gegenstand suchen (z. B. Jacke, Schlüssel, Sportbeutel)")
    
    st.divider()
    
    # Beispiel-Inhalte anzeigen
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🧥 Blaue Jacke")
        st.caption("Gefunden am: 05.09.")
        if st.button("Das ist meins!", key="item1"):
            st.toast("Anfrage für die blaue Jacke gesendet!")

    with col2:
        st.subheader("🔑 Schlüsselbund")
        st.caption("Gefunden am: 07.09.")
        if st.button("Das ist meins!", key="item2"):
            st.toast("Anfrage für den Schlüsselbund gesendet!")

    st.divider()
    
    # Logout-Button zum Testen
    if st.button("Abmelden"):
        st.session_state.logged_in = False
        st.session_state.school_code = ""
        st.rerun()
