import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
from PIL import Image
import joblib

# Încarcă datele și modelul
statiuni_df = pd.read_csv("statiuni_caracteristici_coord.csv")
model = joblib.load("mlp_model.pkl")

# === FUNCȚIE DE RECOMANDARE ===
def genereaza_recomandare(df, activitate, sezon, tip_calator, buget, nopti):
    filtrate = df[
        (df['Activitate'] == activitate) &
        (df[sezon] == 1) &
        (df['travelerType'] == tip_calator) &
        (df['Buget'] == buget) &
        (df['numberOfNights'].between(nopti - 3, nopti + 3))
    ]
    if not filtrate.empty:
        filtrate = filtrate.copy()
        features = filtrate[model.feature_names_in_].fillna(0)
        filtrate['prob'] = model.predict_proba(features)[:, 1]
        return filtrate.sort_values(by="prob", ascending=False).iloc[0]
    return None

# === FUNCTIE SALVARE UTILIZATOR ===
def salveaza_recomandare(nume, statiune, judet, activitate):
    df_log = pd.DataFrame([[nume, statiune, judet, activitate]],
                          columns=['Nume', 'Statiune', 'Judet', 'Activitate'])
    if os.path.exists("recomandari_utilizatori.csv"):
        df_log.to_csv("recomandari_utilizatori.csv", mode='a', header=False, index=False)
    else:
        df_log.to_csv("recomandari_utilizatori.csv", index=False)

# === INTERFAȚA STREAMLIT ===
st.set_page_config(page_title="Recomandare Turistică", page_icon="🌍")
st.title("🌄 Sistem Inteligent de Recomandare a Stațiunilor din România")

if "nume" not in st.session_state:
    st.session_state.nume = ""

if st.session_state.nume == "":
    st.subheader("Bine ai venit! 👋")
    st.session_state.nume = st.text_input("Introdu numele tău pentru a continua:")
    if st.session_state.nume:
        st.experimental_rerun()
else:
    st.success(f"Salut, {st.session_state.nume}! Completează preferințele tale pentru a primi o recomandare personalizată.")

    with st.form("filtre_form"):
        activitate = st.selectbox("Alege activitatea preferată:", statiuni_df['Activitate'].unique())
        sezon = st.selectbox("În ce sezon dorești să călătorești?", ['Rece', 'Cald', 'Tot'])
        tip_calator = st.selectbox("Ce tip de călător ești?", statiuni_df['travelerType'].unique())
        buget = st.selectbox("Ce buget ai?", statiuni_df['Buget'].unique())
        nopti = st.slider("Câte nopți dorești să petreci?", 1, 14, 5)
        trimite = st.form_submit_button("🔍 Găsește recomandarea mea")

    if trimite:
        recom = genereaza_recomandare(statiuni_df, activitate, sezon, tip_calator, buget, nopti)

        if recom is not None:
            st.success(f"🏖️ Recomandare: **{recom['Statiune']}** ({recom['Judet']})\n\n🎯 Activitate: **{recom['Activitate']}**")
            salveaza_recomandare(st.session_state.nume, recom['Statiune'], recom['Judet'], recom['Activitate'])

            # Imagine
            image_path = f"imagini/{recom['Statiune']}.jpg"
            if os.path.exists(image_path):
                image = Image.open(image_path)
                st.image(image, caption=recom['Statiune'], use_column_width=True)
            else:
                st.warning("Imaginea pentru această stațiune nu este disponibilă.")

            # Hartă
            m = folium.Map(location=[recom['Latitude'], recom['Longitude']], zoom_start=10)
            folium.Marker([recom['Latitude'], recom['Longitude']], popup=recom['Statiune']).add_to(m)
            st_folium(m, width=700)
        else:
            st.error("❌ Ne pare rău, nu am găsit nicio stațiune care să corespundă exact preferințelor tale.")

    # Buton resetare
    if st.button("🔄 Resetează și începe din nou"):
        st.session_state.nume = ""
        st.experimental_rerun()
