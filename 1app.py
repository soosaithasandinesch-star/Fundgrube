import streamlit as st
import datetime
from PIL import Image

# ---------------------------------------------------------
# 1. KONFIGURATION & STYLING (UI)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Schul-Fundbüro",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS für die Smartphone-Karten-Optik
st.markdown("""
    <style>
    .stApp { background-color: #f4f8fb; }
    .block-container {
        max-width: 450px;
        background-color: #ffffff;
        padding: 30px 20px;
        margin-top: 20px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
    }
    .main-title {
        text-align: center;
        font-weight: 800;
        font-size: 24px;
        color: #1a1a1a;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 14px;
        color: #657786;
        margin-bottom: 25px;
    }
    /* Buttons stilen */
    div.stButton > button {
        width: 100%;
        border-radius: 12px;
        padding: 10px 16px;
        font-weight: 600;
    }
    .ki-box {
        background-color: #eef6ff;
        border: 1px dashed #2b78e4;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        color: #1c529b;
        font-size: 13px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SESSION STATE (DATENBANK-ERSATZ & ZUSTAND)
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "menu"  # menu, found, lost, matches, list

# In-Memory Daten (Später durch eine Datenbank wie SQLite/PostgreSQL ersetzen)
if 'found_items' not in st.session_state:
    st.session_state.found_items = []

if 'lost_items' not in st.session_state:
    st.session_state.lost_items = []

if 'matches' not in st.session_state:
    st.session_state.matches = []

# Kategorien und Orte für konsistente Eingaben
CATEGORIES = ["Trinkflasche", "Jacke/Kleidung", "Schlüssel", "Tasche/Rucksack", "Schulsachen", "Elektronik", "Sonstiges"]
COLORS = ["Blau", "Schwarz", "Rot", "Grün", "Gelb", "Weiß", "Grau", "Bunt"]
LOCATIONS = ["Sporthalle", "Pausenhof", "Mensa", "Flur EG", "Flur 1. OG", "Klassenzimmer", "Unbekannt"]

# ---------------------------------------------------------
# 3. KI-PLATZHALTER-FUNKTION
# ---------------------------------------------------------
def analyze_image_with_ai(image):
    """
    Hier kannst du später deinen KI-Code einbinden (z. B. OpenAI GPT-4o, Google Gemini API etc.)
    """
    # Dummy KI-Erkennung für Testzwecke:
    return {
        "kategorie": "Trinkflasche",
        "farbe": "Blau",
        "hinweis": "Automatisch von KI als blaue Flasche erkannt"
    }

# ---------------------------------------------------------
# SCREEN 1: LOGIN (Zugangscode "BigD")
# ---------------------------------------------------------
if not st.session_state.logged_in:
    st.markdown("<div style='font-size: 60px; text-align: center;'>📦</div>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Willkommen im<br>Schul-Fundbüro</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Bitte gib den Zugangscode deiner Schule ein:</div>", unsafe_allow_html=True)

    code_input = st.text_input("Zugangscode", type="password", placeholder="Zugangscode eingeben", label_visibility="collapsed")
    
    if st.button("App Starten", type="primary"):
        if code_input == "BigD":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Falscher Zugangscode! (Hinweis: Password ist 'BigD')")

# ---------------------------------------------------------
# ANGEMELDETER BEREICH (HAUPT-APP)
# ---------------------------------------------------------
else:
    # Navigation-Header (Profil / Logout)
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.caption("🏫 Schul-Fundbüro")
    with col_head2:
        if st.button("Abmelden", key="logout"):
            st.session_state.logged_in = False
            st.rerun()

    # -----------------------------------------------------
    # SCREEN 2: HAUPTMENÜ ("Was möchtest du tun?")
    # -----------------------------------------------------
    if st.session_state.current_screen == "menu":
        st.subheader("Was möchtest du tun?")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📷\n\nIch habe etwas\nGEFUNDEN", use_container_width=True):
                st.session_state.current_screen = "found"
                st.rerun()
        with c2:
            if st.button("🔍\n\nIch habe etwas\nVERLOREN", use_container_width=True):
                st.session_state.current_screen = "lost"
                st.rerun()

        st.write("")
        c3, c4 = st.columns(2)
        with c3:
            if st.button("📋\n\nFundstücke\ndurchsuchen", use_container_width=True):
                st.session_state.current_screen = "list"
                st.rerun()
        with c4:
            match_count = len(st.session_state.matches)
            badge = f" ({match_count})" if match_count > 0 else ""
            if st.button(f"🔔\n\nMeine Meldungen\n& Treffer{badge}", use_container_width=True):
                st.session_state.current_screen = "matches"
                st.rerun()

    # -----------------------------------------------------
    # SCREEN 3: FUNDSTÜCK ERFASSEN ("Ich habe etwas gefunden")
    # -----------------------------------------------------
    elif st.session_state.current_screen == "found":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Fundstück melden")
        st.write("### 1. Foto machen oder hochladen")
        
        uploaded_file = st.file_uploader("Foto aufnehmen", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        
        # KI-Vorausfüllung initialisieren
        detected_category = CATEGORIES[0]
        detected_color = COLORS[0]

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Hochgeladenes Foto", use_container_width=True)
            
            # KI Analyse ausführen
            ai_results = analyze_image_with_ai(image)
            detected_category = ai_results["kategorie"]
            detected_color = ai_results["farbe"]

            st.markdown(f"""
                <div class="ki-box">
                    🤖 <b>KI analysiert Bild...</b><br>
                    Automatische Erkennung: <b>{detected_category}</b>, <b>{detected_color}</b>
                </div>
            """, unsafe_allow_html=True)

        st.write("### 2. Daten überprüfen & anpassen:")
        
        cat_idx = CATEGORIES.index(detected_category) if detected_category in CATEGORIES else 0
        col_idx = COLORS.index(detected_color) if detected_color in COLORS else 0

        cat = st.selectbox("* Kategorie", CATEGORIES, index=cat_idx)
        color = st.selectbox("* Hauptfarbe", COLORS, index=col_idx)
        loc = st.selectbox("* Fundort", LOCATIONS)
        time_found = st.text_input("* Datum/Zeit", value=f"Heute, ca. {datetime.datetime.now().strftime('%H:%M')} Uhr")
        note = st.text_input("Hinweis", placeholder="z. B. Schwarzer Deckel, Kratzer am Boden")

        if st.button("Fundstück Speichern", type="primary"):
            new_item = {
                "id": len(st.session_state.found_items) + 1,
                "kategorie": cat,
                "farbe": color,
                "ort": loc,
                "zeit": time_found,
                "hinweis": note,
                "status": "im_fundbuero"
            }
            st.session_state.found_items.append(new_item)
            
            # AUTOMATISCHER ABGLEICH (MATCHING)
            for lost in st.session_state.lost_items:
                if lost["kategorie"] == cat and lost["farbe"] == color:
                    st.session_state.matches.append({
                        "found_item": new_item,
                        "lost_item": lost
                    })

            st.success("Fundstück erfolgreich gespeichert!")
            st.session_state.current_screen = "menu"
            st.rerun()

    # -----------------------------------------------------
    # SCREEN 4: VERLUSTMELDUNG ERSTELLEN
    # -----------------------------------------------------
    elif st.session_state.current_screen == "lost":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Verlustmeldung erstellen")
        
        cat = st.selectbox("* Was hast du verloren?", CATEGORIES)
        color = st.selectbox("* Farbe", COLORS)
        loc = st.selectbox("* Wo vermutlich verloren?", LOCATIONS)
        time_lost = st.selectbox("* Wann ungefähr?", ["Heute", "Gestern", "Diese Woche", "Vor längerer Zeit"])
        details = st.text_area("Details", placeholder="Beschreibe den Gegenstand möglichst genau...")
        
        st.write("**Notification Preferences:**")
        notify = st.radio("Benachrichtigung", ["Per E-Mail", "Nur in der App"], label_visibility="collapsed")

        if st.button("Suchmeldung aufgeben", type="primary"):
            new_lost = {
                "id": len(st.session_state.lost_items) + 1,
                "kategorie": cat,
                "farbe": color,
                "ort": loc,
                "details": details
            }
            st.session_state.lost_items.append(new_lost)

            # Automatischen Abgleich durchführen
            for found in st.session_state.found_items:
                if found["kategorie"] == cat and found["farbe"] == color:
                    st.session_state.matches.append({
                        "found_item": found,
                        "lost_item": new_lost
                    })

            st.success("Suchmeldung gespeichert. Das System benachrichtigt dich bei Treffern!")
            st.session_state.current_screen = "menu"
            st.rerun()

    # -----------------------------------------------------
    # SCREEN 5: TREFFER / MATCHING & RÜCKGABE (Privacy by Design)
    # -----------------------------------------------------
    elif st.session_state.current_screen == "matches":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Möglicher Treffer!")
        
        if len(st.session_state.matches) == 0:
            st.info("Aktuell gibt es keine neuen Treffer für deine Suchmeldungen.")
        else:
            st.write("Passt dieses Fundstück zu deiner Suchmeldung?")
            
            for idx, match in enumerate(st.session_state.matches):
                item = match["found_item"]
                
                with st.container(border=True):
                    st.markdown(f"### 📦 {item['kategorie']}")
                    st.write(f"**Farbe:** {item['farbe']}")
                    st.write(f"**Fundort:** {item['ort']}")
                    st.write(f"**Zeit:** {item['zeit']}")
                    if item['hinweis']:
                        st.write(f"**Hinweise:** {item['hinweis']}")
                    
                    # DSGVO & Anonymisierte Rückgabe-Logik
                    st.info("📍 **Abholort:** Das Fundstück wurde im **SECRETARIAT / HAUSMEISTER** abgegeben (Schrank/Fach Nr. 4).")
                    
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        if st.button("Ja, das ist meins!", key=f"yes_{idx}", type="primary"):
                            item["status"] = "zurueckgegeben"
                            st.session_state.matches.pop(idx)
                            st.balloons()
                            st.success("Super! Bitte hole deinen Gegenstand beim Hausmeister/Sekretariat ab.")
                            st.rerun()
                    with col_m2:
                        if st.button("Nein, passt nicht", key=f"no_{idx}"):
                            st.session_state.matches.pop(idx)
                            st.rerun()

    # -----------------------------------------------------
    # SCREEN 6: ALLE FUNDSTÜCKE DURCHSUCHEN
    # -----------------------------------------------------
    elif st.session_state.current_screen == "list":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Fundstücke durchsuchen")
        
        filter_cat = st.selectbox("Filtern nach Kategorie", ["Alle"] + CATEGORIES)
        
        active_items = [i for i in st.session_state.found_items if i.get("status") != "zurueckgegeben"]
        
        if filter_cat != "Alle":
            active_items = [i for i in active_items if i["kategorie"] == filter_cat]

        if not active_items:
            st.info("Keine Fundstücke vorhanden.")
        else:
            for item in active_items:
                with st.container(border=True):
                    st.markdown(f"**{item['kategorie']}** ({item['farbe']})")
                    st.write(f"Ort: {item['ort']} | Datum: {item['zeit']}")
                    if item['hinweis']:
                        st.caption(f"Hinweis: {item['hinweis']}")
