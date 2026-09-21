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
        line-height: 1.7;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. SESSION STATE (DATENBANK-ERSATZ & ZUSTAND)
# =========================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Anonyme Sitzungs-ID statt Name/E-Mail (DSGVO / Privacy by Design)
if 'user_id' not in st.session_state:
    st.session_state.user_id = uuid.uuid4().hex[:8]

if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "menu"  # menu, found, lost, matches, list

# In-Memory Daten (später z. B. durch SQLite/PostgreSQL ersetzen)
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

# Kategorien und Orte für konsistente Eingaben
CATEGORIES = ["Trinkflasche", "Jacke/Kleidung", "Schlüssel", "Tasche/Rucksack",
              "Schulsachen", "Elektronik", "Sonstiges"]
COLORS = ["Blau", "Schwarz", "Rot", "Grün", "Gelb", "Weiß", "Grau", "Bunt"]
LOCATIONS = ["Sporthalle", "Pausenhof", "Mensa", "Flur EG", "Flur 1. OG",
              "Klassenzimmer", "Unbekannt"]

# =========================================================
# 3. KI: OPENAI CLIP ZERO-SHOT BILDERKENNUNG
# =========================================================
# CLIP vergleicht ein Foto mit Text-Beschreibungen und sagt, welche am
# besten passt ("zero-shot" = kein Training mit eigenen Fotos nötig).
# Wir prüfen 7 Kategorien x 8 Farben = 56 Beschreibungen pro Foto.

MODEL_NAME = "openai/clip-vit-base-patch32"

# Bei wenig Arbeitsspeicher (z. B. kleines Cloud-Hosting) auf True setzen:
# lädt das Modell in float16 (halber RAM-Bedarf, etwas langsamer).
# WICHTIG: Danach die App einmal komplett neu starten!
USE_FLOAT16 = False

# Prompts auf Englisch, da CLIP überwiegend englisch trainiert wurde
CATEGORY_TEMPLATES = {
    "Trinkflasche":    "a photo of a {farbe} water bottle or drinking bottle",
    "Jacke/Kleidung":  "a photo of a {farbe} jacket, hoodie or piece of clothing",
    "Schlüssel":       "a photo of a {farbe} key or keychain",
    "Tasche/Rucksack": "a photo of a {farbe} backpack, bag or purse",
    "Schulsachen":     "a photo of {farbe} school supplies like a book, notebook, pencil case or folder",
    "Elektronik":      "a photo of a {farbe} electronic device like a smartphone, headphones or calculator",
    "Sonstiges":       "a photo of a {farbe} everyday object",
}

COLOR_ADJECTIVES = {
    "Blau":    "blue",
    "Schwarz": "black",
    "Rot":     "red",
    "Grün":    "green",
    "Gelb":    "yellow",
    "Weiß":    "white",
    "Grau":    "gray",
    "Bunt":    "colorful multicolored",
}

# Untertypen -> Vorschlag für das "Hinweis"-Feld (weitere sichtbare Merkmale)
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
    "Schlüssel": [
        ("Einzelner Schlüssel", "a photo of a single key"),
        ("Schlüsselbund mit Anhänger", "a photo of a bunch of keys on a keyring with a keychain"),
    ],
    "Tasche/Rucksack": [
        ("Rucksack", "a photo of a backpack"),
        ("Turnbeutel", "a photo of a drawstring gym sack"),
        ("Handtasche / Schultertasche", "a photo of a handbag or shoulder bag"),
        ("Sporttasche", "a photo of a sports duffel bag"),
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
        ("Smartwatch / Uhr", "a photo of a smartwatch or wristwatch"),
        ("Tablet / Laptop", "a photo of a tablet or laptop"),
        ("Ladekabel / Ladegerät", "a photo of a charging cable or power adapter"),
    ],
    "Sonstiges": [
        ("Regenschirm", "a photo of an umbrella"),
        ("Brille", "a photo of eyeglasses or sunglasses"),
        ("Brotdose / Vesperbox", "a photo of a lunchbox"),
        ("Spielzeug", "a photo of a toy"),
        ("Sportgerät (z. B. Ball)", "a photo of sports equipment like a ball"),
        ("Anderer Gegenstand", "a photo of a single everyday object"),
    ],
}

# Alle 56 Prompts (Kategorie x Farbe) einmalig als Liste aufbauen.
# Reihenfolge ist wichtig: Index = Kategorie-Index * 8 + Farb-Index
ALL_PROMPTS = [
    CATEGORY_TEMPLATES[cat].format(farbe=COLOR_ADJECTIVES[col])
    for cat in CATEGORIES
    for col in COLORS
]


@st.cache_resource
def load_clip_model():
    """Lädt das OpenAI CLIP-Modell (über Hugging Face Transformers).
    Dank @st.cache_resource passiert das nur EINMAL pro App-Start."""
    import torch
    from transformers import CLIPModel, CLIPProcessor
    dtype = torch.float16 if USE_FLOAT16 else torch.float32
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model = CLIPModel.from_pretrained(MODEL_NAME, torch_dtype=dtype)
    model.eval()
    return model, processor


@st.cache_resource
def get_clip_text_features():
    """Berechnet die Text-Vektoren aller 56 Beschreibungen einmalig."""
    import torch
    model, processor = load_clip_model()
    inputs = processor(text=ALL_PROMPTS, return_tensors="pt",
                       padding=True, truncation=True)
    with torch.no_grad():
        feats = model.get_text_features(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
        )
        feats = feats / feats.norm(dim=-1, keepdim=True)
    return feats


def _detect_subtype(image_features, kategorie):
    """Erkennt feinere Merkmale innerhalb der Kategorie (z. B. Hoodie vs. Jacke)."""
    import torch
    subtypes = SUBTYPE_PROMPTS.get(kategorie, [])
    if not subtypes:
        return None, 0.0
    labels = [label for label, _ in subtypes]
    prompts = [prompt for _, prompt in subtypes]

    model, processor = load_clip_model()
    inputs = processor(text=prompts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = model.get_text_features(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
        )
       
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        similarity = (image_features @ text_features.T).squeeze(0)
        probs = similarity.float().softmax(dim=0)
    best = int(probs.argmax())
    return labels[best], float(probs[best])


def _clip_analyze(image):
    """Reine CLIP-Berechnung ohne Streamlit-Aufrufe (cache-freundlich)."""
    import torch
    model, processor = load_clip_model()
    text_features = get_clip_text_features()

    # Handy-Fotos: Ausrichtung laut EXIF korrigieren, in RGB umwandeln
    image = ImageOps.exif_transpose(image)
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = processor(images=image, return_tensors="pt")
    pixel_values = inputs["pixel_values"]
    if USE_FLOAT16:
        pixel_values = pixel_values.half()

    with torch.no_grad():
        # Bild-Vektor berechnen
        image_features = model.get_image_features(pixel_values=pixel_values)
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        # Ähnlichkeit Foto <-> alle 56 Beschreibungen -> Wahrscheinlichkeiten
        similarity = (image_features @ text_features.T).squeeze(0)
        probs = similarity.float().softmax(dim=0).cpu().numpy()

    # 56 Wahrscheinlichkeiten als Tabelle anordnen: 7 Kategorien x 8 Farben
    matrix = probs.reshape(len(CATEGORIES), len(COLORS))

    # Kategorie = Summe über alle Farbkombinationen
    cat_probs = matrix.sum(axis=1)
    cat_idx = int(cat_probs.argmax())

    # Farbe = beste Farbe INNERHALB der erkannten Kategorie
    color_probs = matrix[cat_idx]
    color_idx = int(color_probs.argmax())

    # Top-3 Kategorien als Korrektur-Vorschläge
    top3_idx = sorted(range(len(CATEGORIES)), key=lambda i: -cat_probs[i])[:3]

    result = {
        "kategorie": CATEGORIES[cat_idx],
        "farbe": COLORS[color_idx],
        "conf_kategorie": float(cat_probs[cat_idx]),
        "conf_farbe": float(color_probs[color_idx]),
        "alternativen": [
            {"kategorie": CATEGORIES[i], "confidence": float(cat_probs[i])}
            for i in top3_idx if i != cat_idx
    
    # Untertyp bestimmen (z. B. "Hoodie" bei "Jacke/Kleidung")
    merkmal, merkmal_conf = _detect_subtype(image_features, result["kategorie"])
    if merkmal:
        result["merkmal"] = merkmal
        result["conf_merkmal"] = merkmal_conf

    return result


@st.cache_data(show_spinner=False)
def analyze_image_with_ai(file_bytes):
    """Öffentliche Funktion für die UI: erhält die rohen Bild-Bytes und
    cached das Ergebnis pro Foto (damit bei Streamlit-Reruns nicht neu
    gerechnet werden muss)."""
    import io
    image = Image.open(io.BytesIO(file_bytes))
    return _clip_analyze(image)


# =========================================================
# 4. MATCHING-SYSTEM (AUTOMATISCHER ABGLEICH)
# =========================================================
def auto_abgleich(new_item, ist_fundstueck):
    """
    Vergleicht einen neuen Eintrag mit allen bestehenden
