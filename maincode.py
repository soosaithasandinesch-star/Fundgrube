import streamlit as st
import datetime
import uuid
from PIL import Image, ImageOps

# =========================================================
# 1. KONFIGURATION & STYLING (UI)
# =========================================================
st.set_page_config(
    page_title="Schul-Fundbüro",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS für die Smartphone-Karten-Optik
# Custom CSS für die Smartphone-Karten-Optik
st.markdown("""
    <style>
    /* ===== GRUNDREGEL: helle Fläche -> schwarze Schrift ===== */
    .stApp {
        background-color: #f4f8fb;
        color: #000000;
    }
    .block-container {
        max-width: 450px;
        background-color: #ffffff;
        padding: 30px 20px;
        margin-top: 20px;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e1e8ed;
        color: #000000;
    }
    .main-title {
        text-align: center;
        font-weight: 800;
        font-size: 24px;
        color: #000000;
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        font-size: 14px;
        color: #000000;
        margin-bottom: 25px;
    }

    /* Alle Texte auf hellen Hintergründen: schwarz und gut lesbar */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp p, .stApp li, .stApp label, .stApp strong, .stApp em,
    .stApp th, .stApp td, .stApp small, .stApp blockquote,
    .stApp figcaption, .stApp a {
        color: #000000;
    }
    /* Auch Captions/Untertitel dunkel statt hellgrau */
    .stApp [data-testid="stCaptionContainer"],
    .stApp [data-testid="stCaptionContainer"] p,
    .stApp [data-testid="stCaption"] {
        color: #000000;
    }
    /* Info-/Erfolgs-/Fehler-Boxen: helle Hintergründe -> schwarze Schrift */
    .stApp [data-testid="stAlert"],
    .stApp [data-testid="stNotification"],
    .stApp [data-testid="stAlert"] p,
    .stApp [data-testid="stAlert"] span,
    .stApp [data-testid="stAlert"] strong,
    .stApp [data-testid="stNotification"] p,
    .stApp [data-testid="stNotification"] span,
    .stApp [data-testid="stNotification"] strong {
        color: #000000;
    }

    /* ===== BUTTONS: ganze Wörter sichtbar, nichts abgeschnitten ===== */
    div.stButton > button {
        width: 100%;
        box-sizing: border-box;
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 700;
        line-height: 1.5;
        min-height: 48px;
        white-space: pre-line;          /* Zeilenumbrüche (\n) anzeigen */
        overflow-wrap: break-word;      /* lange Wörter umbrechen statt abschneiden */
        word-break: break-word;
        color: #000000;                 /* normale Buttons: schwarze Schrift */
    }
    /* Auch der innere Text-Container des Buttons */
    div.stButton > button p,
    div.stButton > button span {
        white-space: pre-line !important;
        overflow-wrap: break-word;
        word-break: break-word;
        color: inherit;
    }

    /* ===== DUNKLE FLÄCHEN -> WEISSE Schrift ===== */
    /* Rote Primär-Buttons: dunkelroter Hintergrund + weiße fette Schrift */
    .stApp button[kind="primary"],
    .stApp button[data-testid="baseButton-primary"],
    .stApp button[data-testid="stBaseButton-primary"],
    .stApp button[data-testid="stFormSubmitButton"] {
        background-color: #b02a2a !important;
        border: 1px solid #8f2020 !important;
        color: #ffffff !important;
        font-weight: 700;
    }
    .stApp button[kind="primary"] p,
    .stApp button[kind="primary"] span,
    .stApp button[data-testid="baseButton-primary"] p,
    .stApp button[data-testid="baseButton-primary"] span,
    .stApp button[data-testid="stBaseButton-primary"] p,
    .stApp button[data-testid="stBaseButton-primary"] span {
        color: #ffffff !important;
    }

    /* KI-Box: heller blauer Hintergrund -> schwarze Schrift */
    .ki-box {
        background-color: #eef6ff;
        border: 1px dashed #2b78e4;
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        color: #000000;
        font-size: 13px;
        margin: 10px 0;
        line-height: 1.7;
    }
    .ki-box b { color: #000000; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. SESSION STATE (DATENBANK-ERSATZ & ZUSTAND)
# =========================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user_id' not in st.session_state:
    st.session_state.user_id = uuid.uuid4().hex[:8]

if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "menu"

if 'found_items' not in st.session_state:
    st.session_state.found_items = []
if 'lost_items' not in st.session_state:
    st.session_state.lost_items = []
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'flash' not in st.session_state:
    st.session_state.flash = None
if 'clip_ready' not in st.session_state:
    st.session_state.clip_ready = False

# ------------------ KATEGORIEN & ORTE ------------------
CATEGORIES = [
    "Trinkflasche",
    "Jacke/Kleidung",
    "Tasche/Rucksack",
    "Schlüssel",
    "Schulsachen",
    "Elektronik",
    "Brille",
    "Geldbörse/Portemonnaie",
    "Schmuck",
    "Brotdose/Vesperbox",
    "Regenschirm",
    "Sportgerät",
    "Musikinstrument",
    "Sonstiges",
]
COLORS = ["Blau", "Schwarz", "Rot", "Grün", "Gelb", "Weiß", "Grau", "Bunt"]
LOCATIONS = ["Sporthalle", "Pausenhof", "Mensa", "Aula", "Bibliothek/Mediothek",
             "Flur EG", "Flur 1. OG", "Treppenhaus", "Toiletten/Umkleide",
             "Klassenzimmer", "Schulgelände (außen)", "Unbekannt"]

# =========================================================
# 3. KI: OPENAI CLIP ZERO-SHOT BILDERKENNUNG
# =========================================================
MODEL_NAME = "openai/clip-vit-base-patch32"
USE_FLOAT16 = False  # Bei wenig RAM auf True setzen + App neu starten

CATEGORY_TEMPLATES = {
    "Trinkflasche":           "a photo of a {farbe} water bottle or drinking bottle",
    "Jacke/Kleidung":         "a photo of a {farbe} jacket, hoodie or piece of clothing",
    "Tasche/Rucksack":        "a photo of a {farbe} backpack, bag or purse",
    "Schlüssel":              "a photo of a {farbe} key or keychain",
    "Schulsachen":            "a photo of {farbe} school supplies like a book, notebook, pencil case or folder",
    "Elektronik":             "a photo of a {farbe} electronic device like a smartphone, headphones or calculator",
    "Brille":                 "a photo of {farbe} eyeglasses or sunglasses",
    "Geldbörse/Portemonnaie": "a photo of a {farbe} wallet or purse",
    "Schmuck":                "a photo of {farbe} jewelry like a ring, necklace or bracelet",
    "Brotdose/Vesperbox":     "a photo of a {farbe} lunchbox or food container",
    "Regenschirm":            "a photo of a {farbe} umbrella",
    "Sportgerät":             "a photo of {farbe} sports equipment like a ball or racket",
    "Musikinstrument":        "a photo of a {farbe} musical instrument like a recorder flute or instrument case",
    "Sonstiges":              "a photo of a {farbe} everyday object",
}

COLOR_ADJECTIVES = {
    "Blau": "blue", "Schwarz": "black", "Rot": "red", "Grün": "green",
    "Gelb": "yellow", "Weiß": "white", "Grau": "gray",
    "Bunt": "colorful multicolored",
}

SUBTYPE_PROMPTS = {
    "Trinkflasche": [
        ("Kunststoffflasche", "a photo of a plastic water bottle"),
        ("Metall-/Thermosflasche", "a photo of a metal thermos flask or insulated bottle"),
        ("Glasflasche", "a photo of a glass bottle"),
    ],
    "Jacke/Kleidung": [
        ("Jacke / Winterjacke", "a photo of a jacket or winter coat"),
        ("Hoodie / Kapuzenpullover", "a photo of a hoodie"),
        ("Pullover / Sweatshirt", "a photo of a sweater or sweatshirt"),
        ("Mütze / Hut", "a photo of a cap, beanie or hat"),
        ("Schal / Handschuhe", "a photo of a scarf or gloves"),
        ("Sportsachen", "a photo of sports clothing"),
    ],
    "Tasche/Rucksack": [
        ("Rucksack", "a photo of a backpack"),
        ("Turnbeutel", "a photo of a drawstring gym sack"),
        ("Handtasche / Schultertasche", "a photo of a handbag or shoulder bag"),
        ("Sporttasche", "a photo of a sports duffel bag"),
    ],
    "Schlüssel": [
        ("Einzelner Schlüssel", "a photo of a single key"),
        ("Schlüsselbund mit Anhänger", "a photo of a bunch of keys on a keyring with a keychain"),
    ],
    "Schulsachen": [
        ("Buch", "a photo of a book"),
        ("Heft / Notizbuch", "a photo of a notebook or exercise book"),
        ("Federmäppchen", "a photo of a pencil case"),
        ("Ordner / Mappe", "a photo of a folder or binder"),
        ("Stift", "a photo of a pen or pencil"),
    ],
    "Elektronik": [
        ("Smartphone / Handy", "a photo of a smartphone"),
        ("Kopfhörer / Earbuds", "a photo of headphones or earbuds"),
        ("Taschenrechner", "a photo of a pocket calculator"),
        ("Tablet / Laptop", "a photo of a tablet or laptop"),
        ("Ladekabel / Ladegerät", "a photo of a charging cable or power adapter"),
    ],
    "Brille": [
        ("Korrekturbrille", "a photo of prescription eyeglasses"),
        ("Sonnenbrille", "a photo of sunglasses"),
        ("Brillen-Etui", "a photo of a glasses case"),
    ],
    "Geldbörse/Portemonnaie": [
        ("Geldbörse", "a photo of a wallet"),
        ("Kleingeld-Etui", "a photo of a small coin purse"),
    ],
    "Schmuck": [
        ("Halskette / Kette", "a photo of a necklace"),
        ("Armband", "a photo of a bracelet"),
        ("Ring", "a photo of a ring"),
        ("Ohrringe", "a photo of earrings"),
        ("Uhr", "a photo of a wristwatch"),
    ],
    "Brotdose/Vesperbox": [
        ("Brotdose", "a photo of a lunchbox"),
        ("Trinkbecher", "a photo of a drinking cup or tumbler"),
    ],
    "Regenschirm": [
        ("Regenschirm", "a photo of an umbrella"),
    ],
    "Sportgerät": [
        ("Ball", "a photo of a ball"),
        ("Schläger", "a photo of a racket"),
        ("Springseil", "a photo of a skipping rope"),
    ],
    "Musikinstrument": [
        ("Blockflöte", "a photo of a recorder flute"),
        ("Instrumentenetui", "a photo of an instrument case"),
        ("Noten / Notenmappe", "a photo of sheet music"),
    ],
    "Sonstiges": [
        ("Spielzeug", "a photo of a toy"),
        ("Anderer Gegenstand", "a photo of a single everyday object"),
    ],
}

ALL_PROMPTS = [
    CATEGORY_TEMPLATES[cat].format(farbe=COLOR_ADJECTIVES[col])
    for cat in CATEGORIES
    for col in COLORS
]


@st.cache_resource
def load_clip_model():
    """Lädt das OpenAI CLIP-Modell (nur einmal pro App-Start)."""
    import torch
    from transformers import CLIPModel, CLIPProcessor
    dtype = torch.float16 if USE_FLOAT16 else torch.float32
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model = CLIPModel.from_pretrained(MODEL_NAME, torch_dtype=dtype)
    model.eval()
    return model, processor


def _as_tensor(output):
    """NEUER FIX: Neuere transformers-Versionen (v5+) geben statt einem
    Tensor ein 'BaseModelOutputWithPooling'-Objekt zurück. Diese Funktion
    holt den echten Tensor daraus heraus (kompatibel mit alt + neu)."""
    import torch
    if isinstance(output, torch.Tensor):
        return output  # alte Version: direkt ein Tensor
    for attr in ("pooler_output", "image_embeds", "text_embeds", "last_hidden_state"):
        val = getattr(output, attr, None)
        if val is not None:
            return val  # neue Version: Tensor steckt hier drin
    raise TypeError(f"Unerwarteter KI-Output-Typ: {type(output)}")


@st.cache_resource
def get_clip_text_features():
    """Text-Vektoren aller Beschreibungen einmalig berechnen."""
    import torch
    model, processor = load_clip_model()
    inputs = processor(text=ALL_PROMPTS, return_tensors="pt",
                       padding=True, truncation=True)
    with torch.no_grad():
        feats = _as_tensor(model.get_text_features(          # FIX: _as_tensor
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
        ))
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats


def _detect_subtype(image_features, kategorie):
    """Erkennt feinere Merkmale (z. B. Hoodie vs. Jacke)."""
    import torch
    subtypes = SUBTYPE_PROMPTS.get(kategorie, [])
    if not subtypes:
        return None, 0.0
    labels = [label for label, _ in subtypes]
    prompts = [prompt for _, prompt in subtypes]

    model, processor = load_clip_model()
    inputs = processor(text=prompts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = _as_tensor(model.get_text_features(   # FIX: _as_tensor
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
        ))
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        similarity = (image_features @ text_features.T).squeeze(0)
        probs = similarity.float().softmax(dim=0)
    best = int(probs.argmax())
    return labels[best], float(probs[best])


def _clip_analyze(image):
    """Reine CLIP-Berechnung ohne Streamlit-Aufrufe."""
    import torch
    model, processor = load_clip_model()
    text_features = get_clip_text_features()

    image = ImageOps.exif_transpose(image)
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    pixel_values = inputs["pixel_values"]
    if USE_FLOAT16:
        pixel_values = pixel_values.half()

    with torch.no_grad():
        image_features = _as_tensor(                          # FIX: _as_tensor
            model.get_image_features(pixel_values=pixel_values)
        )
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        similarity = (image_features @ text_features.T).squeeze(0)
        probs = similarity.float().softmax(dim=0).cpu().numpy()

    matrix = probs.reshape(len(CATEGORIES), len(COLORS))
    cat_probs = matrix.sum(axis=1)
    cat_idx = int(cat_probs.argmax())
    color_probs = matrix[cat_idx]
    color_idx = int(color_probs.argmax())
    top3_idx = sorted(range(len(CATEGORIES)), key=lambda i: -cat_probs[i])[:3]

    result = {
        "kategorie": CATEGORIES[cat_idx],
        "farbe": COLORS[color_idx],
        "conf_kategorie": float(cat_probs[cat_idx]),
        "conf_farbe": float(color_probs[color_idx]),
        "alternativen": [
            {"kategorie": CATEGORIES[i], "confidence": float(cat_probs[i])}
            for i in top3_idx if i != cat_idx
        ],
    }
    merkmal, merkmal_conf = _detect_subtype(image_features, result["kategorie"])
    if merkmal:
        result["merkmal"] = merkmal
        result["conf_merkmal"] = merkmal_conf
    return result


@st.cache_data(show_spinner=False)
def analyze_image_with_ai(file_bytes):
    """Öffentliche Funktion: wird von Screen 3 (Foto-Upload) aufgerufen."""
    import io
    image = Image.open(io.BytesIO(file_bytes))
    return _clip_analyze(image)

# =========================================================
# 4. MATCHING-SYSTEM (AUTOMATISCHER ABGLEICH)
# =========================================================
def auto_abgleich(new_item, ist_fundstueck):
    """Vergleicht einen neuen Eintrag mit allen Gegenstücken.
    Treffer = gleiche Kategorie UND gleiche Farbe."""
    if ist_fundstueck:
        kandidaten = [l for l in st.session_state.lost_items
                      if l.get("status") != "zurueckgegeben"]
    else:
        kandidaten = [f for f in st.session_state.found_items
                      if f.get("status") != "zurueckgegeben"]

    treffer = 0
    for anderer in kandidaten:
        if (anderer["kategorie"] == new_item["kategorie"]
                and anderer["farbe"] == new_item["farbe"]):
            if ist_fundstueck:
                st.session_state.matches.append({"found_item": new_item,
                                                 "lost_item": anderer})
            else:
                st.session_state.matches.append({"found_item": anderer,
                                                 "lost_item": new_item})
            treffer += 1
    return treffer


# =========================================================
# SCREEN 1: LOGIN (Zugangscode "BigD")
# =========================================================
if not st.session_state.logged_in:
    st.markdown("<div style='font-size: 60px; text-align: center;'>📦</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='main-title'>Willkommen im<br>Schul-Fundbüro</div>",
                unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Bitte gib den Zugangscode deiner Schule ein:</div>",
                unsafe_allow_html=True)

    code_input = st.text_input("Zugangscode", type="password",
                               placeholder="Zugangscode eingeben",
                               label_visibility="collapsed")

    if st.button("App Starten", type="primary"):
        if code_input == "BigD":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Falscher Zugangscode! (Hinweis: Passwort ist 'BigD')")

# =========================================================
# ANGEMELDETER BEREICH (HAUPT-APP)
# =========================================================
else:
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.caption("🏫 Schul-Fundbüro")
    with col_head2:
        if st.button("Abmelden", key="logout"):
            st.session_state.logged_in = False
            st.rerun()

    # -----------------------------------------------------
    # SCREEN 2: HAUPTMENÜ
    # -----------------------------------------------------
    if st.session_state.current_screen == "menu":
        if st.session_state.flash:
            st.success(st.session_state.flash)
            st.session_state.flash = None

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
            meine_matches = [m for m in st.session_state.matches
                             if m["lost_item"].get("owner") == st.session_state.user_id]
            badge = f" ({len(meine_matches)})" if meine_matches else ""
            if st.button(f"🔔\n\nMeine Meldungen\n& Treffer{badge}", use_container_width=True):
                st.session_state.current_screen = "matches"
                st.rerun()

        st.divider()
        with st.expander("🔒 Datenschutz & Daten"):
            st.caption("Alle Daten liegen nur temporär im Arbeitsspeicher dieser Sitzung "
                       "und werden nicht dauerhaft gespeichert. Fotos werden als kleine "
                       "Vorschaubilder gespeichert und beim Löschen/Abmelden bzw. beim "
                       "Schließen der App entfernt. Es werden keine Namen oder Kontakte "
                       "gesammelt – die Rückgabe läuft anonym über das Sekretariat.")
            if st.button("🗑️ Alle Daten dieser Sitzung löschen"):
                st.session_state.found_items = []
                st.session_state.lost_items = []
                st.session_state.matches = []
                st.session_state.flash = "🗑️ Alle Daten wurden gelöscht."
                st.rerun()

    # -----------------------------------------------------
    # SCREEN 3: FUNDSTÜCK ERFASSEN
    # -----------------------------------------------------
    elif st.session_state.current_screen == "found":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Fundstück melden")
        st.write("### 1. Foto machen oder hochladen")
        st.caption("🔒 Datenschutz: Bitte nur den Gegenstand fotografieren – keine Personen!")

        quelle = st.radio("Foto-Quelle",
                          ["📷 Mit der Kamera aufnehmen", "📁 Foto hochladen"],
                          horizontal=True, label_visibility="collapsed")

        uploaded_file = None
        if quelle.startswith("📷"):
            uploaded_file = st.camera_input("Foto aufnehmen", label_visibility="collapsed")
        else:
            uploaded_file = st.file_uploader("Foto auswählen",
                                             type=["jpg", "jpeg", "png"],
                                             label_visibility="collapsed")

        detected_category = CATEGORIES[0]
        detected_color = COLORS[0]
        ai_results = None
        merkmal_vorschlag = ""

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Foto zur Kontrolle", width=320)

            if not st.session_state.clip_ready:
                st.info("ℹ️ Die KI wird beim ersten Mal initialisiert (einmaliger Download "
                        "des CLIP-Modells, ca. 600 MB) – das dauert einige Minuten. "
                        "Danach geht es schnell.")

            try:
                with st.spinner("🤖 KI analysiert das Foto (CLIP Zero-Shot)..."):
                    ai_results = analyze_image_with_ai(uploaded_file.getvalue())
                st.session_state.clip_ready = True
            except Exception as e:
                ai_results = None
                st.warning(f"⚠️ KI-Analyse gerade nicht möglich ({e}). "
                           "Bitte Kategorie und Farbe selbst auswählen.")

            if ai_results is not None:
                detected_category = ai_results["kategorie"]
                detected_color = ai_results["farbe"]
                merkmal_vorschlag = ai_results.get("merkmal", "")

                alternativen = " | ".join(
                    f"{a['kategorie']} ({a['confidence']:.0%})"
                    for a in ai_results.get("alternativen", [])[:2]
                )

                st.markdown(f"""
                    <div class="ki-box">
                        🤖 <b>KI-Erkennung (OpenAI CLIP, Zero-Shot)</b><br>
                        Kategorie: <b>{detected_category}</b> – {ai_results['conf_kategorie']:.0%} sicher<br>
                        Farbe: <b>{detected_color}</b> – {ai_results['conf_farbe']:.0%} sicher<br>
                        Merkmal: <b>{merkmal_vorschlag or '–'}</b>
                    </div>
                """, unsafe_allow_html=True)

                if ai_results["conf_kategorie"] < 0.30:
                    st.caption("🤔 Die KI ist sich nicht ganz sicher – "
                               "bitte prüfen und ggf. korrigieren!")
                elif alternativen:
                    st.caption(f"KI-Alternativen: {alternativen} – gerne korrigieren.")

        st.write("### 2. Daten überprüfen & anpassen:")

        cat_idx = CATEGORIES.index(detected_category) if detected_category in CATEGORIES else 0
        col_idx = COLORS.index(detected_color) if detected_color in COLORS else 0

        cat = st.selectbox("* Kategorie", CATEGORIES, index=cat_idx)
        color = st.selectbox("* Hauptfarbe", COLORS, index=col_idx)
        loc = st.selectbox("* Fundort", LOCATIONS)
        time_found = st.text_input(
            "* Datum/Zeit",
            value=f"Heute, ca. {datetime.datetime.now().strftime('%H:%M')} Uhr")
        note = st.text_input("Hinweis", value=merkmal_vorschlag,
                             placeholder="z. B. Schwarzer Deckel, Kratzer am Boden")

        if st.button("Fundstück Speichern", type="primary"):
            foto_thumb = None
            if uploaded_file is not None:
                foto_thumb = ImageOps.exif_transpose(image).copy()
                foto_thumb.thumbnail((320, 320))

            new_item = {
                "id": max([i["id"] for i in st.session_state.found_items], default=0) + 1,
                "kategorie": cat,
                "farbe": color,
                "ort": loc,
                "zeit": time_found,
                "hinweis": note,
                "merkmal": merkmal_vorschlag,
                "foto": foto_thumb,
                "status": "im_fundbuero"
            }
            st.session_state.found_items.append(new_item)

            anzahl_treffer = auto_abgleich(new_item, ist_fundstueck=True)

            if anzahl_treffer > 0:
                st.session_state.flash = (f"✅ Fundstück gespeichert! 🔔 {anzahl_treffer} "
                                          "mögliche(r) Treffer gefunden – siehe 'Meine "
                                          "Meldungen & Treffer'!")
            else:
                st.session_state.flash = "✅ Fundstück erfolgreich gespeichert!"

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
        time_lost = st.selectbox("* Wann ungefähr?",
                                 ["Heute", "Gestern", "Diese Woche", "Vor längerer Zeit"])
        details = st.text_area(
            "Details",
            placeholder="Beschreibe den Gegenstand möglichst genau (z. B. Aufdruck, Marke, Beschädigung)...")

        st.write("**Benachrichtigung:**")
        notify = st.radio("Benachrichtigung", ["Nur in der App", "Per E-Mail"],
                          label_visibility="collapsed")
        email = ""
        if notify == "Per E-Mail":
            email = st.text_input("E-Mail-Adresse",
                                  placeholder="Nur für die Treffer-Benachrichtigung")
            st.caption("🔒 Deine Adresse wird nicht öffentlich angezeigt (Privacy by Design).")

        if st.button("Suchmeldung aufgeben", type="primary"):
            if notify == "Per E-Mail" and not email.strip():
                st.error("Bitte gib eine E-Mail-Adresse ein oder wähle 'Nur in der App'.")
            else:
                new_lost = {
                    "id": max([i["id"] for i in st.session_state.lost_items], default=0) + 1,
                    "kategorie": cat,
                    "farbe": color,
                    "ort": loc,
                    "zeit": time_lost,
                    "details": details,
                    "owner": st.session_state.user_id,
                    "benachrichtigung": notify,
                    "status": "aktiv"
                }
                st.session_state.lost_items.append(new_lost)

                anzahl = auto_abgleich(new_lost, ist_fundstueck=False)

                if anzahl > 0:
                    st.session_state.flash = (f"✅ Suchmeldung gespeichert! 🔔 {anzahl} "
                                              "passendes Fundstück(e) gefunden – "
                                              "siehe Benachrichtigungen!")
                else:
                    st.session_state.flash = ("✅ Suchmeldung gespeichert. Wir benachrichtigen "
                                              "dich, sobald ein passendes Fundstück gemeldet wird!")

                st.session_state.current_screen = "menu"
                st.rerun()

    # -----------------------------------------------------
    # SCREEN 5: MEINE MELDUNGEN, BENACHRICHTIGUNGEN & TREFFER
    # -----------------------------------------------------
    elif st.session_state.current_screen == "matches":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Meine Meldungen & Treffer")

        st.subheader("📋 Meine Suchmeldungen")
        meine_meldungen = [l for l in st.session_state.lost_items
                           if l.get("owner") == st.session_state.user_id]
        if not meine_meldungen:
            st.info("Du hast noch keine Verlustmeldung erstellt.")
        else:
            for lost in meine_meldungen:
                status = ("✅ zurückgegeben" if lost.get("status") == "zurueckgegeben"
                          else "🔍 aktiv")
                with st.container(border=True):
                    st.markdown(f"**{lost['kategorie']}** ({lost['farbe']}) – {status}")
                    st.caption(f"Verlustort: {lost['ort']} | {lost['zeit']}")
                    if lost.get("details"):
                        st.caption(f"Details: {lost['details']}")

        st.divider()

        st.subheader("🔔 Benachrichtigungen")
        meine_matches = [m for m in st.session_state.matches
                         if m["lost_item"].get("owner") == st.session_state.user_id]

        if not meine_matches:
            st.info("Aktuell gibt es keine neuen Treffer für deine Suchmeldungen.")
        else:
            st.write("Passt dieses Fundstück zu deiner Suchmeldung?")
            for match in meine_matches:
                item = match["found_item"]
                with st.container(border=True):
                    if item.get("foto") is not None:
                        st.image(item["foto"], width=200)
                    st.markdown(f"### 📦 {item['kategorie']}")
                    st.write(f"**Farbe:** {item['farbe']}")
                    if item.get("merkmal"):
                        st.write(f"**Merkmal:** {item['merkmal']}")
                    st.write(f"**Fundort:** {item['ort']}")
                    st.write(f"**Zeit:** {item['zeit']}")
                    if item.get("hinweis"):
                        st.write(f"**Hinweise:** {item['hinweis']}")

                    st.info("📍 **Abholort:** Das Fundstück wurde im **SEKRETARIAT / beim "
                            "HAUSMEISTER** abgegeben (Schrank/Fach Nr. 4).")

                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        if st.button("Ja, das ist meins!",
                                     key=f"yes_{item['id']}_{match['lost_item']['id']}",
                                     type="primary"):
                            match["found_item"]["status"] = "zurueckgegeben"
                            match["lost_item"]["status"] = "zurueckgegeben"
                            st.session_state.matches = [
                                m for m in st.session_state.matches
                                if m["lost_item"] is not match["lost_item"]
                            ]
                            st.balloons()
                            st.session_state.flash = ("🎉 Super! Bitte hole deinen Gegenstand "
                                                      "beim Hausmeister/Sekretariat ab "
                                                      "(Schrank/Fach Nr. 4).")
                            st.rerun()
                    with col_m2:
                        if st.button("Nein, passt nicht",
                                     key=f"no_{item['id']}_{match['lost_item']['id']}"):
                            st.session_state.matches = [
                                m for m in st.session_state.matches if m is not match
                            ]
                            st.rerun()

    # -----------------------------------------------------
    # SCREEN 6: FUNDSTÜCKE DURCHSUCHEN
    # -----------------------------------------------------
    elif st.session_state.current_screen == "list":
        if st.button("← Zurück zum Hauptmenü"):
            st.session_state.current_screen = "menu"
            st.rerun()

        st.title("Fundstücke durchsuchen")

        active_items = [i for i in st.session_state.found_items
                        if i.get("status") != "zurueckgegeben"]

        f1, f2 = st.columns(2)
        with f1:
            filter_cat = st.selectbox("Kategorie", ["Alle"] + CATEGORIES)
            filter_color = st.selectbox("Farbe", ["Alle"] + COLORS)
        with f2:
            filter_loc = st.selectbox("Ort", ["Alle"] + LOCATIONS)
            suchtext = st.text_input("Beschreibung",
                                     placeholder="z. B. Deckel, Kratzer, Heute ...")

        gefiltert = active_items
        if filter_cat != "Alle":
            gefiltert = [i for i in gefiltert if i["kategorie"] == filter_cat]
        if filter_color != "Alle":
            gefiltert = [i for i in gefiltert if i["farbe"] == filter_color]
        if filter_loc != "Alle":
            gefiltert = [i for i in gefiltert if i["ort"] == filter_loc]
        if suchtext:
            q = suchtext.lower()
            gefiltert = [
                i for i in gefiltert
                if q in i["kategorie"].lower()
                or q in (i.get("hinweis") or "").lower()
                or q in (i.get("merkmal") or "").lower()
                or q in i["zeit"].lower()
            ]

        if not gefiltert:
            st.info("Keine Fundstücke gefunden, die zu deiner Suche passen.")
        else:
            st.caption(f"{len(gefiltert)} Fundstück(e) – Fotos werden nur temporär in "
                       "dieser Sitzung gespeichert (DSGVO).")
            for item in gefiltert:
                with st.container(border=True):
                    if item.get("foto") is not None:
                        st.image(item["foto"], width=180)
                    st.markdown(f"**{item['kategorie']}** ({item['farbe']})")
                    if item.get("merkmal"):
                        st.caption(f"Merkmal: {item['merkmal']}")
                    st.write(f"Ort: {item['ort']} | Datum: {item['zeit']}")
                    if item.get("hinweis"):
                        st.caption(f"Hinweis: {item['hinweis']}")
