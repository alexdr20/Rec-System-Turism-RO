import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import joblib

# =========================
# Page config
# =========================
st.set_page_config(page_title="Recomandare Turistică", layout="centered")

# =========================
# i18n / Localization
# =========================
LANG = {
    "RO": {
        "app_title": "🏝️ Recomandare Turistică Inteligentă",
        "app_desc": "Completează preferințele pentru a primi o sugestie de stațiune din România.",
        "lang_label": "🌐 Alege limba / Choose language",
        "reset": "🔄 Resetare filtre",
        "sezon_label": "🗓️ Sezonul preferat:",
        "sezon_opts": {"rece": "rece", "cald": "cald", "tot": "tot"},
        "traveler_label": "👤 Tipul de călător:",
        "traveler_opts": {"cuplu": "cuplu", "familie": "familie", "solo": "solo", "grup": "grup"},
        "activity_label": "🎯 Activitatea principală:",
        "activity_opts": {"plaja": "plajă", "partie": "pârtie", "trasee": "trasee", "tratament": "tratament"},
        "info_label": "ℹ️ Centru Info Turistic:",
        "cult_label": "🎭 Activități culturale:",
        "alim_label": "🍽️ Facilități alimentație:",
        "tri_opts": {"nu": "nu", "da": "da", "nu conteaza": "nu contează"},
        "budget_label": "💰 Buget disponibil:",
        "budget_opts": {"scazut": "scăzut", "ridicat": "ridicat"},
        "nights_label": "🛌 Număr de nopți:",
        "find_btn": "🔍 Găsește stațiunea ideală",
        "no_result": "❌ Nicio stațiune nu corespunde criteriilor selectate.",
        "prefs_title": "### 🔎 Preferințele selectate:",
        "pref_sezon": "Sezon",
        "pref_trav": "Tip călător",
        "pref_budget": "Buget",
        "pref_nights": "Număr nopți",
        "pref_info": "Centru Info",
        "pref_cult": "Cultură",
        "pref_alim": "Alimentație",
        "recom": "🏖️ Recomandare: **{st}** ({jd}) – Activitate: _{act}_",
        "img_missing": "⚠️ Nu există imagine locală pentru această stațiune.",
        "img_error": "⚠️ Eroare la încărcarea imaginii: {e}",
    },
    "EN": {
        "app_title": "🏝️ Smart Tourism Recommendation",
        "app_desc": "Fill in your preferences to get a suggested Romanian resort.",
        "lang_label": "🌐 Choose language / Alege limba",
        "reset": "🔄 Reset filters",
        "sezon_label": "🗓️ Preferred season:",
        "sezon_opts": {"rece": "cold", "cald": "warm", "tot": "year-round"},
        "traveler_label": "👤 Traveler type:",
        "traveler_opts": {"cuplu": "couple", "familie": "family", "solo": "solo", "grup": "group"},
        "activity_label": "🎯 Main activity:",
        "activity_opts": {"plaja": "beach", "partie": "ski slope", "trasee": "trails", "tratament": "spa/therapy"},
        "info_label": "ℹ️ Tourist Info Center:",
        "cult_label": "🎭 Cultural activities:",
        "alim_label": "🍽️ Food facilities:",
        "tri_opts": {"nu": "no", "da": "yes", "nu conteaza": "doesn't matter"},
        "budget_label": "💰 Budget:",
        "budget_opts": {"scazut": "low", "ridicat": "high"},
        "nights_label": "🛌 Number of nights:",
        "find_btn": "🔍 Find the ideal resort",
        "no_result": "❌ No resort matches your selected criteria.",
        "prefs_title": "### 🔎 Selected preferences:",
        "pref_sezon": "Season",
        "pref_trav": "Traveler type",
        "pref_budget": "Budget",
        "pref_nights": "Nights",
        "pref_info": "Info Center",
        "pref_cult": "Culture",
        "pref_alim": "Food",
        "recom": "🏖️ Recommendation: **{st}** ({jd}) – Activity: _{act}_",
        "img_missing": "⚠️ No local image found for this resort.",
        "img_error": "⚠️ Image loading error: {e}",
    }
}

# =========================
# Helper: background CSS
# =========================
DEFAULT_BG = "https://img.freepik.com/premium-photo/exploring-world-with-vintage-maps-smartphone_1276740-33677.jpg"   
BG_BY_ACTIVITY = {
    "plaja":     "https://preview.redd.it/cptzeo4cdie51.jpg?width=640&crop=smart&auto=webp&s=2f4e68544383ea87a937c8e2b2288a731f1dd001",  # beach
    "partie":    "https://www.pluxee.ro/sites/g/files/jclxxe416/files/styles/coh_x_large/public/2023-09/poiana-brasov-475293493.jpeg.webp?itok=uLDB9uXc",  # ski
    "trasee":    "https://lp-cms-production.imgix.net/2024-08/LPT1009063.jpg?auto=format,compress&q=72&w=1440&h=810&fit=crop",  # trails/mountain
    "tratament": "https://static.independent.co.uk/2024/04/04/17/Evening%20at%20The%20Palm%2C%20Therme%2C%20Bucharest%20%28Photo_%20Therme%29.JPG",  # spa/therapy
}

def set_background(url: str, overlay_rgba="rgba(255,255,255,0.60)"):
    st.markdown(
        f"""
        <style>
        /* Force light mode and clear base bg */
        html, body, [data-testid="stAppViewContainer"] {{
            color-scheme: light !important;
            background-color: transparent !important;
        }}
        /* Background image */
        .stApp {{
            background: url("{url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            position: relative;
        }}
        /* Semi-transparent overlay */
        .stApp::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: {overlay_rgba};
            z-index: 0;
        }}
        /* Keep app content above overlay */
        .stApp > div:first-child {{
            position: relative;
            z-index: 1;
        }}
        /* Titles & text: black */
        h1, h2, h3, h4, h5, h6, .stMarkdown p, div[data-testid="stMarkdownContainer"] * {{
            color: #111111 !important;
            text-shadow: none !important;
        }}

        /* White cards + black text for ALL inputs */
        div[data-testid="stRadio"],
        div[data-testid="stSelectbox"],
        div[data-testid="stSlider"],
        div[data-testid="stNumberInput"],
        div[data-testid="stCheckbox"],
        div[data-testid="stTextInput"] {{
            background: #FFFFFF !important;
            border: 1px solid rgba(0,0,0,0.10);
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}
        div[data-testid="stRadio"] *,
        div[data-testid="stSelectbox"] *,
        div[data-testid="stSlider"] *,
        div[data-testid="stNumberInput"] *,
        div[data-testid="stCheckbox"] *,
        div[data-testid="stTextInput"] * {{
            color: #111111 !important;
        }}

        /* Radio options as white pills (selected keeps white/black, thicker border) */
        div[role="radiogroup"] > label {{
            background: #FFFFFF !important;
            color: #111111 !important;
            border: 1px solid #CFCFCF !important;
            border-radius: 10px;
            padding: 6px 12px;
            margin: 4px;
        }}
        div[role="radiogroup"] input:checked + div {{
            background: #FFFFFF !important;
            color: #111111 !important;
            border: 2px solid #111111 !important;
            font-weight: 700 !important;
        }}
        input[type="radio"] {{ accent-color: #111111 !important; }}

        /* Buttons */
        button[kind="primary"], button[kind="secondary"] {{
            background: #FFFFFF !important;
            color: #111111 !important;
            border: 1px solid #999999 !important;
            border-radius: 10px;
            font-weight: 600;
        }}
        button[kind="primary"]:hover, button[kind="secondary"]:hover {{
            background-color: #F2F2F2 !important;
            border-color: #555555 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =========================
# Session state
# =========================
for key in ["recommendation", "no_result", "input_filters"]:
    if key not in st.session_state:
        st.session_state[key] = None

# Set default background first (form page)
set_background(DEFAULT_BG, overlay_rgba="rgba(255,255,255,0.55)")

# === Language toggle (always visible, restart on change) ===

# --- Language toggle with restart on change (no on_change callback) ---
if "lang" not in st.session_state:
    st.session_state.lang = "RO"  # default

LANG_CHOICES = ["🇷🇴 Română", "🇬🇧 English"]
current_lang = st.session_state.lang
idx = 0 if current_lang == "RO" else 1

choice = st.radio(
    "🌐 Alege limba / Choose language",
    LANG_CHOICES,
    horizontal=True,
    index=idx,
    key="lang_toggle_any"
)

new_lang = "RO" if choice.startswith("🇷🇴") else "EN"

# If the user changed the language (even on the results page), reset and rerun
if new_lang != current_lang:
    st.session_state.lang = new_lang
    for k in ["recommendation", "no_result", "input_filters"]:
        st.session_state[k] = None
    st.rerun()  # valid here (outside callback)

# Use T as before
lang = st.session_state.lang
T = LANG[lang]


# =========================
# Title & subtitle
# =========================
st.title(T["app_title"])
st.markdown(T["app_desc"])

# =========================
# Data & model (unchanged logic)
# =========================
df = pd.read_csv("statiuni_caracteristici_coord.csv")
model = joblib.load("mlp_model.pkl")

# Internal canonical values (RO) used by the model
sezoane = ['rece', 'cald', 'tot']
tipuri_calator = ['cuplu', 'familie', 'solo', 'grup']
map_traveler = {
    "cuplu": "Couple",
    "familie": "Family",
    "solo": "Solo traveler",
    "grup": "Group"
}
activitati = ['plaja', 'partie', 'trasee', 'tratament']
valoare_binar = {'nu': 0, 'da': 1, 'nu conteaza': None}
bugete = ['scazut', 'ridicat']

feature_names = [
    'sezon_rece', 'sezon_cald', 'sezon_tot',
    'travelerType_Couple', 'travelerType_Family', 'travelerType_Solo traveler', 'travelerType_Group',
    'activitate_principala_plaja', 'activitate_principala_partie',
    'activitate_principala_trasee', 'activitate_principala_tratament',
    'Info', 'Cultura', 'Alimentatie',
    'buget_scazut', 'buget_ridicat',
    'numberOfNights'
]

def choose_with_labels(label, options_map, key):
    labels = list(options_map.values())
    keys = list(options_map.keys())
    selected = st.radio(label, labels, horizontal=True, key=key)
    inv = {v: k for k, v in options_map.items()}
    return inv[selected]

# Reset button
if st.button(T["reset"], key="reset_btn"):
    for key in ["recommendation", "no_result", "input_filters"]:
        st.session_state[key] = None
    st.rerun()

# =========================
# FORM / INPUTS
# =========================
if st.session_state.recommendation is None and not st.session_state.no_result:
    sezon = choose_with_labels(T["sezon_label"], T["sezon_opts"], key="sezon")
    calator = choose_with_labels(T["traveler_label"], T["traveler_opts"], key="calator")
    activitate = choose_with_labels(T["activity_label"], T["activity_opts"], key="activitate")
    info_key = choose_with_labels(T["info_label"], T["tri_opts"], key="info")
    cultura_key = choose_with_labels(T["cult_label"], T["tri_opts"], key="cultura")
    alimentatie_key = choose_with_labels(T["alim_label"], T["tri_opts"], key="alim")
    buget = choose_with_labels(T["budget_label"], T["budget_opts"], key="buget")
    nopti = st.slider(T["nights_label"], 1, 14, 5, key="nopti")

    # Prepare model input (same logic)
    user_input = {col: 0 for col in feature_names}
    user_input[f'sezon_{sezon}'] = 1
    user_input[f'travelerType_{map_traveler[calator]}'] = 1
    user_input[f'activitate_principala_{activitate}'] = 1
    user_input[f'buget_{buget}'] = 1
    user_input['numberOfNights'] = nopti
    user_input['Info'] = valoare_binar[info_key]
    user_input['Cultura'] = valoare_binar[cultura_key]
    user_input['Alimentatie'] = valoare_binar[alimentatie_key]
    input_df = pd.DataFrame([user_input])

    if st.button(T["find_btn"], key="find_btn"):
        df_model = df.copy()
        df_features = df_model[feature_names].fillna(0)
        df_model['Scor_model'] = model.predict_proba(df_features)[:, 1]

        col_activitate = f'activitate_principala_{activitate}'
        col_buget = f'buget_{buget}'
        df_model = df_model[(df_model[col_activitate] == 1) & (df_model[col_buget] == 1)]

        scor = 0
        for col in input_df.columns:
            if col in df_model.columns and user_input[col] is not None:
                scor += (df_model[col] == user_input[col]).astype(int)
        scor -= abs(df_model['numberOfNights'] - nopti) / 10
        df_model['Scor_final'] = scor + df_model['Scor_model']

        if not df_model.empty:
            best = df_model.sort_values(by="Scor_final", ascending=False).iloc[0]
            st.session_state.recommendation = best
            st.session_state.input_filters = {
                T["pref_sezon"]: T["sezon_opts"][sezon].capitalize(),
                T["pref_trav"]: T["traveler_opts"][calator].capitalize(),
                "Activitate" if lang == "RO" else "Activity": T["activity_opts"][activitate].capitalize(),
                T["pref_info"]: T["tri_opts"][info_key].capitalize(),
                T["pref_cult"]: T["tri_opts"][cultura_key].capitalize(),
                T["pref_alim"]: T["tri_opts"][alimentatie_key].capitalize(),
                T["pref_budget"]: T["budget_opts"][buget].capitalize(),
                T["pref_nights"]: nopti,
                "_activitate_key": activitate,   # keep canonical for bg
            }
            st.session_state.no_result = False
        else:
            st.session_state.no_result = True

# =========================
# RESULTS
# =========================
if st.session_state.no_result:
    st.error(T["no_result"])

elif st.session_state.recommendation is not None:
    # Change background according to activity (after recommendation)
    act_key = st.session_state.input_filters.get("_activitate_key", "plaja")
    bg_url = BG_BY_ACTIVITY.get(act_key, DEFAULT_BG)
    set_background(bg_url, overlay_rgba="rgba(255,255,255,0.60)")

    recom = st.session_state.recommendation
    filters = st.session_state.input_filters

    st.markdown(T["prefs_title"])
    st.markdown(
        "\n".join(
            [
                f"- **{T['pref_sezon']}**: {filters[T['pref_sezon']]}",
                f"- **{T['pref_trav']}**: {filters[T['pref_trav']]}",
                f"- **{T['pref_budget']}**: {filters[T['pref_budget']]}",
                f"- **{T['pref_nights']}**: {filters[T['pref_nights']]}",
                f"- **{T['pref_info']}**: {filters[T['pref_info']]}",
                f"- **{T['pref_cult']}**: {filters[T['pref_cult']]}",
                f"- **{T['pref_alim']}**: {filters[T['pref_alim']]}",
            ]
        )
    )

    act_disp = filters["Activitate" if lang == "RO" else "Activity"]
    st.success(T["recom"].format(st=recom['Statiune'], jd=recom['Judet'], act=act_disp))

    # Image
    img_path = f"imagini/{recom['Statiune']}.jpg"
    try:
        image = Image.open(img_path)
        st.image(image, caption=recom['Statiune'])
    except FileNotFoundError:
        st.warning(T["img_missing"])
    except Exception as e:
        st.warning(T["img_error"].format(e=e))

    # Map
    if pd.notna(recom['Latitude']) and pd.notna(recom['Longitude']):
        m = folium.Map(location=[recom['Latitude'], recom['Longitude']], zoom_start=12)
        folium.Marker(
            [recom['Latitude'], recom['Longitude']],
            tooltip=recom['Statiune'],
            popup=f"{recom['Statiune']} ({recom['Judet']})"
        ).add_to(m)
        st_folium(m, width=700)
