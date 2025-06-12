# Rec-System-Turism-RO
# 🇷🇴 Sistem inteligent de Recomandare Turistică (România)

Acest proiect este un sistem interactiv de recomandare a stațiunilor turistice din România, dezvoltat în cadrul lucrării de dizertație la programul de master „Statistică și Data Science” – ASE București.

## 📌 Descriere generală

Aplicația permite utilizatorului să introducă preferințe privind:

- Sezonul călătoriei (cald / rece)
- Tipul de călător (cuplu, familie, solo, grup)
- Activitatea preferată (plajă, partie, trasee montane, tratament)
- Buget (scăzut / ridicat)
- Numărul de nopți
- Alte facilități dorite: centre de informare turistică, alimentație, activități culturale

Pe baza acestor inputuri, aplicația:

✅ recomandă stațiunea turistică optimă  
✅ afișează o imagine reprezentativă a stațiunii  
✅ poziționează stațiunea pe o hartă interactivă folosind coordonatele geografice  
✅ permite resetarea rapidă a filtrelor și păstrează filtrele aplicate

## 🧠 Tehnologii folosite

- `Python` (pandas, scikit-learn, PIL, folium, streamlit)
- `MLPClassifier` pentru clasificarea binară a stațiunilor recomandate
- `Streamlit` pentru interfața web interactivă
- `Folium` pentru generarea hărții dinamice

## 📁 Structură proiect

rec-system-turism-ro/

├── app.py # Aplicația principală Streamlit

├── mlp_model.pkl # Modelul antrenat de tip MLPClassifier

├── statiuni_caracteristici_coord.csv # Baza de date cu stațiuni și coordonate

├── /imagini # Imagini reprezentative pentru stațiuni (nume identic cu numele stațiunilor)

└── README.md # Acest fișier

# 🇬🇧 Smart Tourist Recommender System (Romania)

This project is an interactive recommendation system for tourist resorts in Romania, developed as part of a master's dissertation in the “Statistics and Data Science” program at ASE Bucharest.

## 📌 Overview

The app allows users to input preferences regarding:

- Travel season (warm / cold)
- Traveler type (couple, family, solo, group)
- Main activity of interest (beach, ski slope, hiking, treatment)
- Budget (low / high)
- Number of nights
- Additional preferences: tourist info centers, food services, cultural activities

Based on these inputs, the app:

✅ Recommends the most suitable tourist resort  
✅ Displays a representative image of the resort  
✅ Shows the resort’s position on an interactive map using geographic coordinates  
✅ Retains the selected filters and allows quick reset  

## 🧠 Technologies Used

- `Python` (pandas, scikit-learn, PIL, folium, streamlit)
- `MLPClassifier` used for binary classification of recommended resorts
- `Streamlit` for building the interactive web interface
- `Folium` for map generation and display

## 📁 Project Structure

rec-system-turism-ro/

├── app.py # Main Streamlit app

├── mlp_model.pkl # Trained MLPClassifier model

├── statiuni_caracteristici_coord.csv # Dataset with resort features and coordinates

├── /imagini # Folder with resort images (named exactly like the resorts)

└── README.md # This file
