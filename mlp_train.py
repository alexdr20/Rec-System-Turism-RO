import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import joblib

# === 1. Încarcă datele cu coordonate ===
df = pd.read_csv("statiuni_caracteristici_coord.csv")

# === 2. Definește lista de variabile folosite la antrenare ===
feature_names = [
    'sezon_rece', 'sezon_cald', 'sezon_tot',
    'travelerType_Couple', 'travelerType_Family', 'travelerType_Solo traveler', 'travelerType_Group',
    'activitate_principala_plaja', 'activitate_principala_partie',
    'activitate_principala_trasee', 'activitate_principala_tratament',
    'Info', 'Cultura', 'Alimentatie',
    'buget_scazut', 'buget_ridicat',
    'numberOfNights'
]

# === 3. Pregătește datele
X = df[feature_names]
y = (X["numberOfNights"] > 3).astype(int)  # target simplificat: recomandabil dacă nopțile > 3

# === 4. Împarte datele
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# === 5. Creează și antrenează modelul
mlp_model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500, random_state=42)
mlp_model.fit(X_train, y_train)

# === 6. Salvează modelul
joblib.dump(mlp_model, "mlp_model.pkl")
print("✅ Modelul MLP a fost salvat ca 'mlp_model.pkl'")
