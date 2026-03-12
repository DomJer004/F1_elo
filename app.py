import streamlit as st
import pandas as pd
import math
import plotly.express as px
import plotly.graph_objects as go

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
        'menu_results': "📊 Profile Wyścigów",
        'missing_files': "Brakuje plików! Upewnij się, że w folderze są: races, drivers, results, qualifying, sprint_results, constructors, circuits.",
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
        'team': "Zespół", 'nat': "Narodowość", 'country': " ", 'seasons': "Sezony", 'year': "Rok",
        'peak_title': "👑 Peak Elo - Ranking Wszech Czasów",
        'peak_desc': "Sprawdź, kto zanotował najwyższy, absolutny szczyt formy (Peak Elo) w całej historii Formuły 1. Zespół wskazuje, w jakich barwach kierowca osiągnął ten szczyt.",
        'top_peak': "🌋 Wszystkie wyniki (Pełny Ranking)",
        'peak_info': "💡 **Czym jest Peak Elo?** To najwyższa wartość punktowa, jaką dany zawodnik wygenerował w dowolnym momencie swojej kariery, będąc w absolutnym 'prime'.",
        'decades_title': "📅 Peak Elo - Najlepsi w Dekadach",
        'decades_desc': "Sprawdź, kto dominował w poszczególnych dziesięcioleciach. Algorytm wyszukuje najwyższe Elo osiągnięte przez kierowców w wybranym przedziale czasu.",
        'search_drv': "Wybierz kierowcę z listy:",
        'dob': "Data ur.", 'all_teams': "Wszystkie zespoły w karierze",
        'last_elo': "Ostatnie Elo (Pożegnalne/Obecne)", 'peak_max': "PEAK Elo (Max)", 'lowest_elo': "Najniższe Elo (Min)",
        'career_path': "📈 Przebieg kariery",
        'track_title': "🛤️ Ranking Torów F1 (Indeks Chaosu)",
        'track_desc': "Każdy tor 'walczy' z faworytem wyścigu. Jeśli faworyt (kierowca z najwyższym Elo) nie wygra wyścigu, tor zyskuje punkty. Im wyższe Elo toru, tym bardziej jest nieprzewidywalny i trudny!",
        'track_table': "Zestawienie torów (Ranking pełny)",
        'track_chart': "📈 Ewolucja trudności toru",
        'race_results_title': "📊 Profile Historycznych Sesji",
        'pos': "Poz.", 'points': "Punkty", 'driver': "Kierowca",
        'custom_stats': "📊 Wybierz statystyki do wyświetlenia:",
        'stat_starts': "Liczba startów (GP)", 'stat_wins': "Wygrane wyścigi", 'stat_podiums': "Miejsca na podium", 'stat_poles': "Pole Position",
        'race_profile_title': "🏆 Wizytówka Sesji",
        'winner': "🥇 1. Miejsce", 'second_place': "🥈 2. Miejsce", 'third_place': "🥉 3. Miejsce",
        'pole_pos': "⏱️ Pole Position:", 'fastest_lap': "🚀 Najszybsze okrążenie:", 'no_data_session': "Brak danych dla tej sesji w historycznej bazie.",
        'highlight_options': "✨ Zaznacz na wykresie:",
        'h_wins': "Zwycięstwa 🥇", 'h_podiums': "Podia 🏆", 'h_poles': "Pole Position ⏱️", 'h_fastest': "Najszybsze Okr. 🚀",
        'track_elo_drv_title': "🛤️ Ulubione Tory (Siła kierowcy na konkretnych obiektach)",
        'track_name': "Tor (W całej karierze)", 'track_elo': "Elo na tym torze"
    },
    'English': {
        'title': "🏎️ Formula 1 - Elo Rating Database",
        'nav': "Navigation",
        'menu_race': "🏁 Ranking after Race",
        'menu_peak': "👑 All-Time Peak Ranking",
        'menu_decades': "📅 Best of the Decades",
        'menu_profile': "👤 Driver Profiles",
        'menu_track': "🛤️ Track Elo (Difficulty)",
        'menu_results': "📊 Event Profiles",
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
        'team': "Team", 'nat': "Nationality", 'country': " ", 'seasons': "Seasons", 'year': "Year",
        'peak_title': "👑 Peak Elo - All-Time Ranking",
        'peak_desc': "Check who reached the absolute highest peak form (Peak Elo) in the history of Formula 1. The team indicates who they were driving for at that exact moment.",
        'top_peak': "🌋 All results (Full Ranking)",
        'peak_info': "💡 **What is Peak Elo?** It is the highest point value a driver generated at any point in their career, being in their absolute 'prime'.",
        'decades_title': "📅 Peak Elo - Best of the Decades",
        'decades_desc': "See who dominated in each decade. The algorithm finds the highest Elo achieved by drivers within the selected time frame.",
        'search_drv': "Select driver from the list:",
        'dob': "Date of Birth", 'all_teams': "All career teams",
        'last_elo': "Last Elo (Current/Final)", 'peak_max': "PEAK Elo (Max)", 'lowest_elo': "Lowest Elo (Min)",
        'career_path': "📈 Career Progression",
        'track_title': "🛤️ F1 Track Ranking (Chaos Index)",
        'track_desc': "Each track 'fights' the race favorite. If the favorite (driver with highest Elo) fails to win, the track gains points. Higher Elo means a more unpredictable and difficult track!",
        'track_table': "Track breakdown (Full Ranking)",
        'track_chart': "📈 Track difficulty evolution",
        'race_results_title': "📊 Historical Event Profiles",
        'pos': "Pos", 'points': "Points", 'driver': "Driver",
        'custom_stats': "📊 Select career stats to display:",
        'stat_starts': "Race Starts (GP)", 'stat_wins': "Race Wins", 'stat_podiums': "Podium Finishes", 'stat_poles': "Pole Positions",
        'race_profile_title': "🏆 Session Profile",
        'winner': "🥇 1st Place", 'second_place': "🥈 2nd Place", 'third_place': "🥉 3rd Place",
        'pole_pos': "⏱️ Pole Position:", 'fastest_lap': "🚀 Fastest Lap:", 'no_data_session': "No data available for this session in the database.",
        'highlight_options': "✨ Highlight on chart:",
        'h_wins': "Wins 🥇", 'h_podiums': "Podiums 🏆", 'h_poles': "Pole Position ⏱️", 'h_fastest': "Fastest Lap 🚀",
        'track_elo_drv_title': "🛤️ Best Tracks (Driver's strength on specific circuits)",
        'track_name': "Track (Career-wide)", 'track_elo': "Elo on this track"
    }
}

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
        return None, None, None, None

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
            'Wszystkie_Zespoly': ", ".join(zespoly_kierowcy) if len(zespoly_kierowcy) > 0 else "Brak danych",
            'Stat_Starts': 0, 'Stat_Wins': 0, 'Stat_Podiums': 0, 'Stat_Poles': 0
        }

    races = races.sort_values(by=['year', 'round'])
    elo_quali, elo_sprint, elo_race, elo_overall, elo_tracks = {}, {}, {}, {}, {}
    elo_driver_track = {} # NOWE: Elo kierowcy na konkretnym torze!
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

        poles_in_race = set()
        quali_data = qualifying[qualifying['raceId'] == r_id]
        if not quali_data.empty:
            q_res = []
            for _, row in quali_data.iterrows():
                pos = row['position']
                d_id = row['driverId']
                q_res.append({'driverId': d_id, 'pos': pos})
                if pos == 1:
                    poles_in_race.add(d_id)
                    fname = driver_dict.get(d_id)
                    if fname in driver_info: driver_info[fname]['Stat_Poles'] += 1
            update_driver_elo(q_res, elo_quali, elo_overall, K_QUALI)
            
        sprint_data = sprint_results[sprint_results['raceId'] == r_id]
        if not sprint_data.empty:
            s_res = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in sprint_data.iterrows()]
            update_driver_elo(s_res, elo_sprint, elo_overall, K_SPRINT)
            
        race_data = results[results['raceId'] == r_id]
        if not race_data.empty:
            r_res = []
            fastest_lap_driver = None
            if 'rank' in race_data.columns:
                fl_row = race_data[race_data['rank'].astype(str) == '1']
                if not fl_row.empty: fastest_lap_driver = fl_row.iloc[0]['driverId']

            for _, row in race_data.iterrows():
                pos = row['positionOrder']
                d_id = row['driverId']
                r_res.append({'driverId': d_id, 'pos': pos})
                fname = driver_dict.get(d_id)
                if fname in driver_info:
                    driver_info[fname]['Stat_Starts'] += 1
                    if pos == 1: driver_info[fname]['Stat_Wins'] += 1
                    if pos <= 3: driver_info[fname]['Stat_Podiums'] += 1

                # Ustawianie znaczników dla historii
                history.append({
                    'Data': race['date'], 'Rok': race['year'], 'Dekada': f"{(race['year'] // 10) * 10}s",
                    'Runda': race['round'], 'Wyścig': race['name'], 'Kierowca': fname, 
                    'Zespol': race_driver_team.get((r_id, d_id), "Unknown"), 'Narodowosc': driver_info.get(fname, {}).get('Narodowosc', ''),
                    'Is_Win': True if pos == 1 else False,
                    'Is_Podium': True if pos <= 3 else False,
                    'Is_Pole': True if d_id in poles_in_race else False,
                    'Is_Fastest': True if d_id == fastest_lap_driver else False,
                    'Elo_Kwalifikacje': 0, 'Elo_Sprint': 0, 'Elo_Wyścig': 0, 'Elo_Ogólne': 0 # Wypełnimy po update
                })

            # AKTUALIZACJA TRACK-SPECIFIC DRIVER ELO
            for d in r_res:
                if (d['driverId'], c_id) not in elo_driver_track:
                    elo_driver_track[(d['driverId'], c_id)] = INITIAL_ELO
            current_dt_elo = {d['driverId']: elo_driver_track[(d['driverId'], c_id)] for d in r_res}
            changes_dt = {d['driverId']: 0 for d in r_res}
            
            for i in range(len(r_res)):
                for j in range(i+1, len(r_res)):
                    a, b = r_res[i], r_res[j]
                    id_a, pos_a = a['driverId'], a['pos']
                    id_b, pos_b = b['driverId'], b['pos']
                    e_a = get_expected_score(current_dt_elo[id_a], current_dt_elo[id_b])
                    e_b = get_expected_score(current_dt_elo[id_b], current_dt_elo[id_a])
                    s_a = 1 if pos_a < pos_b else (0 if pos_a > pos_b else 0.5)
                    s_b = 1 if pos_b < pos_a else (0 if pos_b > pos_a else 0.5)
                    changes_dt[id_a] += K_RACE * (s_a - e_a)
                    changes_dt[id_b] += K_RACE * (s_b - e_b)
            for d_id in changes_dt:
                elo_driver_track[(d_id, c_id)] = current_dt_elo[d_id] + changes_dt[d_id]

            # ELO TORU (Względem faworyta)
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

            # AKTUALIZACJA GŁÓWNEGO ELO KIEROWCÓW
            update_driver_elo(r_res, elo_race, elo_overall, K_RACE)
            
            # Aktualizacja zapisanych wierszy history (ostatnie N elementów)
            for idx in range(len(history) - len(r_res), len(history)):
                hist_row = history[idx]
                fname = hist_row['Kierowca']
                # Odwrócony słownik dla driver_dict na szybko (wyszukiwanie ID po imieniu dla zapisu)
                d_id = next(k for k, v in driver_dict.items() if v == fname)
                hist_row['Elo_Kwalifikacje'] = round(elo_quali.get(d_id, INITIAL_ELO), 1)
                hist_row['Elo_Sprint'] = round(elo_sprint.get(d_id, INITIAL_ELO), 1)
                hist_row['Elo_Wyścig'] = round(elo_race.get(d_id, INITIAL_ELO), 1)
                hist_row['Elo_Ogólne'] = round(elo_overall.get(d_id, INITIAL_ELO), 1)

    # Przygotowanie DF dla Track-Specific Driver Elo
    drv_track_list = []
    for (d_id, c_id), elo_val in elo_driver_track.items():
        fname = driver_dict.get(d_id)
        cname = circuit_dict.get(c_id)
        if fname and cname:
            drv_track_list.append({
                'Kierowca': fname, 'Tor': cname, 'Flaga_URL': f"https://flagcdn.com/24x18/{CIRCUIT_COUNTRY_TO_CODE.get(circuit_country_dict.get(c_id, ''), '')}.png",
                'Elo_Toru_Dla_Kierowcy': round(elo_val, 1)
            })
    df_drv_track = pd.DataFrame(drv_track_list)

    return pd.DataFrame(history).reset_index(drop=True), pd.DataFrame.from_dict(driver_info, orient='index'), pd.DataFrame(track_history), df_drv_track

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
def load_event_profiles_data():
    try:
        races = pd.read_csv('races.csv').rename(columns={'name': 'race_name'})
        results = pd.read_csv('results.csv')
        qualifying = pd.read_csv('qualifying.csv')
        sprint = pd.read_csv('sprint_results.csv')
        drivers = pd.read_csv('drivers.csv').rename(columns={'nationality': 'driver_nationality'})
        constructors = pd.read_csv('constructors.csv').rename(columns={'name': 'team_name', 'nationality': 'constructor_nationality'})
        return races, results, qualifying, sprint, drivers, constructors
    except:
        return None, None, None, None, None, None

# --- UI APP ---
lang_choice = st.sidebar.radio("Language / Język", ["Polski", "English"])
lang = 'Polski' if lang_choice == "Polski" else 'English'
L = T[lang]

st.title(L['title'])

with st.spinner(L['loading']):
    df_history, df_info, df_tracks, df_drv_track = load_and_calculate_data()

if df_history is None:
    st.error(L['missing_files'])
    st.stop()

menu = st.sidebar.radio(L['nav'], [L['menu_race'], L['menu_peak'], L['menu_decades'], L['menu_profile'], L['menu_track'], L['menu_results']])

def display_driver_table(df, elo_col, show_year=False):
    if elo_col == 'Elo_Sprint': df = df[df['Elo_Sprint'] != INITIAL_ELO]
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
    
    peak_overall = get_peak_df(df_history, 'Elo_Ogólne')
    peak_race = get_peak_df(df_history, 'Elo_Wyścig')
    peak_quali = get_peak_df(df_history, 'Elo_Kwalifikacje')

    with st.expander(L['filters']):
        c_nat, c_team = st.columns(2)
        with c_nat: sel_nat_p = st.multiselect(L['filter_nat'] + " ", sorted([n for n in peak_overall['Narodowosc'].unique() if pd.notna(n)]))
        with c_team: sel_team_p = st.multiselect(L['filter_team'] + " ", sorted([t for t in peak_overall['Zespol'].unique() if pd.notna(t)]))
    if sel_nat_p: 
        peak_overall, peak_race, peak_quali = peak_overall[peak_overall['Narodowosc'].isin(sel_nat_p)], peak_race[peak_race['Narodowosc'].isin(sel_nat_p)], peak_quali[peak_quali['Narodowosc'].isin(sel_nat_p)]
    if sel_team_p: 
        peak_overall, peak_race, peak_quali = peak_overall[peak_overall['Zespol'].isin(sel_team_p)], peak_race[peak_race['Zespol'].isin(sel_team_p)], peak_quali[peak_quali['Zespol'].isin(sel_team_p)]
    
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
    if sel_nat_prof: filtered_info = filtered_info[filtered_info['Narodowosc'].isin(sel_nat_prof)]
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
                if info['Flaga_URL']: st.image(info['Flaga_URL'], width=80)
            with col_txt:
                st.markdown(f"## {selected_driver}")
                st.markdown(f"**{L['dob']}:** {info['Data_Urodzenia']}")
            st.markdown(f"🏎️ **{L['all_teams']}:** *{info['Wszystkie_Zespoly']}*")
            st.markdown("---")
            
            st.markdown(f"### {L['custom_stats']}")
            stat_options = {L['stat_starts']: info['Stat_Starts'], L['stat_wins']: info['Stat_Wins'], L['stat_podiums']: info['Stat_Podiums'], L['stat_poles']: info['Stat_Poles']}
            selected_stats = st.multiselect(" ", list(stat_options.keys()), default=[L['stat_starts'], L['stat_wins'], L['stat_podiums']])
            if selected_stats:
                stat_cols = st.columns(len(selected_stats))
                for i, stat_name in enumerate(selected_stats):
                    stat_cols[i].metric(stat_name, stat_options[stat_name])
            
            st.markdown("---")
            tab_hist, tab_track = st.tabs([L['career_path'], L['track_elo_drv_title']])
            
            with tab_hist:
                c1, c2, c3 = st.columns(3)
                c1.metric(L['last_elo'], ostatnie['Elo_Ogólne'])
                c2.metric(L['peak_max'], max_elo_row['Elo_Ogólne'], f"{max_elo_row['Rok']} {max_elo_row['Wyścig']} ({max_elo_row['Zespol']})", delta_color="normal")
                c3.metric(L['lowest_elo'], min_elo_row['Elo_Ogólne'], f"{min_elo_row['Rok']} {min_elo_row['Wyścig']}", delta_color="inverse")
                
                st.markdown(f"**{L['highlight_options']}**")
                c_h1, c_h2, c_h3, c_h4 = st.columns(4)
                with c_h1: show_wins = st.checkbox(L['h_wins'])
                with c_h2: show_podiums = st.checkbox(L['h_podiums'])
                with c_h3: show_poles = st.checkbox(L['h_poles'])
                with c_h4: show_fls = st.checkbox(L['h_fastest'])

                melted_df = driver_history.melt(id_vars=['Data', 'Wyścig', 'Rok', 'Is_Win', 'Is_Podium', 'Is_Pole', 'Is_Fastest'], value_vars=['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'], var_name='Rodzaj_Elo', value_name='Wartość')
                melted_df = melted_df[~((melted_df['Rodzaj_Elo'] == 'Elo_Sprint') & (melted_df['Wartość'] == INITIAL_ELO))]
                
                fig2 = px.line(melted_df, x='Data', y='Wartość', color='Rodzaj_Elo', hover_data=['Wyścig', 'Rok'])
                
                # Dodawanie znaczników punktowych
                if show_wins:
                    wins_df = melted_df[melted_df['Is_Win'] & (melted_df['Rodzaj_Elo'] == 'Elo_Ogólne')]
                    fig2.add_trace(go.Scatter(x=wins_df['Data'], y=wins_df['Wartość'], mode='markers', marker=dict(symbol='star', size=12, color='gold'), name=L['h_wins']))
                if show_podiums:
                    pod_df = melted_df[melted_df['Is_Podium'] & (melted_df['Rodzaj_Elo'] == 'Elo_Ogólne')]
                    fig2.add_trace(go.Scatter(x=pod_df['Data'], y=pod_df['Wartość'], mode='markers', marker=dict(symbol='circle', size=8, color='silver'), name=L['h_podiums']))
                if show_poles:
                    pol_df = melted_df[melted_df['Is_Pole'] & (melted_df['Rodzaj_Elo'] == 'Elo_Kwalifikacje')]
                    fig2.add_trace(go.Scatter(x=pol_df['Data'], y=pol_df['Wartość'], mode='markers', marker=dict(symbol='diamond', size=10, color='purple'), name=L['h_poles']))
                if show_fls:
                    fls_df = melted_df[melted_df['Is_Fastest'] & (melted_df['Rodzaj_Elo'] == 'Elo_Wyścig')]
                    fig2.add_trace(go.Scatter(x=fls_df['Data'], y=fls_df['Wartość'], mode='markers', marker=dict(symbol='triangle-up', size=10, color='red'), name=L['h_fastest']))

                st.plotly_chart(fig2, use_container_width=True)
                
            with tab_track:
                driver_tracks = df_drv_track[df_drv_track['Kierowca'] == selected_driver].sort_values('Elo_Toru_Dla_Kierowcy', ascending=False).reset_index(drop=True)
                driver_tracks.index = driver_tracks.index + 1
                
                st.dataframe(driver_tracks[['Flaga_URL', 'Tor', 'Elo_Toru_Dla_Kierowcy']], 
                    column_config={
                        "Flaga_URL": st.column_config.ImageColumn(L['country']),
                        "Tor": st.column_config.TextColumn(L['track_name']),
                        "Elo_Toru_Dla_Kierowcy": st.column_config.NumberColumn(L['track_elo'], format="%.1f")
                    }, height=500, use_container_width=True)

elif menu == L['menu_track']:
    st.header(L['track_title'])
    st.markdown(L['track_desc'])
    ostatnie_tory = df_tracks.sort_values('Data').groupby('Tor').tail(1).sort_values('Elo_Toru', ascending=False).reset_index(drop=True)
    ostatnie_tory.index = ostatnie_tory.index + 1
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader(L['track_table'])
        st.dataframe(ostatnie_tory[['Flaga_URL', 'Tor', 'Sezony_Wystepowania', 'Elo_Toru']], 
            column_config={
                "Flaga_URL": st.column_config.ImageColumn(L['country']),
                "Tor": st.column_config.TextColumn("Tor"),
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
    races_df, res_df, qual_df, sprint_df, drv_df, cons_df = load_event_profiles_data()
    
    if races_df is None:
        st.error(L['missing_files'])
    else:
        valid_race_ids = res_df['raceId'].unique()
        valid_races = races_df[races_df['raceId'].isin(valid_race_ids)]
        
        col1, col2 = st.columns(2)
        with col1:
            dostepne_lata = sorted(valid_races['year'].unique(), reverse=True)
            wybrany_rok = st.selectbox(L['select_season'] + " ", dostepne_lata)
        with col2:
            sezon_df = valid_races[valid_races['year'] == wybrany_rok].sort_values('round')
            dostepne_wyscigi = sezon_df['race_name'].unique() 
            wybrany_wyscig = st.selectbox(L['select_race'] + " ", dostepne_wyscigi)
            
        r_id = sezon_df[sezon_df['race_name'] == wybrany_wyscig].iloc[0]['raceId']
        
        def format_event_table(df, pos_col, show_points=False):
            df = df.merge(drv_df, on='driverId').merge(cons_df, on='constructorId')
            df['Kierowca'] = df.apply(lambda row: f"{row['forename']} {row['surname']}".upper(), axis=1)
            df['Flaga_URL'] = df['driver_nationality'].apply(
                lambda nat: f"https://flagcdn.com/24x18/{NATIONALITY_TO_CODE.get(str(nat).strip(), '')}.png" if NATIONALITY_TO_CODE.get(str(nat).strip(), '') else None
            )
            df = df.sort_values(pos_col)
            cols_to_keep = [pos_col, 'Flaga_URL', 'Kierowca', 'team_name']
            final_cols = [L['pos'], L['country'], L['driver'], L['team']]
            if show_points and 'points' in df.columns:
                cols_to_keep.append('points')
                final_cols.append(L['points'])
            if 'q1' in df.columns:
                cols_to_keep.extend(['q1', 'q2', 'q3'])
                final_cols.extend(['Q1', 'Q2', 'Q3'])
                
            display_df = df[cols_to_keep].copy()
            display_df.columns = final_cols
            display_df.set_index(L['pos'], inplace=True)
            return display_df

        def get_driver_name(d_id):
            d_row = drv_df[drv_df['driverId'] == d_id].iloc[0]
            return f"{d_row['forename']} {d_row['surname']}".upper()

        tab_r, tab_q, tab_s = st.tabs([f"🏁 {L['race']}", f"⏱️ {L['quali']}", f"🏎️ {L['sprint']}"])
        
        with tab_r:
            r_data = res_df[res_df['raceId'] == r_id].copy()
            if r_data.empty: st.info(L['no_data_session'])
            else:
                r_data = r_data.sort_values('positionOrder')
                podium = r_data.head(3)
                p1 = podium.iloc[0]['driverId'] if len(podium) > 0 else None
                p2 = podium.iloc[1]['driverId'] if len(podium) > 1 else None
                p3 = podium.iloc[2]['driverId'] if len(podium) > 2 else None
                
                fl_driver, fl_time = None, ""
                if 'rank' in r_data.columns:
                    fl_row = r_data[r_data['rank'].astype(str) == '1']
                    if not fl_row.empty:
                        fl_driver = fl_row.iloc[0]['driverId']
                        ft = fl_row.iloc[0].get('fastestLapTime', "")
                        fl_time = f" ({ft})" if pd.notna(ft) and str(ft).strip() not in ['nan', 'NaN', '\\N'] else ""
                        
                pole_driver = None
                if 'grid' in r_data.columns:
                    pole_row = r_data[r_data['grid'] == 1]
                    if not pole_row.empty: pole_driver = pole_row.iloc[0]['driverId']
                
                st.markdown(f"### {L['race_profile_title']}")
                c1, c2, c3 = st.columns(3)
                if p1: c2.markdown(f"#### {L['winner']}\n**{get_driver_name(p1)}**")
                if p2: c1.markdown(f"#### {L['second_place']}\n**{get_driver_name(p2)}**")
                if p3: c3.markdown(f"#### {L['third_place']}\n**{get_driver_name(p3)}**")
                st.markdown("---")
                c4, c5 = st.columns(2)
                if pole_driver: c4.markdown(f"**{L['pole_pos']}** {get_driver_name(pole_driver)}")
                if fl_driver: c5.markdown(f"**{L['fastest_lap']}** {get_driver_name(fl_driver)}{fl_time}")
                st.markdown("---")
                disp_df = format_event_table(r_data, 'positionOrder', show_points=True)
                st.dataframe(disp_df, column_config={L['country']: st.column_config.ImageColumn(" ")}, height=500, use_container_width=True)

        with tab_q:
            q_data = qual_df[qual_df['raceId'] == r_id].copy()
            if q_data.empty: st.info(L['no_data_session'])
            else:
                q_data = q_data.sort_values('position')
                p1 = q_data.iloc[0]['driverId'] if len(q_data) > 0 else None
                st.markdown(f"### {L['race_profile_title']}")
                if p1: st.markdown(f"#### {L['winner']}\n**{get_driver_name(p1)}**")
                st.markdown("---")
                disp_df = format_event_table(q_data, 'position', show_points=False)
                st.dataframe(disp_df, column_config={L['country']: st.column_config.ImageColumn(" ")}, height=500, use_container_width=True)

        with tab_s:
            s_data = sprint_df[sprint_df['raceId'] == r_id].copy()
            if s_data.empty: st.info(L['no_data_session'])
            else:
                s_data = s_data.sort_values('positionOrder')
                podium = s_data.head(3)
                p1 = podium.iloc[0]['driverId'] if len(podium) > 0 else None
                p2 = podium.iloc[1]['driverId'] if len(podium) > 1 else None
                p3 = podium.iloc[2]['driverId'] if len(podium) > 2 else None
                st.markdown(f"### {L['race_profile_title']}")
                c1, c2, c3 = st.columns(3)
                if p1: c2.markdown(f"#### {L['winner']}\n**{get_driver_name(p1)}**")
                if p2: c1.markdown(f"#### {L['second_place']}\n**{get_driver_name(p2)}**")
                if p3: c3.markdown(f"#### {L['third_place']}\n**{get_driver_name(p3)}**")
                st.markdown("---")
                disp_df = format_event_table(s_data, 'positionOrder', show_points=True)
                st.dataframe(disp_df, column_config={L['country']: st.column_config.ImageColumn(" ")}, height=500, use_container_width=True)
