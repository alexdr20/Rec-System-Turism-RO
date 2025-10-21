import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import joblib

# === Config pagină ===
st.set_page_config(page_title="Recomandare Turistică", layout="centered")

# ---------------------------
#       i18n / Localizare
# ---------------------------
LANG = {
    "RO": {
        "app_title": "🏝️ Recomandare Turistică Inteligentă",
        "app_desc": "Completează preferințele pentru a primi o sugestie de stațiune din România.",
        "sidebar_lang": "Limbă / Language",
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
        "sidebar_lang": "Limbă / Language",
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

# Limba selectată în sidebar
# === Lang selector with flags ===
lang_display = st.sidebar.selectbox(
    "🌐 Choose language / Alege limba",
    ["🇷🇴 Română", "🇬🇧 English"],
    index=0
)
lang = "RO" if "🇷🇴" in lang_display else "EN"
T = LANG[lang]
# Helpers: mapăm eticheta afișată -> valoarea canonică (în română)
def choose_with_labels(label, options_map, key):
    """Arată radio cu etichete traduse, returnează cheia canonică."""
    labels = list(options_map.values())
    keys = list(options_map.keys())
    selected_label = st.radio(label, labels, horizontal=True, key=key)
    # găsește cheia canonică corespunzătoare etichetei selectate
    inv = {v: k for k, v in options_map.items()}
    return inv[selected_label]

def choose_with_labels_tristate(label, options_map, key):
    return choose_with_labels(label, options_map, key)

# ---------------------------
#    Titlu + descriere
# ---------------------------
st.title(T["app_title"])
st.markdown(T["app_desc"])

# === Încărcare date și model (logică neschimbată) ===
df = pd.read_csv("statiuni_caracteristici_coord.csv")
model = joblib.load("mlp_model.pkl")

# === Opțiuni / mapări interne (logica rămâne) ===
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

# === Inițializare stare aplicație ===
for key in ["recommendation", "no_result", "input_filters"]:
    if key not in st.session_state:
        st.session_state[key] = None

# === Resetare ===
if st.button(T["reset"], key="reset_btn"):
    for key in ["recommendation", "no_result", "input_filters"]:
        st.session_state[key] = None
    st.rerun()

# === Colectare inputuri dacă nu există recomandare ===
if st.session_state.recommendation is None and not st.session_state.no_result:
    # Selectoare cu etichete traduse, dar valori canonice înapoi
    sezon = choose_with_labels(T["sezon_label"], T["sezon_opts"], key="sezon")
    calator = choose_with_labels(T["traveler_label"], T["traveler_opts"], key="calator")
    activitate = choose_with_labels(T["activity_label"], T["activity_opts"], key="activitate")
    info_key = choose_with_labels_tristate(T["info_label"], T["tri_opts"], key="info")
    cultura_key = choose_with_labels_tristate(T["cult_label"], T["tri_opts"], key="cultura")
    alimentatie_key = choose_with_labels_tristate(T["alim_label"], T["tri_opts"], key="alim")
    buget = choose_with_labels(T["budget_label"], T["budget_opts"], key="buget")
    nopti = st.slider(T["nights_label"], 1, 14, 5, key="nopti")

    # Pregătire input model (logică identică)
    user_input = {col: 0 for col in feature_names}
    user_input[f'sezon_{sezon}'] = 1
    user_input[f'travelerType_{map_traveler[calator]}'] = 1
    user_input[f'activitate_principala_{activitate}'] = 1
    user_input[f'buget_{buget}'] = 1
    user_input['numberOfNights'] = nopti
    user_input['Info'] = {'nu': 0, 'da': 1, 'nu conteaza': None}[info_key]
    user_input['Cultura'] = {'nu': 0, 'da': 1, 'nu conteaza': None}[cultura_key]
    user_input['Alimentatie'] = {'nu': 0, 'da': 1, 'nu conteaza': None}[alimentatie_key]
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
            # salvăm filtrele în limbajul UI curent (pentru afișare)
            st.session_state.input_filters = {
                T["pref_sezon"]: T["sezon_opts"][sezon].capitalize(),
                T["pref_trav"]: T["traveler_opts"][calator].capitalize(),
                "Activitate" if lang == "RO" else "Activity": T["activity_opts"][activitate].capitalize(),
                T["pref_info"]: T["tri_opts"][info_key].capitalize(),
                T["pref_cult"]: T["tri_opts"][cultura_key].capitalize(),
                T["pref_alim"]: T["tri_opts"][alimentatie_key].capitalize(),
                T["pref_budget"]: T["budget_opts"][buget].capitalize(),
                T["pref_nights"]: nopti
            }
            st.session_state.no_result = False
        else:
            st.session_state.no_result = True

# === Afișare rezultate ===
if st.session_state.no_result:
    st.error(T["no_result"])
elif st.session_state.recommendation is not None:
    recom = st.session_state.recommendation
    filters = st.session_state.input_filters

    st.markdown(T["prefs_title"])
    # listăm preferințele în ordinea logică
    prefs_lines = [
        f"- **{list(filters.keys())[0]}**: {filters[list(filters.keys())[0]]}",
        f"- **{list(filters.keys())[1]}**: {filters[list(filters.keys())[1]]}",
        f"- **{T['pref_budget']}**: {filters[T['pref_budget']]}",
        f"- **{T['pref_nights']}**: {filters[T['pref_nights']]}",
        f"- **{T['pref_info']}**: {filters[T['pref_info']]}",
        f"- **{T['pref_cult']}**: {filters[T['pref_cult']]}",
        f"- **{T['pref_alim']}**: {filters[T['pref_alim']]}"
    ]
    st.markdown("\n".join(prefs_lines))

    act_disp = filters["Activitate" if lang == "RO" else "Activity"]
    st.success(T["recom"].format(st=recom['Statiune'], jd=recom['Judet'], act=act_disp))

    # === Imagine locală (cu nume exact)
    img_path = f"imagini/{recom['Statiune']}.jpg"
    try:
        image = Image.open(img_path)
        st.image(image, caption=recom['Statiune'])
    except FileNotFoundError:
        st.warning(T["img_missing"])
    except Exception as e:
        st.warning(T["img_error"].format(e=e))

    # === Hartă interactivă
    if pd.notna(recom['Latitude']) and pd.notna(recom['Longitude']):
        m = folium.Map(location=[recom['Latitude'], recom['Longitude']], zoom_start=12)
        folium.Marker(
            [recom['Latitude'], recom['Longitude']],
            tooltip=recom['Statiune'],
            popup=f"{recom['Statiune']} ({recom['Judet']})"
        ).add_to(m)
        st_folium(m, width=700)
