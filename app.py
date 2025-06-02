import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from PIL import Image
import joblib

# === Setup pagină ===
st.set_page_config(page_title="Recomandare Turistică", layout="centered")
st.title("🏝️ Recomandare Turistică Inteligentă")
st.markdown("Completează preferințele pentru a primi o sugestie de stațiune din România.")

# === Load date + model ===
df = pd.read_csv("statiuni_caracteristici_coord.csv")
model = joblib.load("mlp_model.pkl")

# === Opțiuni și mapări ===
sezoane = ['rece', 'cald', 'tot']
tipuri_calator = ['couple', 'family', 'solo', 'group']
map_traveler = {
    "couple": "Couple",
    "family": "Family",
    "solo": "Solo traveler",
    "group": "Group"
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

# === Inițializare sesiune ===
for key in ["recommendation", "no_result", "input_filters"]:
    if key not in st.session_state:
        st.session_state[key] = None

# === Resetare ===
if st.button("🔄 Resetare filtre"):
    for key in ["recommendation", "no_result", "input_filters"]:
        st.session_state[key] = None
    st.rerun()

# === Colectare inputuri dacă nu avem deja un rezultat ===
if st.session_state.recommendation is None and not st.session_state.no_result:
    sezon = st.radio("🗓️ Sezonul preferat:", sezoane, horizontal=True)
    calator = st.radio("👤 Tipul de călător:", tipuri_calator, horizontal=True)
    activitate = st.radio("🎯 Activitatea principală:", activitati, horizontal=True)
    info = st.radio("ℹ️ Centru Info Turistic:", list(valoare_binar.keys()), horizontal=True)
    cultura = st.radio("🎭 Activități culturale:", list(valoare_binar.keys()), horizontal=True)
    alimentatie = st.radio("🍽️ Facilități alimentație:", list(valoare_binar.keys()), horizontal=True)
    buget = st.radio("💰 Buget disponibil:", bugete, horizontal=True)
    nopti = st.slider("🛌 Număr de nopți:", 1, 14, 5)

    user_input = {col: 0 for col in feature_names}
    user_input[f'sezon_{sezon}'] = 1
    user_input[f'travelerType_{map_traveler[calator]}'] = 1
    user_input[f'activitate_principala_{activitate}'] = 1
    user_input[f'buget_{buget}'] = 1
    user_input['numberOfNights'] = nopti
    user_input['Info'] = valoare_binar[info]
    user_input['Cultura'] = valoare_binar[cultura]
    user_input['Alimentatie'] = valoare_binar[alimentatie]
    input_df = pd.DataFrame([user_input])

    if st.button("🔍 Găsește stațiunea ideală"):
        df_model = df.copy()
        df_features = df_model[feature_names].fillna(0)
        df_model['Scor_model'] = model.predict_proba(df_features)[:, 1]

        # === Filtrare activitate + buget ===
        col_activitate = f'activitate_principala_{activitate}'
        col_buget = f'buget_{buget}'
        df_model = df_model[(df_model[col_activitate] == 1) & (df_model[col_buget] == 1)]

        # === Scor de potrivire
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
                "Sezon": sezon,
                "Tip călător": calator,
                "Activitate": activitate,
                "Info": info,
                "Cultura": cultura,
                "Alimentatie": alimentatie,
                "Buget": buget,
                "Nopți": nopti
            }
            st.session_state.no_result = False
        else:
            st.session_state.no_result = True

# === Afișare recomandare finală ===
if st.session_state.no_result:
    st.error("❌ Nicio stațiune nu corespunde criteriilor selectate.")
elif st.session_state.recommendation is not None:
    recom = st.session_state.recommendation
    filters = st.session_state.input_filters

    st.success(f"🏖️ Recomandare: **{recom['Statiune']}** ({recom['Judet']}) – Activitatea aleasa: _{filters['Activitate'].capitalize()}_")
    st.markdown("### 🔎 Preferințele tale:")
    st.markdown(f"""
    - **Sezon**: {filters['Sezon'].capitalize()}
    - **Tip călător**: {filters['Tip călător'].capitalize()}
    - **Buget**: {filters['Buget'].capitalize()}
    - **Număr nopți**: {filters['Nopți']}
    - **Centru Info**: {filters['Info'].capitalize()}
    - **Cultură**: {filters['Cultura'].capitalize()}
    - **Alimentație**: {filters['Alimentatie'].capitalize()}
    """)

    # === Imagine
    img_path = f"imagini/{recom['Statiune'].lower().replace(' ', '_')}.jpg"
    try:
        with open(img_path, "rb") as file:
            st.image(file, caption=recom['Statiune'])
    except FileNotFoundError::
        st.warning("⚠️ Nu există imagine locală pentru această stațiune.")

    # === Hartă
    if pd.notna(recom['Latitude']) and pd.notna(recom['Longitude']):
        m = folium.Map(location=[recom['Latitude'], recom['Longitude']], zoom_start=12)
        folium.Marker(
            [recom['Latitude'], recom['Longitude']],
            tooltip=recom['Statiune'],
            popup=f"{recom['Statiune']} ({recom['Judet']})"
        ).add_to(m)
        st_folium(m, width=700)
