import streamlit as st
import pandas as pd
import math
import plotly.express as px

st.set_page_config(page_title="F1 Advanced Elo", layout="wide", page_icon="🏎️")

# --- SŁOWNIK JĘZYKOWY (TŁUMACZENIA) ---
T = {
    'Polski': {
        'title': "🏎️ Formuła 1 - Baza Rankingowa Elo",
        'nav': "Nawigacja",
        'menu_race': "🏁 Ranking po Wyścigu",
        'menu_peak': "👑 Ranking Wszech Czasów",
        'menu_decades': "📅 Najlepsi w Dekadach",
        'menu_profile': "👤 Profile Kierowców",
        'menu_track': "🛤️ Elo Torów (Trudność)",
        'menu_results': "📊 Wyniki Wyścigów",
        'missing_files': "Brakuje plików! Upewnij się, że masz pobrane: races, drivers, results, qualifying, sprint_results, constructors, circuits.",
        'loading': "Przeliczanie bazy danych i historii wyścigów...",
        'select_season': "Wybierz sezon:",
        'select_race': "Wybierz wyścig:",
        'select_decade': "Wybierz dekadę:",
        'tables_after': "🏆 Tabele po:",
        'overall': "Ogólne", 'race': "Wyścig", 'quali': "Kwalifikacje", 'sprint': "Sprint",
        'form_chart': "📈 Wykres formy w sezonie",
        'elo_type': "Rodzaj Elo:",
        'compare_drv': "Porównaj kierowców w tym roku:",
        'filters': "⚙️ Filtry (Nacja, Zespół)",
        'filter_nat': "Wyszukaj po Narodowości:",
        'filter_team': "Wyszukaj po Zespole:",
        'team': "Zespół", 'nat': "Narodowość", 'country': "Kraj", 'seasons': "Sezony", 'year': "Rok",
        'peak_title': "👑 Peak Elo - Ranking Wszech Czasów",
        'peak_desc': "Sprawdź, kto zanotował najwyższy, absolutny szczyt formy (Peak Elo) w całej historii Formuły 1. Zespół wskazuje, w jakich barwach kierowca osiągnął ten szczyt.",
        'top_peak': "🌋 Wszystkie wyniki (Pełny Ranking)",
        'peak_info': "💡 **Czym jest Peak Elo?** To najwyższa wartość punktowa, jaką dany zawodnik wygenerował w dowolnym momencie swojej kariery, będąc w absolutnym 'prime'.",
        'decades_title': "📅 Peak Elo - Najlepsi w Dekadach",
        'decades_desc': "Sprawdź, kto dominował w poszczególnych dziesięcioleciach. Algorytm wyszukuje najwyższe Elo osiągnięte przez kierowców w wybranym przedziale czasu.",
        'search_drv': "Wybierz kierowcę z listy:",
        'dob': "Data ur.", 'all_teams': "Wszystkie zespoły w karierze",
        'last_elo': "Ostatnie Elo (Pożegnalne/Obecne)", 'peak_max': "PEAK Elo (Max)", 'lowest_elo': "Najniższe Elo (Min)", 'races_count': "Liczba wystąpień (GP)",
        'career_path': "📈 Przebieg kariery",
        'track_title': "🛤️ Ranking Torów F1 (Indeks Chaosu)",
        'track_desc': "Każdy tor 'walczy' z faworytem wyścigu. Jeśli faworyt (kierowca z najwyższym Elo) nie wygra wyścigu, tor zyskuje punkty. Im wyższe Elo toru, tym bardziej jest nieprzewidywalny i trudny!",
        'track_table': "Zestawienie torów (Ranking pełny)",
        'track_chart': "📈 Ewolucja trudności toru",
        'race_results_title': "📊 Wyniki Historycznych Wyścigów",
        'pos': "Poz.", 'points': "Punkty", 'driver': "Kierowca"
    },
    'English': {
        'title': "🏎️ Formula 1 - Elo Rating Database",
        'nav': "Navigation",
        'menu_race': "🏁 Ranking after Race",
        'menu_peak': "👑 All-Time Peak Ranking",
        'menu_decades': "📅 Best of the Decades",
        'menu_profile': "👤 Driver Profiles",
        'menu_track': "🛤️ Track Elo (Difficulty)",
        'menu_results': "📊 Race Results",
        'missing_files': "Missing files! Ensure you have: races, drivers, results, qualifying, sprint_results, constructors, circuits.",
        'loading': "Calculating database and race history...",
        'select_season': "Select season:",
        'select_race': "Select race:",
        'select_decade': "Select decade:",
        'tables_after': "🏆 Standings after:",
        'overall': "Overall", 'race': "Race", 'quali': "Qualifying", 'sprint': "Sprint",
        'form_chart': "📈 Season Form Chart",
        'elo_type': "Elo Type:",
        'compare_drv': "Compare drivers this year:",
        'filters': "⚙️ Filters (Nationality, Team)",
        'filter_nat': "Search by Nationality:",
        'filter_team': "Search by Team:",
        'team': "Team", 'nat': "Nationality", 'country': "Country", 'seasons': "Seasons", 'year': "Year",
        'peak_title': "👑 Peak Elo - All-Time Ranking",
        'peak_desc': "Check who reached the absolute highest peak form (Peak Elo) in the history of Formula 1. The team indicates who they were driving for at that exact moment.",
        'top_peak': "🌋 All results (Full Ranking)",
        'peak_info': "💡 **What is Peak Elo?** It is the highest point value a driver generated at any point in their career, being in their absolute 'prime'.",
        'decades_title': "📅 Peak Elo - Best of the Decades",
        'decades_desc': "See who dominated in each decade. The algorithm finds the highest Elo achieved by drivers within the selected time frame.",
        'search_drv': "Select driver from the list:",
        'dob': "Date of Birth", 'all_teams': "All career teams",
        'last_elo': "Last Elo (Current/Final)", 'peak_max': "PEAK Elo (Max)", 'lowest_elo': "Lowest Elo (Min)", 'races_count': "Race Entries (GP)",
        'career_path': "📈 Career Progression",
        'track_title': "🛤️ F1 Track Ranking (Chaos Index)",
        'track_desc': "Each track 'fights' the race favorite. If the favorite (driver with highest Elo) fails to win, the track gains points. Higher Elo means a more unpredictable and difficult track!",
        'track_table': "Track breakdown (Full Ranking)",
        'track_chart': "📈 Track difficulty evolution",
        'race_results_title': "📊 Historical Race Results",
        'pos': "Pos", 'points': "Points", 'driver': "Driver"
    }
}

# --- SŁOWNIKI FLAG ---
NATIONALITY_TO_CODE = {
    'British': 'gb', 'Dutch': 'nl', 'Monegasque': 'mc', 'Spanish': 'es', 'French': 'fr', 'Australian': 'au', 
    'Japanese': 'jp', 'Finnish': 'fi', 'Canadian': 'ca', 'Thai': 'th', 'American': 'us', 'Chinese': 'cn',
    'Mexican': 'mx', 'German': 'de', 'Danish': 'dk', 'New Zealander': 'nz', 'Italian': 'it', 'Brazilian': 'br', 
    'Polish': 'pl', 'Argentine': 'ar', 'Argentinian': 'ar', 'Swiss': 'ch', 'Belgian': 'be', 'Austrian': 'at',
    'Swedish': 'se', 'South African': 'za', 'Russian': 'ru', 'Colombian': 'co', 'Venezuelan': 've', 'Indian': 'in', 
    'Indonesian': 'id', 'Irish': 'ie', 'Portuguese': 'pt', 'Chilean': 'cl', 'Rhodesian': 'zw', 'Uruguayan': 'uy',
    'Liechtensteiner': 'li', 'Malaysian': 'my', 'Hungarian': 'hu', 'Czech': 'cz'
}

CIRCUIT_COUNTRY_TO_CODE = {
    'UK': 'gb', 'Austria': 'at', 'Italy': 'it', 'USA': 'us', 'United States': 'us', 'Spain': 'es',
    'Monaco': 'mc', 'Canada': 'ca', 'France': 'fr', 'Germany': 'de', 'Hungary': 'hu', 'Belgium': 'be', 
    'Netherlands': 'nl', 'Singapore': 'sg', 'Japan': 'jp', 'Brazil': 'br', 'Australia': 'au', 'Bahrain': 'bh',
    'China': 'cn', 'Azerbaijan': 'az', 'Mexico': 'mx', 'Saudi Arabia': 'sa', 'Qatar': 'qa', 'UAE': 'ae', 
    'Russia': 'ru', 'Malaysia': 'my', 'Portugal': 'pt', 'Turkey': 'tr', 'India': 'in', 'Korea': 'kr',
    'South Africa': 'za', 'Argentina': 'ar', 'Morocco': 'ma', 'Switzerland': 'ch', 'Sweden': 'se'
}

INITIAL_ELO = 1500
K_QUALI, K_SPRINT, K_RACE, K_TRACK = 1.0, 1.5, 2.0, 16.0

def get_expected_score(rating_a, rating_b):
    return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))

# --- GŁÓWNA LOGIKA ---
@st.cache_data
def load_and_calculate_data():
    try:
        races = pd.read_csv('races.csv')
        drivers = pd.read_csv('drivers.csv')
        results = pd.read_csv('results.csv')
        qualifying = pd.read_csv('qualifying.csv')
        sprint_results = pd.read_csv('sprint_results.csv')
        constructors = pd.read_csv('constructors.csv')
        circuits = pd.read_csv('circuits.csv')
    except FileNotFoundError:
        return None, None, None

    res_cons = results.merge(constructors, on='constructorId', suffixes=('', '_cons'))
    team_col_name = 'name_cons' if 'name_cons' in res_cons.columns else 'name'
    
    race_driver_team = {}
    for _, row in res_cons.iterrows():
        race_driver_team[(row['raceId'], row['driverId'])] = row[team_col_name]
        
    driver_teams = res_cons.groupby('driverId')[team_col_name].unique().to_dict()
    
    circuit_dict = dict(zip(circuits.circuitId, circuits.name))
    circuit_country_dict = dict(zip(circuits.circuitId, circuits.country))
    
    driver_dict = {}
    driver_info = {}
    for _, drv in drivers.iterrows():
        full_name = f"{drv['forename']} {drv['surname']}".upper()
        driver_dict[drv['driverId']] = full_name
        nat = str(drv['nationality']).strip()
        code = NATIONALITY_TO_CODE.get(nat, '')
        
        zespoly_kierowcy = driver_teams.get(drv['driverId'], [])
        driver_info[full_name] = {
            'Narodowosc': nat, 
            'Flaga_URL': f"https://flagcdn.com/24x18/{code}.png" if code else None, 
            'Data_Urodzenia': drv['dob'],
            'Wszystkie_Zespoly': ", ".join(zespoly_kierowcy) if len(zespoly_kierowcy) > 0 else "Brak danych"
        }

    races = races.sort_values(by=['year', 'round'])
    elo_quali, elo_sprint, elo_race, elo_overall, elo_tracks = {}, {}, {}, {}, {}
    track_seasons = {}
    
    history, track_history = [], []

    for _, race in races.iterrows():
        r_id, c_id = race['raceId'], race['circuitId']
        c_name = circuit_dict.get(c_id, f"Track {c_id}")
        c_country = circuit_country_dict.get(c_id, "Unknown")
        
        if c_id not in elo_tracks: 
            elo_tracks[c_id] = INITIAL_ELO
            track_seasons[c_id] = set()
            
        track_seasons[c_id].add(race['year'])

        quali_data = qualifying[qualifying['raceId'] == r_id]
        if not quali_data.empty:
            q_res = [{'driverId': row['driverId'], 'pos': row['position']} for _, row in quali_data.iterrows()]
            update_driver_elo(q_res, elo_quali, elo_overall, K_QUALI)
            
        sprint_data = sprint_results[sprint_results['raceId'] == r_id]
        if not sprint_data.empty:
            s_res = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in sprint_data.iterrows()]
            update_driver_elo(s_res, elo_sprint, elo_overall, K_SPRINT)
            
        race_data = results[results['raceId'] == r_id]
        if not race_data.empty:
            r_res = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in race_data.iterrows()]
            
            # ELO TORU
            current_race_elos = {d['driverId']: elo_overall.get(d['driverId'], INITIAL_ELO) for d in r_res}
            if current_race_elos:
                favorite_id = max(current_race_elos, key=current_race_elos.get)
                favorite_elo = current_race_elos[favorite_id]
                favorite_pos = next(d['pos'] for d in r_res if d['driverId'] == favorite_id)
                exp_track = get_expected_score(elo_tracks[c_id], favorite_elo)
                track_score = 1.0 if favorite_pos > 1 else 0.0
                elo_tracks[c_id] += K_TRACK * (track_score - exp_track)
            
            t_code = CIRCUIT_COUNTRY_TO_CODE.get(c_country, '')
            track_history.append({
                'Data': race['date'], 'Rok': race['year'], 'Tor': c_name, 'Kraj': c_country,
                'Flaga_URL': f"https://flagcdn.com/24x18/{t_code}.png" if t_code else None,
                'Sezony_Wystepowania': ", ".join(map(str, sorted(list(track_seasons[c_id])))),
                'Elo_Toru': round(elo_tracks[c_id], 1)
            })

            # AKTUALIZACJA KIEROWCÓW
            update_driver_elo(r_res, elo_race, elo_overall, K_RACE)
            
            for drv in r_res:
                d_id = drv['driverId']
                full_name = driver_dict.get(d_id, str(d_id))
                team_name = race_driver_team.get((r_id, d_id), "Unknown")
                nat = driver_info.get(full_name, {}).get('Narodowosc', '')
                
                history.append({
                    'Data': race['date'], 'Rok': race['year'], 'Dekada': f"{(race['year'] // 10) * 10}s",
                    'Runda': race['round'], 'Wyścig': race['name'], 'Kierowca': full_name, 
                    'Zespol': team_name, 'Narodowosc': nat,
                    'Elo_Kwalifikacje': round(elo_quali.get(d_id, INITIAL_ELO), 1),
                    'Elo_Sprint': round(elo_sprint.get(d_id, INITIAL_ELO), 1),
                    'Elo_Wyścig': round(elo_race.get(d_id, INITIAL_ELO), 1),
                    'Elo_Ogólne': round(elo_overall.get(d_id, INITIAL_ELO), 1)
                })

    # Reset indeksu ułatwi późniejsze używanie idxmax()
    return pd.DataFrame(history).reset_index(drop=True), pd.DataFrame.from_dict(driver_info, orient='index'), pd.DataFrame(track_history)

def update_driver_elo(event_results, specific_elo, overall_elo, k_factor):
    for drv in event_results:
        d_id = drv['driverId']
        if d_id not in specific_elo: specific_elo[d_id] = INITIAL_ELO
        if d_id not in overall_elo: overall_elo[d_id] = INITIAL_ELO
            
    changes_spec, changes_ovr = {d['driverId']: 0 for d in event_results}, {d['driverId']: 0 for d in event_results}
    
    for i in range(len(event_results)):
        for j in range(i + 1, len(event_results)):
            id_a, pos_a = event_results[i]['driverId'], event_results[i]['pos']
            id_b, pos_b = event_results[j]['driverId'], event_results[j]['pos']
            
            e_a_spec, e_b_spec = get_expected_score(specific_elo[id_a], specific_elo[id_b]), get_expected_score(specific_elo[id_b], specific_elo[id_a])
            e_a_ovr, e_b_ovr = get_expected_score(overall_elo[id_a], overall_elo[id_b]), get_expected_score(overall_elo[id_b], overall_elo[id_a])
            
            s_a = 1 if pos_a < pos_b else (0 if pos_a > pos_b else 0.5)
            s_b = 1 if pos_b < pos_a else (0 if pos_b > pos_a else 0.5)
            
            changes_spec[id_a] += k_factor * (s_a - e_a_spec)
            changes_spec[id_b] += k_factor * (s_b - e_b_spec)
            changes_ovr[id_a] += k_factor * (s_a - e_a_ovr)
            changes_ovr[id_b] += k_factor * (s_b - e_b_ovr)
            
    for d_id in changes_spec:
        specific_elo[d_id] += changes_spec[d_id]
        overall_elo[d_id] += changes_ovr[d_id]

@st.cache_data
def load_race_results_module():
    try:
        races = pd.read_csv('races.csv')
        results = pd.read_csv('results.csv')
        drivers = pd.read_csv('drivers.csv')
        constructors = pd.read_csv('constructors.csv')
        
        races = races.rename(columns={'name': 'race_name'})
        constructors = constructors.rename(columns={'name': 'team_name'})
        
        df = results.merge(races, on='raceId').merge(drivers, on='driverId').merge(constructors, on='constructorId')
        return df
    except:
        return pd.DataFrame()

# --- UI APP ---
lang_choice = st.sidebar.radio("Language / Język", ["Polski", "English"])
lang = 'Polski' if lang_choice == "Polski" else 'English'
L = T[lang]

st.title(L['title'])

with st.spinner(L['loading']):
    df_history, df_info, df_tracks = load_and_calculate_data()

if df_history is None:
    st.error(L['missing_files'])
    st.stop()

menu = st.sidebar.radio(L['nav'], [L['menu_race'], L['menu_peak'], L['menu_decades'], L['menu_profile'], L['menu_track'], L['menu_results']])

def display_driver_table(df, elo_col, show_year=False):
    if elo_col == 'Elo_Sprint': df = df[df['Elo_Sprint'] != INITIAL_ELO]
    
    # Tworzymy dynamiczną listę kolumn - wyrzucamy 'Narodowosc', bo flaga wystarczy
    cols = ['Flaga_URL', 'Kierowca']
    if 'Zespol' in df.columns: cols.append('Zespol')
    if show_year and 'Rok' in df.columns: cols.append('Rok')
    cols.append(elo_col)

    disp_df = df[cols].sort_values(elo_col, ascending=False).reset_index(drop=True)
    disp_df.index = disp_df.index + 1
    
    col_config = {
        "Flaga_URL": st.column_config.ImageColumn(L['country']),
        "Kierowca": st.column_config.TextColumn(L['driver']),
        "Zespol": st.column_config.TextColumn(L['team']),
        "Rok": st.column_config.NumberColumn(L['year'], format="%d"),
        elo_col: st.column_config.NumberColumn("Elo", format="%.1f")
    }
    
    st.dataframe(disp_df, column_config=col_config, height=600, use_container_width=True)

def get_peak_df(data_df, elo_type):
    # Pobiera dokładny moment (wiersz) z najwyższym wynikiem dla każdego zawodnika
    idx = data_df.groupby('Kierowca')[elo_type].idxmax()
    peak_df = data_df.loc[idx, ['Kierowca', 'Zespol', 'Rok', 'Narodowosc', elo_type]].copy()
    peak_df['Flaga_URL'] = peak_df['Kierowca'].apply(lambda x: df_info.loc[x, 'Flaga_URL'] if x in df_info.index else None)
    return peak_df

if menu == L['menu_race']:
    col_lata, col_wyscig = st.columns(2)
    with col_lata:
        dostepne_lata = sorted(df_history['Rok'].unique(), reverse=True)
        wybrany_rok = st.selectbox(L['select_season'], dostepne_lata)
    with col_wyscig:
        sezon_df = df_history[df_history['Rok'] == wybrany_rok].sort_values('Runda')
        dostepne_wyscigi = sezon_df['Wyścig'].unique()
        wybrany_wyscig = st.selectbox(L['select_race'], dostepne_wyscigi, index=len(dostepne_wyscigi)-1)
        
    wyniki_po_wyscigu = sezon_df[sezon_df['Wyścig'] == wybrany_wyscig].copy()
    wyniki_po_wyscigu['Flaga_URL'] = wyniki_po_wyscigu['Kierowca'].apply(lambda x: df_info.loc[x, 'Flaga_URL'] if x in df_info.index else None)

    with st.expander(L['filters']):
        c_nat, c_team = st.columns(2)
        with c_nat: sel_nat = st.multiselect(L['filter_nat'], sorted(wyniki_po_wyscigu['Narodowosc'].unique()))
        with c_team: sel_team = st.multiselect(L['filter_team'], sorted(wyniki_po_wyscigu['Zespol'].unique()))
        
    if sel_nat: wyniki_po_wyscigu = wyniki_po_wyscigu[wyniki_po_wyscigu['Narodowosc'].isin(sel_nat)]
    if sel_team: wyniki_po_wyscigu = wyniki_po_wyscigu[wyniki_po_wyscigu['Zespol'].isin(sel_team)]

    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader(f"{L['tables_after']} {wybrany_wyscig} ({wybrany_rok})")
        tab1, tab2, tab3, tab4 = st.tabs([L['overall'], L['race'], L['quali'], L['sprint']])
        with tab1: display_driver_table(wyniki_po_wyscigu, 'Elo_Ogólne')
        with tab2: display_driver_table(wyniki_po_wyscigu, 'Elo_Wyścig')
        with tab3: display_driver_table(wyniki_po_wyscigu, 'Elo_Kwalifikacje')
        with tab4: display_driver_table(wyniki_po_wyscigu, 'Elo_Sprint')

    with col2:
        st.subheader(L['form_chart'])
        elo_type = st.selectbox(L['elo_type'], ['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'])
        aktywni = sorted(sezon_df['Kierowca'].unique())
        sel_drv = st.multiselect(L['compare_drv'], aktywni, default=aktywni[:3] if len(aktywni)>=3 else aktywni)
        if sel_drv:
            fig = px.line(sezon_df[sezon_df['Kierowca'].isin(sel_drv)], x='Wyścig', y=elo_type, color='Kierowca', markers=True)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

elif menu == L['menu_peak']:
    st.header(L['peak_title'])
    st.markdown(L['peak_desc'])
    
    # Wyciągamy poprawne Peaki
    peak_overall = get_peak_df(df_history, 'Elo_Ogólne')
    peak_race = get_peak_df(df_history, 'Elo_Wyścig')
    peak_quali = get_peak_df(df_history, 'Elo_Kwalifikacje')

    with st.expander(L['filters']):
        c_nat, c_team = st.columns(2)
        with c_nat: sel_nat_p = st.multiselect(L['filter_nat'] + " ", sorted([n for n in peak_overall['Narodowosc'].unique() if pd.notna(n)]))
        with c_team: sel_team_p = st.multiselect(L['filter_team'] + " ", sorted([t for t in peak_overall['Zespol'].unique() if pd.notna(t)]))
        
    if sel_nat_p: 
        peak_overall = peak_overall[peak_overall['Narodowosc'].isin(sel_nat_p)]
        peak_race = peak_race[peak_race['Narodowosc'].isin(sel_nat_p)]
        peak_quali = peak_quali[peak_quali['Narodowosc'].isin(sel_nat_p)]
    if sel_team_p: 
        peak_overall = peak_overall[peak_overall['Zespol'].isin(sel_team_p)]
        peak_race = peak_race[peak_race['Zespol'].isin(sel_team_p)]
        peak_quali = peak_quali[peak_quali['Zespol'].isin(sel_team_p)]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(L['top_peak'])
        tab_p1, tab_p2, tab_p3 = st.tabs([L['overall'], L['race'], L['quali']])
        with tab_p1: display_driver_table(peak_overall, 'Elo_Ogólne', show_year=True)
        with tab_p2: display_driver_table(peak_race, 'Elo_Wyścig', show_year=True)
        with tab_p3: display_driver_table(peak_quali, 'Elo_Kwalifikacje', show_year=True)
    with col2:
        st.info(L['peak_info'])
        top_10 = peak_overall.nlargest(10, 'Elo_Ogólne')
        if not top_10.empty:
            fig_peak = px.bar(top_10, x='Kierowca', y='Elo_Ogólne', color='Elo_Ogólne', title="Top 10 z wybranych (Prime Form)", hover_data=['Zespol', 'Rok'])
            fig_peak.update_yaxes(range=[1500, top_10['Elo_Ogólne'].max() + 50])
            st.plotly_chart(fig_peak, use_container_width=True)

elif menu == L['menu_decades']:
    st.header(L['decades_title'])
    st.markdown(L['decades_desc'])
    
    dostepne_dekady = sorted(df_history['Dekada'].unique(), reverse=True)
    wybrana_dekada = st.selectbox(L['select_decade'], dostepne_dekady)
    
    # Filtrujemy historię tylko dla wybranej dekady
    df_dekady = df_history[df_history['Dekada'] == wybrana_dekada]
    
    peak_dec_overall = get_peak_df(df_dekady, 'Elo_Ogólne')
    peak_dec_race = get_peak_df(df_dekady, 'Elo_Wyścig')
    peak_dec_quali = get_peak_df(df_dekady, 'Elo_Kwalifikacje')
    
    st.subheader(f"🏆 {L['tables_after'].replace('po:', '')} {wybrana_dekada}")
    tab_d1, tab_d2, tab_d3 = st.tabs([L['overall'], L['race'], L['quali']])
    with tab_d1: display_driver_table(peak_dec_overall, 'Elo_Ogólne', show_year=True)
    with tab_d2: display_driver_table(peak_dec_race, 'Elo_Wyścig', show_year=True)
    with tab_d3: display_driver_table(peak_dec_quali, 'Elo_Kwalifikacje', show_year=True)

elif menu == L['menu_profile']:
    st.header(L['menu_profile'])
    
    with st.expander(L['filters'] + " (Ułatwia wyszukiwanie)"):
        c_nat, c_team = st.columns(2)
        nations = sorted([str(n) for n in df_info['Narodowosc'].unique() if pd.notna(n)])
        all_t = set()
        for t_str in df_info['Wszystkie_Zespoly'].dropna():
            if t_str != "Brak danych":
                for t in t_str.split(", "): all_t.add(t)
                
        with c_nat: sel_nat_prof = st.multiselect(L['filter_nat'] + "  ", nations)
        with c_team: sel_team_prof = st.multiselect(L['filter_team'] + "  ", sorted(list(all_t)))

    filtered_info = df_info.copy()
    if sel_nat_prof:
        filtered_info = filtered_info[filtered_info['Narodowosc'].isin(sel_nat_prof)]
    if sel_team_prof:
        def has_t(team_str):
            if pd.isna(team_str) or team_str == "Brak danych": return False
            teams = team_str.split(", ")
            return any(t in teams for t in sel_team_prof)
        filtered_info = filtered_info[filtered_info['Wszystkie_Zespoly'].apply(has_t)]

    driver_list = sorted(filtered_info.index.unique())
    
    if len(driver_list) == 0:
        st.warning("Brak wyników po filtracji.")
    else:
        selected_driver = st.selectbox(L['search_drv'], driver_list)
        if selected_driver:
            info = df_info.loc[selected_driver]
            driver_history = df_history[df_history['Kierowca'] == selected_driver]
            ostatnie = driver_history.sort_values('Data').tail(1).iloc[0]
            max_elo_row = driver_history.loc[driver_history['Elo_Ogólne'].idxmax()]
            min_elo_row = driver_history.loc[driver_history['Elo_Ogólne'].idxmin()]
            
            col_img, col_txt = st.columns([1, 15])
            with col_img:
                if info['Flaga_URL']: st.image(info['Flaga_URL'], width=60)
            with col_txt:
                st.markdown(f"## {selected_driver}")
                st.markdown(f"**{L['nat']}:** {info['Narodowosc']} | **{L['dob']}:** {info['Data_Urodzenia']}")
            st.markdown(f"🏎️ **{L['all_teams']}:** *{info['Wszystkie_Zespoly']}*")
            st.markdown("---")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric(L['last_elo'], ostatnie['Elo_Ogólne'])
            c2.metric(L['peak_max'], max_elo_row['Elo_Ogólne'], f"{max_elo_row['Rok']} {max_elo_row['Wyścig']} ({max_elo_row['Zespol']})", delta_color="normal")
            c3.metric(L['lowest_elo'], min_elo_row['Elo_Ogólne'], f"{min_elo_row['Rok']} {min_elo_row['Wyścig']}", delta_color="inverse")
            c4.metric(L['races_count'], len(driver_history))
            st.markdown("---")
            st.subheader(L['career_path'])
            melted_df = driver_history.melt(id_vars=['Data', 'Wyścig', 'Rok'], value_vars=['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'], var_name='Rodzaj_Elo', value_name='Wartość')
            melted_df = melted_df[~((melted_df['Rodzaj_Elo'] == 'Elo_Sprint') & (melted_df['Wartość'] == INITIAL_ELO))]
            fig2 = px.line(melted_df, x='Data', y='Wartość', color='Rodzaj_Elo', hover_data=['Wyścig', 'Rok'])
            st.plotly_chart(fig2, use_container_width=True)

elif menu == L['menu_track']:
    st.header(L['track_title'])
    st.markdown(L['track_desc'])
    ostatnie_tory = df_tracks.sort_values('Data').groupby('Tor').tail(1).sort_values('Elo_Toru', ascending=False).reset_index(drop=True)
    ostatnie_tory.index = ostatnie_tory.index + 1
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader(L['track_table'])
        st.dataframe(ostatnie_tory[['Flaga_URL', 'Tor', 'Kraj', 'Sezony_Wystepowania', 'Elo_Toru']], 
            column_config={
                "Flaga_URL": st.column_config.ImageColumn(L['country']),
                "Tor": st.column_config.TextColumn("Tor"),
                "Kraj": st.column_config.TextColumn(L['country']),
                "Sezony_Wystepowania": st.column_config.TextColumn(L['seasons']),
                "Elo_Toru": st.column_config.NumberColumn("Elo", format="%.1f")
            }, height=600, use_container_width=True)
    with col2:
        st.subheader(L['track_chart'])
        all_tracks = sorted(df_tracks['Tor'].unique())
        def_tracks = [t for t in ['Monaco Grand Prix', 'Belgian Grand Prix', 'Italian Grand Prix', 'Singapore Grand Prix'] if t in all_tracks]
        sel_tracks = st.multiselect("Porównaj tory / Compare tracks:", all_tracks, default=def_tracks)
        if sel_tracks:
            fig3 = px.line(df_tracks[df_tracks['Tor'].isin(sel_tracks)], x='Data', y='Elo_Toru', color='Tor', hover_data=['Rok'])
            st.plotly_chart(fig3, use_container_width=True)

elif menu == L['menu_results']:
    st.header(L['race_results_title'])
    df_res = load_race_results_module()
    
    if df_res.empty:
        st.error(L['missing_files'])
    else:
        col1, col2 = st.columns(2)
        with col1:
            dostepne_lata = sorted(df_res['year'].unique(), reverse=True)
            wybrany_rok = st.selectbox(L['select_season'] + " ", dostepne_lata)
        with col2:
            sezon_df = df_res[df_res['year'] == wybrany_rok].sort_values('round')
            dostepne_wyscigi = sezon_df['race_name'].unique() 
            wybrany_wyscig = st.selectbox(L['select_race'] + " ", dostepne_wyscigi)
            
        wyniki = sezon_df[sezon_df['race_name'] == wybrany_wyscig].sort_values('positionOrder')
        
        wyniki['Kierowca'] = wyniki.apply(lambda row: f"{row['forename']} {row['surname']}".upper(), axis=1)
        wyniki['Flaga_URL'] = wyniki['nationality'].apply(lambda nat: f"https://flagcdn.com/24x18/{NATIONALITY_TO_CODE.get(str(nat).strip(), '')}.png" if NATIONALITY_TO_CODE.get(str(nat).strip(), '') else None)
        
        display_results = wyniki[['positionOrder', 'Flaga_URL', 'Kierowca', 'team_name', 'points']].copy() 
        display_results.columns = [L['pos'], L['country'], L['driver'], L['team'], L['points']]
        display_results.set_index(L['pos'], inplace=True)
        
        st.dataframe(display_results, column_config={
            L['country']: st.column_config.ImageColumn(" "),
        }, height=700, use_container_width=True)
