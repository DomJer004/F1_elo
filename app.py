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
        'menu_race': "🏁 Wybór Wyścigu",
        'menu_peak': "👑 Ranking Wszech Czasów",
        'menu_profile': "👤 Profile Kierowców",
        'menu_track': "🛤️ Elo Torów (Trudność)",
        'missing_files': "Brakuje plików! Upewnij się, że masz: races, drivers, results, qualifying, sprint_results, constructors, circuits.",
        'loading': "Przeliczanie bazy danych i historii wyścigów...",
        'select_season': "Wybierz sezon:",
        'select_race': "Wybierz wyścig:",
        'tables_after': "🏆 Tabele po:",
        'overall': "Ogólne", 'race': "Wyścig", 'quali': "Kwalifikacje", 'sprint': "Sprint",
        'form_chart': "📈 Wykres formy w sezonie",
        'elo_type': "Rodzaj Elo:",
        'compare_drv': "Porównaj kierowców w tym roku:",
        'peak_title': "👑 Peak Elo - Ranking Wszech Czasów",
        'peak_desc': "Sprawdź, kto zanotował najwyższy, absolutny szczyt formy (Peak Elo) w całej historii Formuły 1.",
        'top_peak': "🌋 Najwyższe Peak Elo (Top 100)",
        'peak_info': "💡 **Czym jest Peak Elo?** To najwyższa wartość punktowa, jaką dany zawodnik wygenerował w dowolnym momencie swojej kariery, będąc w absolutnym 'prime'.",
        'search_drv': "Wyszukaj kierowcę (cała historia):",
        'nat': "Narodowość", 'dob': "Data ur.", 'all_teams': "Wszystkie zespoły w karierze",
        'last_elo': "Ostatnie Elo (Pożegnalne/Obecne)", 'peak_max': "PEAK Elo (Max)", 'lowest_elo': "Najniższe Elo (Min)", 'races_count': "Liczba wystąpień (GP)",
        'career_path': "📈 Przebieg kariery",
        'track_title': "🛤️ Ranking Torów F1 (Indeks Chaosu)",
        'track_desc': "Każdy tor 'walczy' z faworytem wyścigu. Jeśli faworyt (kierowca z najwyższym Elo) nie wygra wyścigu, tor zyskuje punkty. Im wyższe Elo toru, tym bardziej jest nieprzewidywalny i trudny!",
        'track_table': "Najbardziej bezlitosne tory (Top 50)",
        'track_chart': "📈 Ewolucja trudności toru"
    },
    'English': {
        'title': "🏎️ Formula 1 - Elo Rating Database",
        'nav': "Navigation",
        'menu_race': "🏁 Race Selection",
        'menu_peak': "👑 All-Time Peak Ranking",
        'menu_profile': "👤 Driver Profiles",
        'menu_track': "🛤️ Track Elo (Difficulty)",
        'missing_files': "Missing files! Ensure you have: races, drivers, results, qualifying, sprint_results, constructors, circuits.",
        'loading': "Calculating database and race history...",
        'select_season': "Select season:",
        'select_race': "Select race:",
        'tables_after': "🏆 Standings after:",
        'overall': "Overall", 'race': "Race", 'quali': "Qualifying", 'sprint': "Sprint",
        'form_chart': "📈 Season Form Chart",
        'elo_type': "Elo Type:",
        'compare_drv': "Compare drivers this year:",
        'peak_title': "👑 Peak Elo - All-Time Ranking",
        'peak_desc': "Check who reached the absolute highest peak form (Peak Elo) in the history of Formula 1.",
        'top_peak': "🌋 Highest Peak Elo (Top 100)",
        'peak_info': "💡 **What is Peak Elo?** It is the highest point value a driver generated at any point in their career, being in their absolute 'prime'.",
        'search_drv': "Search driver (all history):",
        'nat': "Nationality", 'dob': "Date of Birth", 'all_teams': "All career teams",
        'last_elo': "Last Elo (Current/Final)", 'peak_max': "PEAK Elo (Max)", 'lowest_elo': "Lowest Elo (Min)", 'races_count': "Race Entries (GP)",
        'career_path': "📈 Career Progression",
        'track_title': "🛤️ F1 Track Ranking (Chaos Index)",
        'track_desc': "Each track 'fights' the race favorite. If the favorite (driver with the highest Elo) fails to win, the track gains points. Higher Elo means a more unpredictable and difficult track!",
        'track_table': "Most unforgiving tracks (Top 50)",
        'track_chart': "📈 Track difficulty evolution"
    }
}

# --- SŁOWNIK FLAG ---
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
K_TRACK = 16.0 # Wyższy K dla torów, bo mają mniej "pojedynków"

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
        return None, None, None, None

    res_cons = results.merge(constructors, on='constructorId', suffixes=('', '_cons'))
    team_col_name = 'name_cons' if 'name_cons' in res_cons.columns else 'name'
    driver_teams = res_cons.groupby('driverId')[team_col_name].unique().to_dict()
    
    # Mapowanie torów
    circuit_dict = dict(zip(circuits.circuitId, circuits.name))
    
    driver_dict = {}
    driver_info = {}
    for _, drv in drivers.iterrows():
        full_name = f"{drv['forename']} {drv['surname']}".upper()
        driver_dict[drv['driverId']] = full_name
        nat = str(drv['nationality']).strip()
        code = NATIONALITY_TO_CODE.get(nat, '')
        flag_url = f"https://flagcdn.com/24x18/{code}.png" if code else None
        
        zespoly_kierowcy = driver_teams.get(drv['driverId'], [])
        driver_info[full_name] = {
            'Narodowosc': nat, 'Flaga_URL': flag_url, 'Data_Urodzenia': drv['dob'],
            'Wszystkie_Zespoly': ", ".join(zespoly_kierowcy) if len(zespoly_kierowcy) > 0 else "Brak danych"
        }

    races = races.sort_values(by=['year', 'round'])
    elo_quali, elo_sprint, elo_race, elo_overall = {}, {}, {}, {}
    elo_tracks = {} # Słownik dla Elo Torów
    
    history = []
    track_history = []

    for _, race in races.iterrows():
        r_id = race['raceId']
        c_id = race['circuitId']
        c_name = circuit_dict.get(c_id, f"Track {c_id}")
        
        if c_id not in elo_tracks: elo_tracks[c_id] = INITIAL_ELO

        # 1. Kwalifikacje
        quali_data = qualifying[qualifying['raceId'] == r_id]
        if not quali_data.empty:
            q_res = [{'driverId': row['driverId'], 'pos': row['position']} for _, row in quali_data.iterrows()]
            update_driver_elo(q_res, elo_quali, elo_overall, K_QUALI)
            
        # 2. Sprint
        sprint_data = sprint_results[sprint_results['raceId'] == r_id]
        if not sprint_data.empty:
            s_res = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in sprint_data.iterrows()]
            update_driver_elo(s_res, elo_sprint, elo_overall, K_SPRINT)
            
        # 3. Wyścig i Track Elo
        race_data = results[results['raceId'] == r_id]
        if not race_data.empty:
            r_res = [{'driverId': row['driverId'], 'pos': row['positionOrder']} for _, row in race_data.iterrows()]
            
            # --- OBLICZANIE ELO TORU ---
            # Kto był faworytem przed wyścigiem? (Najwyższe Elo Ogólne w stawce)
            current_race_elos = {d['driverId']: elo_overall.get(d['driverId'], INITIAL_ELO) for d in r_res}
            favorite_id = max(current_race_elos, key=current_race_elos.get)
            favorite_elo = current_race_elos[favorite_id]
            
            # Jak poszło faworytowi?
            favorite_pos = next(d['pos'] for d in r_res if d['driverId'] == favorite_id)
            
            exp_track = get_expected_score(elo_tracks[c_id], favorite_elo)
            # Tor dostaje 1 punkt (wygrywa), jeśli faworyt NIE ZAJĄŁ 1 miejsca
            track_score = 1.0 if favorite_pos > 1 else 0.0
            
            elo_tracks[c_id] += K_TRACK * (track_score - exp_track)
            
            track_history.append({
                'Data': race['date'], 'Rok': race['year'], 'Tor': c_name,
                'Elo_Toru': round(elo_tracks[c_id], 1)
            })
            # ---------------------------

            update_driver_elo(r_res, elo_race, elo_overall, K_RACE)
            
            for drv in r_res:
                d_id = drv['driverId']
                full_name = driver_dict.get(d_id, str(d_id))
                history.append({
                    'Data': race['date'], 'Rok': race['year'], 'Runda': race['round'],
                    'Wyścig': race['name'], 'Tor': c_name, 'Kierowca': full_name,
                    'Elo_Kwalifikacje': round(elo_quali.get(d_id, INITIAL_ELO), 1),
                    'Elo_Sprint': round(elo_sprint.get(d_id, INITIAL_ELO), 1),
                    'Elo_Wyścig': round(elo_race.get(d_id, INITIAL_ELO), 1),
                    'Elo_Ogólne': round(elo_overall.get(d_id, INITIAL_ELO), 1)
                })

    return pd.DataFrame(history), pd.DataFrame.from_dict(driver_info, orient='index'), pd.DataFrame(track_history)

def update_driver_elo(event_results, specific_elo, overall_elo, k_factor):
    for drv in event_results:
        d_id = drv['driverId']
        if d_id not in specific_elo: specific_elo[d_id] = INITIAL_ELO
        if d_id not in overall_elo: overall_elo[d_id] = INITIAL_ELO
            
    changes_spec = {drv['driverId']: 0 for drv in event_results}
    changes_ovr = {drv['driverId']: 0 for drv in event_results}
    
    for i in range(len(event_results)):
        for j in range(i + 1, len(event_results)):
            a, b = event_results[i], event_results[j]
            id_a, pos_a = a['driverId'], a['pos']
            id_b, pos_b = b['driverId'], b['pos']
            
            e_a_spec = get_expected_score(specific_elo[id_a], specific_elo[id_b])
            e_b_spec = get_expected_score(specific_elo[id_b], specific_elo[id_a])
            e_a_ovr = get_expected_score(overall_elo[id_a], overall_elo[id_b])
            e_b_ovr = get_expected_score(overall_elo[id_b], overall_elo[id_a])
            
            s_a = 1 if pos_a < pos_b else (0 if pos_a > pos_b else 0.5)
            s_b = 1 if pos_b < pos_a else (0 if pos_b > pos_a else 0.5)
            
            changes_spec[id_a] += k_factor * (s_a - e_a_spec)
            changes_spec[id_b] += k_factor * (s_b - e_b_spec)
            changes_ovr[id_a] += k_factor * (s_a - e_a_ovr)
            changes_ovr[id_b] += k_factor * (s_b - e_b_ovr)
            
    for d_id in changes_spec:
        specific_elo[d_id] += changes_spec[d_id]
        overall_elo[d_id] += changes_ovr[d_id]

# --- UI APP ---
lang_choice = st.sidebar.radio("Language / Język", ["Polski", "English"])
lang = 'Polski' if lang_choice == "Polski" else 'English'
L = T[lang] # Skrót do wybranego języka

st.title(L['title'])

with st.spinner(L['loading']):
    df_history, df_info, df_tracks = load_and_calculate_data()

if df_history is None:
    st.error(L['missing_files'])
    st.stop()

menu = st.sidebar.radio(L['nav'], [L['menu_race'], L['menu_peak'], L['menu_profile'], L['menu_track']])

def display_table(df, elo_col):
    if elo_col == 'Elo_Sprint': df = df[df['Elo_Sprint'] != INITIAL_ELO]
    disp_df = df[['Flaga_URL', 'Kierowca', elo_col]].sort_values(elo_col, ascending=False).reset_index(drop=True)
    disp_df.index = disp_df.index + 1
    st.dataframe(disp_df, column_config={"Flaga_URL": st.column_config.ImageColumn("Kraj"), "Kierowca": st.column_config.TextColumn("Kierowca"), elo_col: st.column_config.NumberColumn("Elo", format="%.1f")}, height=500, use_container_width=True)

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

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(f"{L['tables_after']} {wybrany_wyscig} ({wybrany_rok})")
        tab1, tab2, tab3, tab4 = st.tabs([L['overall'], L['race'], L['quali'], L['sprint']])
        with tab1: display_table(wyniki_po_wyscigu, 'Elo_Ogólne')
        with tab2: display_table(wyniki_po_wyscigu, 'Elo_Wyścig')
        with tab3: display_table(wyniki_po_wyscigu, 'Elo_Kwalifikacje')
        with tab4: display_table(wyniki_po_wyscigu, 'Elo_Sprint')

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
    
    peak_elo = df_history.groupby('Kierowca').agg({'Elo_Ogólne': 'max', 'Elo_Wyścig': 'max', 'Elo_Kwalifikacje': 'max'}).reset_index()
    peak_elo['Flaga_URL'] = peak_elo['Kierowca'].apply(lambda x: df_info.loc[x, 'Flaga_URL'] if x in df_info.index else None)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader(L['top_peak'])
        tab_p1, tab_p2, tab_p3 = st.tabs([L['overall'], L['race'], L['quali']])
        with tab_p1: display_table(peak_elo.nlargest(100, 'Elo_Ogólne'), 'Elo_Ogólne')
        with tab_p2: display_table(peak_elo.nlargest(100, 'Elo_Wyścig'), 'Elo_Wyścig')
        with tab_p3: display_table(peak_elo.nlargest(100, 'Elo_Kwalifikacje'), 'Elo_Kwalifikacje')

    with col2:
        st.info(L['peak_info'])
        top_10 = peak_elo.nlargest(10, 'Elo_Ogólne')
        fig_peak = px.bar(top_10, x='Kierowca', y='Elo_Ogólne', color='Elo_Ogólne', title="Top 10 (Prime Form)")
        fig_peak.update_yaxes(range=[1500, top_10['Elo_Ogólne'].max() + 50])
        st.plotly_chart(fig_peak, use_container_width=True)

elif menu == L['menu_profile']:
    st.header(L['menu_profile'])
    driver_list = sorted(df_info.index.unique())
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
        c2.metric(L['peak_max'], max_elo_row['Elo_Ogólne'], f"{max_elo_row['Rok']} {max_elo_row['Wyścig']}", delta_color="normal")
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
    
    # Wyciągamy ostatnie Elo dla każdego toru
    ostatnie_tory = df_tracks.sort_values('Data').groupby('Tor').tail(1).sort_values('Elo_Toru', ascending=False).reset_index(drop=True)
    ostatnie_tory.index = ostatnie_tory.index + 1
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(L['track_table'])
        st.dataframe(ostatnie_tory[['Tor', 'Elo_Toru']].head(50), height=500, use_container_width=True)
        
    with col2:
        st.subheader(L['track_chart'])
        all_tracks = sorted(df_tracks['Tor'].unique())
        # Wybieramy domyślnie kilka znanych torów
        def_tracks = [t for t in ['Monaco Grand Prix', 'Belgian Grand Prix', 'Italian Grand Prix', 'Singapore Grand Prix'] if t in all_tracks]
        sel_tracks = st.multiselect("Porównaj tory / Compare tracks:", all_tracks, default=def_tracks)
        
        if sel_tracks:
            fig3 = px.line(df_tracks[df_tracks['Tor'].isin(sel_tracks)], x='Data', y='Elo_Toru', color='Tor', hover_data=['Rok'])
            st.plotly_chart(fig3, use_container_width=True)
