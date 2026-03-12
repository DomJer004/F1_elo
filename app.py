import streamlit as st
import pandas as pd
import math
import plotly.express as px

# --- USTAWIENIA STRONY ---
st.set_page_config(page_title="F1 Zaawansowane Elo", layout="wide")
st.title("🏎️ Formuła 1 - Baza Rankingowa Elo (Kwale, Sprint, Wyścig)")

# --- PARAMETRY ELO ---
INITIAL_ELO = 1500
# Wagi dla poszczególnych sesji przy obliczaniu odpowiednich Elo
K_QUALI = 1.0
K_SPRINT = 1.5
K_RACE = 2.0

def get_expected_score(rating_a, rating_b):
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

# Główna funkcja do aktualizacji rankingu
def update_elo(event_results, specific_elo, overall_elo, k_factor):
    # event_results to lista słowników: [{'driverId': id, 'pos': pozycja}, ...]
    
    # Rejestrujemy nowych kierowców
    for drv in event_results:
        d_id = drv['driverId']
        if d_id not in specific_elo: specific_elo[d_id] = INITIAL_ELO
        if d_id not in overall_elo: overall_elo[d_id] = INITIAL_ELO
            
    changes_specific = {drv['driverId']: 0 for drv in event_results}
    changes_overall = {drv['driverId']: 0 for drv in event_results}
    
    # Pojedynki każdy z każdym
    for i in range(len(event_results)):
        for j in range(i + 1, len(event_results)):
            a, b = event_results[i], event_results[j]
            id_a, pos_a = a['driverId'], a['pos']
            id_b, pos_b = b['driverId'], b['pos']
            
            # Oczekiwania dla konkretnej sesji (np. tylko kwale)
            exp_a_spec = get_expected_score(specific_elo[id_a], specific_elo[id_b])
            exp_b_spec = get_expected_score(specific_elo[id_b], specific_elo[id_a])
            
            # Oczekiwania dla rankingu ogólnego
            exp_a_ovr = get_expected_score(overall_elo[id_a], overall_elo[id_b])
            exp_b_ovr = get_expected_score(overall_elo[id_b], overall_elo[id_a])
            
            # Wynik starcia
            score_a = 1 if pos_a < pos_b else (0 if pos_a > pos_b else 0.5)
            score_b = 1 if pos_b < pos_a else (0 if pos_b > pos_a else 0.5)
            
            # Zmiany
            changes_specific[id_a] += k_factor * (score_a - exp_a_spec)
            changes_specific[id_b] += k_factor * (score_b - exp_b_spec)
            
            changes_overall[id_a] += k_factor * (score_a - exp_a_ovr)
            changes_overall[id_b] += k_factor * (score_b - exp_b_ovr)
            
    # Zastosowanie zmian
    for d_id in changes_specific:
        specific_elo[d_id] += changes_specific[d_id]
        overall_elo[d_id] += changes_overall[d_id]


@st.cache_data
def load_and_calculate_data():
    try:
        races = pd.read_csv('races.csv')
        drivers = pd.read_csv('drivers.csv')
        results = pd.read_csv('results.csv')
        qualifying = pd.read_csv('qualifying.csv')
        sprint_results = pd.read_csv('sprint_results.csv')
    except FileNotFoundError:
        st.error("Brakuje plików CSV! Upewnij się, że masz: races, drivers, results, qualifying, sprint_results.")
        return pd.DataFrame()

    # Słownik ułatwiający zamianę ID na nazwisko
    driver_dict = dict(zip(drivers.driverId, drivers.driverRef))
    
    races = races.sort_values(by=['year', 'round'])
    
    # Inicjalizacja 4 osobnych rankingów
    elo_quali = {}
    elo_sprint = {}
    elo_race = {}
    elo_overall = {}
    
    history = []

    for _, race in races.iterrows():
        r_id = race['raceId']
        
        # 1. KWALIFIKACJE
        quali_data = qualifying[qualifying['raceId'] == r_id]
        if not quali_data.empty:
            q_results = [{'driverId': row['driverId'], 'pos': row['position']} for _, row in quali_data.iterrows()]
            update_elo(q_results, elo_quali, elo_overall, K_QUALI)
            
        # 2. SPRINT
        sprint_data = sprint_results[sprint_results['raceId'] == r_id]
        if not sprint_data.empty:
            s_results = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in sprint_data.iterrows()]
            update_elo(s_results, elo_sprint, elo_overall, K_SPRINT)
            
        # 3. WYŚCIG
        race_data = results[results['raceId'] == r_id]
        if not race_data.empty:
            r_results = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in race_data.iterrows()]
            update_elo(r_results, elo_race, elo_overall, K_RACE)
            
            # Zapisujemy stan rankingów PO CAŁYM WEEKENDZIE dla wszystkich kierowców z tego wyścigu
            for drv in r_results:
                d_id = drv['driverId']
                history.append({
                    'Data': race['date'],
                    'Rok': race['year'],
                    'Wyścig': race['name'],
                    'Kierowca': driver_dict.get(d_id, str(d_id)),
                    'Elo_Kwalifikacje': round(elo_quali.get(d_id, INITIAL_ELO), 1),
                    'Elo_Sprint': round(elo_sprint.get(d_id, INITIAL_ELO), 1),
                    'Elo_Wyścig': round(elo_race.get(d_id, INITIAL_ELO), 1),
                    'Elo_Ogólne': round(elo_overall.get(d_id, INITIAL_ELO), 1)
                })

    return pd.DataFrame(history)

# --- ŁADOWANIE DANYCH ---
with st.spinner("Przeliczanie historii F1 (Kwale, Sprinty, Wyścigi)..."):
    df_history = load_and_calculate_data()

if df_history.empty:
    st.stop()

# --- INTERFEJS ---
st.success("Dane załadowane i przeliczone!")

# Filtrujemy do aktualnych kierowców (jeździli po 2023 roku)
latest_stats = df_history.sort_values('Data').groupby('Kierowca').tail(1)
active_drivers = latest_stats[latest_stats['Rok'] >= 2023]

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🏆 Aktualne Rankingi (Aktywni)")
    
    # Tworzymy zakładki dla różnych kategorii Elo
    tab_ogolne, tab_wyscig, tab_kwale, tab_sprint = st.tabs(["Ogólne", "Wyścig", "Kwalifikacje", "Sprint"])
    
    with tab_ogolne:
        st.dataframe(active_drivers[['Kierowca', 'Elo_Ogólne']].sort_values('Elo_Ogólne', ascending=False).reset_index(drop=True), height=400)
    with tab_wyscig:
        st.dataframe(active_drivers[['Kierowca', 'Elo_Wyścig']].sort_values('Elo_Wyścig', ascending=False).reset_index(drop=True), height=400)
    with tab_kwale:
        st.dataframe(active_drivers[['Kierowca', 'Elo_Kwalifikacje']].sort_values('Elo_Kwalifikacje', ascending=False).reset_index(drop=True), height=400)
    with tab_sprint:
        # Pokaż tylko tych, którzy w ogóle jechali w sprincie (ich Elo różni się od startowego 1500)
        sprint_drivers = active_drivers[active_drivers['Elo_Sprint'] != INITIAL_ELO]
        st.dataframe(sprint_drivers[['Kierowca', 'Elo_Sprint']].sort_values('Elo_Sprint', ascending=False).reset_index(drop=True), height=400)

with col2:
    st.subheader("📈 Wykres historii kariery")
    
    # Wybór kategorii do wyświetlenia na wykresie
    elo_type = st.selectbox("Wybierz rodzaj Elo do wykresu:", 
                            ['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'])
    
    all_drivers_list = sorted(df_history['Kierowca'].unique())
    default_drivers = ['hamilton', 'max_verstappen', 'leclerc', 'norris']
    selected_drivers = st.multiselect("Wybierz kierowców do porównania:", all_drivers_list, default=default_drivers)
    
    if selected_drivers:
        filtered_df = df_history[df_history['Kierowca'].isin(selected_drivers)]
        # Wykres liniowy Plotly
        fig = px.line(filtered_df, x='Data', y=elo_type, color='Kierowca', hover_data=['Wyścig', 'Rok'])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Wybierz kierowców z listy powyżej, aby zobaczyć wykres.")
