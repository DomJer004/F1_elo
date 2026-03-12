import streamlit as st
import pandas as pd
import math
import plotly.express as px

# --- USTAWIENIA STRONY ---
st.set_page_config(page_title="F1 Elo Ranking", layout="wide")
st.title("🏎️ Formuła 1 - Baza Rankingowa Elo")

# --- BAZA ELO NA START (Rozwiązanie dla mistrzów F2 itp.) ---
# Standardowy debiutant dostaje 1400. 
# Tutaj możesz dodawać "driverRef" z pliku drivers.csv i ich punkty na start.
CUSTOM_INITIAL_ELO = {
    'leclerc': 1550,     # Mistrz F2
    'russell': 1550,     # Mistrz F2
    'piastri': 1550,     # Mistrz F2
    'hamilton': 1550,    # Mistrz GP2
    'rosberg': 1550,     # Mistrz GP2
    'hulkenberg': 1550,  # Mistrz GP2
    'vandoorne': 1550,   # Mistrz GP2
    'max_verstappen': 1500, # Prosto z F3, ogromny talent, ale bez tytułu F2
    # Możesz dodawać kolejnych! Reszta dostanie domyślne 1400.
}

DEFAULT_INITIAL_ELO = 1400
K_FACTOR = 2

def get_initial_elo(driver_ref):
    return CUSTOM_INITIAL_ELO.get(driver_ref, DEFAULT_INITIAL_ELO)

def get_expected_score(rating_a, rating_b):
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

# --- WCZYTYWANIE I PRZELICZANIE DANYCH ---
# st.cache_data sprawia, że przeliczamy historię tylko raz, a nie przy każdym kliknięciu
@st.cache_data
def calculate_elo_history():
    races = pd.read_csv('races.csv')
    results = pd.read_csv('results.csv')
    drivers = pd.read_csv('drivers.csv')

    df = results.merge(races, on='raceId').merge(drivers, on='driverId')
    df = df.sort_values(by=['year', 'round'])

    elo_ratings = {} 
    elo_history = []
    
    grouped_races = df.groupby('raceId', sort=False)

    for race_id, race_data in grouped_races:
        race_results = race_data[['driverId', 'driverRef', 'positionOrder', 'year', 'name', 'date']].dropna()
        
        current_race_elo = {}
        for _, row in race_results.iterrows():
            driver_id = row['driverId']
            driver_ref = row['driverRef']
            if driver_id not in elo_ratings:
                # Tutaj aplikujemy nasz customowy ranking na start!
                elo_ratings[driver_id] = get_initial_elo(driver_ref)
            current_race_elo[driver_id] = elo_ratings[driver_id]
            
        elo_changes = {driver: 0 for driver in race_results['driverId']}
        drivers_list = race_results.to_dict('records')
        
        # Pojedynki każdy z każdym
        for i in range(len(drivers_list)):
            for j in range(i + 1, len(drivers_list)):
                driver_a, driver_b = drivers_list[i], drivers_list[j]
                
                id_a, pos_a = driver_a['driverId'], driver_a['positionOrder']
                id_b, pos_b = driver_b['driverId'], driver_b['positionOrder']
                
                rating_a, rating_b = current_race_elo[id_a], current_race_elo[id_b]
                
                expected_a = get_expected_score(rating_a, rating_b)
                expected_b = get_expected_score(rating_b, rating_a)
                
                score_a = 1 if pos_a < pos_b else (0 if pos_a > pos_b else 0.5)
                score_b = 1 if pos_b < pos_a else (0 if pos_b > pos_a else 0.5)
                
                elo_changes[id_a] += K_FACTOR * (score_a - expected_a)
                elo_changes[id_b] += K_FACTOR * (score_b - expected_b)
                
        # Zapis i aktualizacja
        for driver in drivers_list:
            driver_id = driver['driverId']
            elo_ratings[driver_id] += elo_changes[driver_id]
            
            elo_history.append({
                'Data': driver['date'],
                'Rok': driver['year'],
                'Wyścig': driver['name'],
                'Kierowca': driver['driverRef'],
                'Elo': round(elo_ratings[driver_id], 1)
            })

    return pd.DataFrame(elo_history)

# --- INTERFEJS APLIKACJI STREAMLIT ---
with st.spinner("Przeliczanie historii F1... (To może potrwać kilka sekund)"):
    history_df = calculate_elo_history()

st.success("Dane załadowane!")

# Wyciągamy najnowszy ranking dla każdego kierowcy
current_ranking = history_df.sort_values('Data').groupby('Kierowca').tail(1)[['Kierowca', 'Elo', 'Rok']]
# Filtrujemy tylko tych, którzy jeździli niedawno (np. od 2023 roku)
active_drivers = current_ranking[current_ranking['Rok'] >= 2023].sort_values('Elo', ascending=False)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏆 Aktualny Ranking Elo (Aktywni kierowcy)")
    st.dataframe(active_drivers[['Kierowca', 'Elo']].reset_index(drop=True), height=500)

with col2:
    st.subheader("📈 Wykres kariery (Porównaj kierowców)")
    all_drivers_list = sorted(history_df['Kierowca'].unique())
    
    # Domyślnie pokazujemy kilku ciekawych kierowców
    default_drivers = ['hamilton', 'max_verstappen', 'leclerc', 'alonso']
    selected_drivers = st.multiselect("Wybierz kierowców do porównania:", all_drivers_list, default=default_drivers)
    
    if selected_drivers:
        filtered_df = history_df[history_df['Kierowca'].isin(selected_drivers)]
        # Wykres liniowy z Plotly
        fig = px.line(filtered_df, x='Data', y='Elo', color='Kierowca', hover_data=['Wyścig', 'Rok'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Wybierz przynajmniej jednego kierowcę z listy powyżej.")
