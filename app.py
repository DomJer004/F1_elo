import streamlit as st
import pandas as pd
import math
import plotly.express as px

st.set_page_config(page_title="F1 Zaawansowane Elo", layout="wide")

# --- SŁOWNIK FLAG ---
FLAGS = {
    'British': '🇬🇧', 'Dutch': '🇳🇱', 'Monegasque': '🇲🇨', 'Spanish': '🇪🇸',
    'French': '🇫🇷', 'Australian': '🇦🇺', 'Japanese': '🇯🇵', 'Finnish': '🇫🇮',
    'Canadian': '🇨🇦', 'Thai': '🇹🇭', 'American': '🇺🇸', 'Chinese': '🇨🇳',
    'Mexican': '🇲🇽', 'German': '🇩🇪', 'Danish': '🇩🇰', 'New Zealander': '🇳🇿',
    'Italian': '🇮🇹', 'Brazilian': '🇧🇷', 'Polish': '🇵🇱', 'Argentine': '🇦🇷'
}

INITIAL_ELO = 1500
K_QUALI, K_SPRINT, K_RACE = 1.0, 1.5, 2.0

def get_expected_score(rating_a, rating_b):
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

def update_elo(event_results, specific_elo, overall_elo, k_factor):
    for drv in event_results:
        d_id = drv['driverId']
        if d_id not in specific_elo: specific_elo[d_id] = INITIAL_ELO
        if d_id not in overall_elo: overall_elo[d_id] = INITIAL_ELO
            
    changes_specific = {drv['driverId']: 0 for drv in event_results}
    changes_overall = {drv['driverId']: 0 for drv in event_results}
    
    for i in range(len(event_results)):
        for j in range(i + 1, len(event_results)):
            a, b = event_results[i], event_results[j]
            id_a, pos_a = a['driverId'], a['pos']
            id_b, pos_b = b['driverId'], b['pos']
            
            exp_a_spec = get_expected_score(specific_elo[id_a], specific_elo[id_b])
            exp_b_spec = get_expected_score(specific_elo[id_b], specific_elo[id_a])
            exp_a_ovr = get_expected_score(overall_elo[id_a], overall_elo[id_b])
            exp_b_ovr = get_expected_score(overall_elo[id_b], overall_elo[id_a])
            
            score_a = 1 if pos_a < pos_b else (0 if pos_a > pos_b else 0.5)
            score_b = 1 if pos_b < pos_a else (0 if pos_b > pos_a else 0.5)
            
            changes_specific[id_a] += k_factor * (score_a - exp_a_spec)
            changes_specific[id_b] += k_factor * (score_b - exp_b_spec)
            changes_overall[id_a] += k_factor * (score_a - exp_a_ovr)
            changes_overall[id_b] += k_factor * (score_b - exp_b_ovr)
            
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
        constructors = pd.read_csv('constructors.csv')
    except FileNotFoundError:
        st.error("Brakuje plików! Upewnij się, że masz: races, drivers, results, qualifying, sprint_results, constructors.")
        return pd.DataFrame(), pd.DataFrame()

    # Słowniki pomocnicze
    driver_dict = dict(zip(drivers.driverId, drivers.driverRef))
    # Łączymy wyniki z konstruktorami, żeby wyciągnąć aktualny zespół
    res_cons = results.merge(constructors, on='constructorId', suffixes=('', '_cons'))
    
    # Wyciąganie najnowszych informacji o zespole i narodowości dla kierowcy
    driver_info = {}
    for _, drv in drivers.iterrows():
        driver_info[drv['driverRef']] = {
            'Imie_Nazwisko': f"{drv['forename']} {drv['surname']}",
            'Narodowosc': drv['nationality'],
            'Data_Urodzenia': drv['dob'],
            'Zespol': 'Brak danych' # Domyślnie
        }
        
    # Szukamy ostatniego zespołu dla każdego kierowcy
    latest_races = res_cons.sort_values('raceId').groupby('driverId').tail(1)
    for _, row in latest_races.iterrows():
        d_ref = driver_dict.get(row['driverId'])
        if d_ref:
            driver_info[d_ref]['Zespol'] = row['name_cons']

    races = races.sort_values(by=['year', 'round'])
    elo_quali, elo_sprint, elo_race, elo_overall = {}, {}, {}, {}
    history = []

    for _, race in races.iterrows():
        r_id = race['raceId']
        
        quali_data = qualifying[qualifying['raceId'] == r_id]
        if not quali_data.empty:
            q_results = [{'driverId': row['driverId'], 'pos': row['position']} for _, row in quali_data.iterrows()]
            update_elo(q_results, elo_quali, elo_overall, K_QUALI)
            
        sprint_data = sprint_results[sprint_results['raceId'] == r_id]
        if not sprint_data.empty:
            s_results = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in sprint_data.iterrows()]
            update_elo(s_results, elo_sprint, elo_overall, K_SPRINT)
            
        race_data = results[results['raceId'] == r_id]
        if not race_data.empty:
            r_results = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in race_data.iterrows()]
            update_elo(r_results, elo_race, elo_overall, K_RACE)
            
            for drv in r_results:
                d_id = drv['driverId']
                d_ref = driver_dict.get(d_id, str(d_id))
                history.append({
                    'Data': race['date'],
                    'Rok': race['year'],
                    'Wyścig': race['name'],
                    'Kierowca': d_ref,
                    'Elo_Kwalifikacje': round(elo_quali.get(d_id, INITIAL_ELO), 1),
                    'Elo_Sprint': round(elo_sprint.get(d_id, INITIAL_ELO), 1),
                    'Elo_Wyścig': round(elo_race.get(d_id, INITIAL_ELO), 1),
                    'Elo_Ogólne': round(elo_overall.get(d_id, INITIAL_ELO), 1)
                })

    return pd.DataFrame(history), pd.DataFrame.from_dict(driver_info, orient='index')

# --- ŁADOWANIE DANYCH ---
with st.spinner("Ładowanie bazy F1..."):
    df_history, df_info = load_and_calculate_data()

if df_history.empty:
    st.stop()

# --- NAWIGACJA ---
st.title("🏎️ Formuła 1 - Baza Rankingowa Elo")
menu = st.sidebar.radio("Nawigacja", ["Rankingi Główne", "Profile Kierowców"])

latest_stats = df_history.sort_values('Data').groupby('Kierowca').tail(1)
active_drivers = latest_stats[latest_stats['Rok'] >= 2023]

if menu == "Rankingi Główne":
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("🏆 Aktualne Rankingi (Aktywni)")
        tab1, tab2, tab3, tab4 = st.tabs(["Ogólne", "Wyścig", "Kwalifikacje", "Sprint"])
        
        with tab1: st.dataframe(active_drivers[['Kierowca', 'Elo_Ogólne']].sort_values('Elo_Ogólne', ascending=False).reset_index(drop=True), height=400)
        with tab2: st.dataframe(active_drivers[['Kierowca', 'Elo_Wyścig']].sort_values('Elo_Wyścig', ascending=False).reset_index(drop=True), height=400)
        with tab3: st.dataframe(active_drivers[['Kierowca', 'Elo_Kwalifikacje']].sort_values('Elo_Kwalifikacje', ascending=False).reset_index(drop=True), height=400)
        with tab4: 
            sprint_drv = active_drivers[active_drivers['Elo_Sprint'] != INITIAL_ELO]
            st.dataframe(sprint_drv[['Kierowca', 'Elo_Sprint']].sort_values('Elo_Sprint', ascending=False).reset_index(drop=True), height=400)

    with col2:
        st.subheader("📈 Wykres kariery")
        elo_type = st.selectbox("Rodzaj Elo:", ['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'])
        all_drv = sorted(df_history['Kierowca'].unique())
        sel_drv = st.multiselect("Porównaj kierowców:", all_drv, default=['hamilton', 'max_verstappen', 'leclerc'])
        if sel_drv:
            fig = px.line(df_history[df_history['Kierowca'].isin(sel_drv)], x='Data', y=elo_type, color='Kierowca', hover_data=['Wyścig'])
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Profile Kierowców":
    st.header("👤 Profile Kierowców")
    
    # Wybór kierowcy z listy aktywnych
    driver_list = sorted(active_drivers['Kierowca'].unique())
    selected_driver = st.selectbox("Wybierz kierowcę:", driver_list)
    
    if selected_driver:
        info = df_info.loc[selected_driver]
        stats = latest_stats[latest_stats['Kierowca'] == selected_driver].iloc[0]
        
        flag = FLAGS.get(info['Narodowosc'], '🏁')
        
        # Wizytówka kierowcy
        st.markdown(f"""
        ### {flag} {info['Imie_Nazwisko']}
        **Zespół (Ostatni):** {info['Zespol']} | **Narodowość:** {info['Narodowosc']} | **Data ur.:** {info['Data_Urodzenia']}
        """)
        
        # Kafelki z rankingami (Metryki)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Elo Ogólne", stats['Elo_Ogólne'])
        c2.metric("Elo Wyścig", stats['Elo_Wyścig'])
        c3.metric("Elo Kwalifikacje", stats['Elo_Kwalifikacje'])
        c4.metric("Elo Sprint", stats['Elo_Sprint'] if stats['Elo_Sprint'] != INITIAL_ELO else "Brak danych")
        
        st.markdown("---")
        st.subheader(f"📈 Wykres ewolucji Elo ({info['Imie_Nazwisko']})")
        
        # Wykres wszystkich rodzajów Elo dla tego jednego kierowcy
        driver_history = df_history[df_history['Kierowca'] == selected_driver]
        
        # Przekształcamy dane do formatu przyjaznego dla Plotly (żeby mieć kilka linii na jednym wykresie)
        melted_df = driver_history.melt(id_vars=['Data', 'Wyścig', 'Rok'], 
                                        value_vars=['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'],
                                        var_name='Rodzaj_Elo', value_name='Wartość')
        
        # Usuwamy puste starty sprinterskie z wykresu, żeby nie psuły skali
        melted_df = melted_df[~((melted_df['Rodzaj_Elo'] == 'Elo_Sprint') & (melted_df['Wartość'] == INITIAL_ELO))]
        
        fig2 = px.line(melted_df, x='Data', y='Wartość', color='Rodzaj_Elo', 
                       title=f"Historia kariery - {info['Imie_Nazwisko']}",
                       hover_data=['Wyścig', 'Rok'])
        st.plotly_chart(fig2, use_container_width=True)
