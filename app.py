import streamlit as st
import pandas as pd
import math
import plotly.express as px

st.set_page_config(page_title="F1 Zaawansowane Elo", layout="wide")

# --- SŁOWNIK FLAG DO FLAGCDN (Kody ISO krajów) ---
NATIONALITY_TO_CODE = {
    'British': 'gb', 'Dutch': 'nl', 'Monegasque': 'mc', 'Spanish': 'es',
    'French': 'fr', 'Australian': 'au', 'Japanese': 'jp', 'Finnish': 'fi',
    'Canadian': 'ca', 'Thai': 'th', 'American': 'us', 'Chinese': 'cn',
    'Mexican': 'mx', 'German': 'de', 'Danish': 'dk', 'New Zealander': 'nz',
    'Italian': 'it', 'Brazilian': 'br', 'Polish': 'pl', 'Argentine': 'ar',
    'Argentinian': 'ar', 'Swiss': 'ch', 'Belgian': 'be', 'Austrian': 'at',
    'Swedish': 'se', 'South African': 'za', 'Russian': 'ru', 'Colombian': 'co',
    'Venezuelan': 've', 'Indian': 'in', 'Indonesian': 'id', 'Irish': 'ie',
    'Portuguese': 'pt', 'Chilean': 'cl', 'Rhodesian': 'zw', 'Uruguayan': 'uy',
    'Liechtensteiner': 'li', 'Malaysian': 'my', 'Hungarian': 'hu', 'Czech': 'cz'
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

    res_cons = results.merge(constructors, on='constructorId', suffixes=('', '_cons'))
    
    # Przetwarzanie kierowców (Wielkie litery i Flagi z Flagcdn)
    driver_dict = {}
    driver_info = {}
    for _, drv in drivers.iterrows():
        # Imię i nazwisko WIELKIMI LITERAMI
        full_name = f"{drv['forename']} {drv['surname']}".upper()
        driver_dict[drv['driverId']] = full_name
        
        nat = drv['nationality']
        code = NATIONALITY_TO_CODE.get(nat, '')
        flag_url = f"https://flagcdn.com/24x18/{code}.png" if code else None
        
        driver_info[full_name] = {
            'Narodowosc': nat,
            'Flaga_URL': flag_url,
            'Data_Urodzenia': drv['dob'],
            'Zespol': 'Brak danych'
        }
        
    latest_races = res_cons.sort_values('raceId').groupby('driverId').tail(1)
    for _, row in latest_races.iterrows():
        full_name = driver_dict.get(row['driverId'])
        if full_name:
            # Naprawiony błąd: używamy row['name']
            driver_info[full_name]['Zespol'] = row['name'] 

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
                full_name = driver_dict.get(d_id, str(d_id))
                history.append({
                    'Data': race['date'],
                    'Rok': race['year'],
                    'Wyścig': race['name'],
                    'Kierowca': full_name,
                    'Elo_Kwalifikacje': round(elo_quali.get(d_id, INITIAL_ELO), 1),
                    'Elo_Sprint': round(elo_sprint.get(d_id, INITIAL_ELO), 1),
                    'Elo_Wyścig': round(elo_race.get(d_id, INITIAL_ELO), 1),
                    'Elo_Ogólne': round(elo_overall.get(d_id, INITIAL_ELO), 1)
                })

    return pd.DataFrame(history), pd.DataFrame.from_dict(driver_info, orient='index')

# --- FUNKCJA WYSWIETLAJĄCA TABELE ---
def display_table(df, elo_col):
    if elo_col == 'Elo_Sprint':
        df = df[df['Elo_Sprint'] != INITIAL_ELO]
        
    disp_df = df[['Flaga_URL', 'Kierowca', elo_col]].sort_values(elo_col, ascending=False).reset_index(drop=True)
    # Zmieniamy indeks, aby zaczynał się od 1, a nie od 0
    disp_df.index = disp_df.index + 1
    
    st.dataframe(
        disp_df,
        column_config={
            "Flaga_URL": st.column_config.ImageColumn("Kraj"),
            "Kierowca": st.column_config.TextColumn("Kierowca"),
            elo_col: st.column_config.NumberColumn("Punkty Elo", format="%.1f")
        },
        height=450,
        use_container_width=True
    )

# --- ŁADOWANIE DANYCH ---
with st.spinner("Ładowanie bazy F1..."):
    df_history, df_info = load_and_calculate_data()

if df_history.empty:
    st.stop()

# --- NAWIGACJA ---
st.title("🏎️ Formuła 1 - Baza Rankingowa Elo")
menu = st.sidebar.radio("Nawigacja", ["Rankingi Sezonowe", "Profile Kierowców"])

if menu == "Rankingi Sezonowe":
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        # WYBÓR HISTORYCZNYCH SEZONÓW
        dostepne_lata = sorted(df_history['Rok'].unique(), reverse=True)
        wybrany_rok = st.selectbox("Wybierz sezon:", dostepne_lata)
        
        # Filtrujemy dane do wybranego roku i pobieramy ostatni wynik z tego roku
        sezon_df = df_history[df_history['Rok'] == wybrany_rok]
        ostatnie_wyniki = sezon_df.sort_values('Data').groupby('Kierowca').tail(1).copy()
        
        # Dodajemy kolumnę z Flagi_URL do wyświetlania w tabeli
        ostatnie_wyniki['Flaga_URL'] = ostatnie_wyniki['Kierowca'].apply(
            lambda x: df_info.loc[x, 'Flaga_URL'] if x in df_info.index else None
        )

        st.subheader(f"🏆 Tabele końcowe: {wybrany_rok}")
        tab1, tab2, tab3, tab4 = st.tabs(["Ogólne", "Wyścig", "Kwalifikacje", "Sprint"])
        
        with tab1: display_table(ostatnie_wyniki, 'Elo_Ogólne')
        with tab2: display_table(ostatnie_wyniki, 'Elo_Wyścig')
        with tab3: display_table(ostatnie_wyniki, 'Elo_Kwalifikacje')
        with tab4: display_table(ostatnie_wyniki, 'Elo_Sprint')

    with col_right:
        st.subheader("📈 Wykres rywalizacji (Cała historia)")
        elo_type = st.selectbox("Rodzaj Elo:", ['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'])
        all_drv = sorted(df_history['Kierowca'].unique())
        
        # Proponowani zawodnicy
        def_drv = [d for d in ['LEWIS HAMILTON', 'MAX VERSTAPPEN', 'CHARLES LECLERC'] if d in all_drv]
        sel_drv = st.multiselect("Porównaj kierowców:", all_drv, default=def_drv)
        
        if sel_drv:
            fig = px.line(df_history[df_history['Kierowca'].isin(sel_drv)], 
                          x='Data', y=elo_type, color='Kierowca', hover_data=['Wyścig', 'Rok'])
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Profile Kierowców":
    st.header("👤 Profile Kierowców")
    
    # Możesz wyszukać każdego kierowcę w historii
    driver_list = sorted(df_info.index.unique())
    selected_driver = st.selectbox("Wybierz kierowcę:", driver_list)
    
    if selected_driver:
        info = df_info.loc[selected_driver]
        
        # Szukamy ostatniego zarejestrowanego wyniku w całej karierze
        ostatnie = df_history[df_history['Kierowca'] == selected_driver].sort_values('Data').tail(1).iloc[0]
        
        col_img, col_txt = st.columns([1, 15])
        with col_img:
            if info['Flaga_URL']:
                st.image(info['Flaga_URL'], width=40)
        with col_txt:
            st.markdown(f"### {selected_driver}")
            
        st.markdown(f"**Ostatni Zespół:** {info['Zespol']} | **Narodowość:** {info['Narodowosc']} | **Data ur.:** {info['Data_Urodzenia']}")
        
        # Kafelki
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Elo Ogólne (Obecne/Końcowe)", ostatnie['Elo_Ogólne'])
        c2.metric("Elo Wyścig", ostatnie['Elo_Wyścig'])
        c3.metric("Elo Kwalifikacje", ostatnie['Elo_Kwalifikacje'])
        c4.metric("Elo Sprint", ostatnie['Elo_Sprint'] if ostatnie['Elo_Sprint'] != INITIAL_ELO else "Brak")
        
        st.markdown("---")
        st.subheader(f"📈 Wykres kariery - {selected_driver}")
        
        driver_history = df_history[df_history['Kierowca'] == selected_driver]
        melted_df = driver_history.melt(id_vars=['Data', 'Wyścig', 'Rok'], 
                                        value_vars=['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'],
                                        var_name='Rodzaj_Elo', value_name='Wartość')
        
        # Usuwamy z wykresu zera ze sprintów
        melted_df = melted_df[~((melted_df['Rodzaj_Elo'] == 'Elo_Sprint') & (melted_df['Wartość'] == INITIAL_ELO))]
        
        fig2 = px.line(melted_df, x='Data', y='Wartość', color='Rodzaj_Elo', 
                       hover_data=['Wyścig', 'Rok'])
        st.plotly_chart(fig2, use_container_width=True)
