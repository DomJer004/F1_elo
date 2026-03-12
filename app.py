import streamlit as st
import pandas as pd
import math
import plotly.express as px

st.set_page_config(page_title="F1 Zaawansowane Elo", layout="wide", page_icon="🏎️")

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
        st.error("Brakuje plików! Upewnij się, że masz pobrane z Kaggle/Ergast: races, drivers, results, qualifying, sprint_results, constructors.")
        return pd.DataFrame(), pd.DataFrame()

    res_cons = results.merge(constructors, on='constructorId', suffixes=('', '_cons'))
    team_col_name = 'name_cons' if 'name_cons' in res_cons.columns else 'name'
    
    # Tworzymy listę wszystkich zespołów dla każdego kierowcy
    driver_teams = res_cons.groupby('driverId')[team_col_name].unique().to_dict()
    
    driver_dict = {}
    driver_info = {}
    for _, drv in drivers.iterrows():
        full_name = f"{drv['forename']} {drv['surname']}".upper()
        driver_dict[drv['driverId']] = full_name
        
        # .strip() usuwa białe znaki, np. ukryte spacje w "Argentinian "
        nat = str(drv['nationality']).strip()
        code = NATIONALITY_TO_CODE.get(nat, '')
        flag_url = f"https://flagcdn.com/24x18/{code}.png" if code else None
        
        zespoly_kierowcy = driver_teams.get(drv['driverId'], [])
        
        driver_info[full_name] = {
            'Narodowosc': nat,
            'Flaga_URL': flag_url,
            'Data_Urodzenia': drv['dob'],
            'Wszystkie_Zespoly': ", ".join(zespoly_kierowcy) if len(zespoly_kierowcy) > 0 else "Brak danych",
            'Ostatni_Zespol': zespoly_kierowcy[-1] if len(zespoly_kierowcy) > 0 else "Brak danych"
        }

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
            
            # Zapisujemy stan Elo do historii PO KAŻDYM WYŚCIGU
            for drv in r_results:
                d_id = drv['driverId']
                full_name = driver_dict.get(d_id, str(d_id))
                history.append({
                    'Data': race['date'],
                    'Rok': race['year'],
                    'Runda': race['round'],
                    'Wyścig': race['name'],
                    'Kierowca': full_name,
                    'Elo_Kwalifikacje': round(elo_quali.get(d_id, INITIAL_ELO), 1),
                    'Elo_Sprint': round(elo_sprint.get(d_id, INITIAL_ELO), 1),
                    'Elo_Wyścig': round(elo_race.get(d_id, INITIAL_ELO), 1),
                    'Elo_Ogólne': round(elo_overall.get(d_id, INITIAL_ELO), 1)
                })

    return pd.DataFrame(history), pd.DataFrame.from_dict(driver_info, orient='index')

# --- FUNKCJA DO TABEL ---
def display_table(df, elo_col):
    if elo_col == 'Elo_Sprint':
        df = df[df['Elo_Sprint'] != INITIAL_ELO]
        
    disp_df = df[['Flaga_URL', 'Kierowca', elo_col]].sort_values(elo_col, ascending=False).reset_index(drop=True)
    disp_df.index = disp_df.index + 1
    
    st.dataframe(
        disp_df,
        column_config={
            "Flaga_URL": st.column_config.ImageColumn("Kraj"),
            "Kierowca": st.column_config.TextColumn("Kierowca"),
            elo_col: st.column_config.NumberColumn("Punkty Elo", format="%.1f")
        },
        height=500,
        use_container_width=True
    )

# --- ŁADOWANIE ---
with st.spinner("Przeliczanie bazy danych i historii wyścigów..."):
    df_history, df_info = load_and_calculate_data()

if df_history.empty:
    st.stop()

# --- MENU GŁÓWNE ---
st.title("🏎️ Formuła 1 - Baza Rankingowa Elo")
menu = st.sidebar.radio("Nawigacja", ["Wybór Wyścigu", "👑 Ranking Wszech Czasów", "Profile Kierowców"])

if menu == "Wybór Wyścigu":
    st.markdown("### 🏁 Sprawdź ranking po dowolnym wyścigu w historii")
    col_lata, col_wyscig = st.columns(2)
    
    with col_lata:
        dostepne_lata = sorted(df_history['Rok'].unique(), reverse=True)
        wybrany_rok = st.selectbox("Wybierz sezon:", dostepne_lata)
        
    with col_wyscig:
        sezon_df = df_history[df_history['Rok'] == wybrany_rok].sort_values('Runda')
        dostepne_wyscigi = sezon_df['Wyścig'].unique()
        # Domyślnie ustawiamy na ostatni wyścig w wybranym roku
        wybrany_wyscig = st.selectbox("Wybierz wyścig:", dostepne_wyscigi, index=len(dostepne_wyscigi)-1)
        
    # Wyciągamy ranking uformowany dokładnie po wybranym wyścigu
    wyniki_po_wyscigu = sezon_df[sezon_df['Wyścig'] == wybrany_wyscig].copy()
    wyniki_po_wyscigu['Flaga_URL'] = wyniki_po_wyscigu['Kierowca'].apply(
        lambda x: df_info.loc[x, 'Flaga_URL'] if x in df_info.index else None
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(f"🏆 Tabele po: {wybrany_wyscig} ({wybrany_rok})")
        tab1, tab2, tab3, tab4 = st.tabs(["Ogólne", "Wyścig", "Kwalifikacje", "Sprint"])
        with tab1: display_table(wyniki_po_wyscigu, 'Elo_Ogólne')
        with tab2: display_table(wyniki_po_wyscigu, 'Elo_Wyścig')
        with tab3: display_table(wyniki_po_wyscigu, 'Elo_Kwalifikacje')
        with tab4: display_table(wyniki_po_wyscigu, 'Elo_Sprint')

    with col2:
        st.subheader("📈 Wykres formy w sezonie")
        elo_type = st.selectbox("Rodzaj Elo:", ['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'])
        aktywni_w_sezonie = sorted(sezon_df['Kierowca'].unique())
        
        def_drv = aktywni_w_sezonie[:3] if len(aktywni_w_sezonie) >= 3 else aktywni_w_sezonie
        sel_drv = st.multiselect("Porównaj kierowców w tym roku:", aktywni_w_sezonie, default=def_drv)
        
        if sel_drv:
            fig = px.line(sezon_df[sezon_df['Kierowca'].isin(sel_drv)], 
                          x='Wyścig', y=elo_type, color='Kierowca', markers=True)
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

elif menu == "👑 Ranking Wszech Czasów":
    st.header("👑 Peak Elo - Ranking Wszech Czasów")
    st.markdown("Sprawdź, kto zanotował najwyższy, absolutny szczyt formy (Peak Elo) w całej historii Formuły 1.")
    
    # Obliczanie maksymalnego Elo kiedykolwiek zdobytego dla każdego kierowcy
    peak_elo = df_history.groupby('Kierowca').agg({
        'Elo_Ogólne': 'max',
        'Elo_Wyścig': 'max',
        'Elo_Kwalifikacje': 'max',
        'Elo_Sprint': 'max'
    }).reset_index()
    
    peak_elo['Flaga_URL'] = peak_elo['Kierowca'].apply(
        lambda x: df_info.loc[x, 'Flaga_URL'] if x in df_info.index else None
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🌋 Najwyższe Peak Elo (Top 100)")
        tab_p1, tab_p2, tab_p3 = st.tabs(["Peak Ogólny", "Peak Wyścigowy", "Peak Kwalifikacyjny"])
        
        with tab_p1: display_table(peak_elo.nlargest(100, 'Elo_Ogólne'), 'Elo_Ogólne')
        with tab_p2: display_table(peak_elo.nlargest(100, 'Elo_Wyścig'), 'Elo_Wyścig')
        with tab_p3: display_table(peak_elo.nlargest(100, 'Elo_Kwalifikacje'), 'Elo_Kwalifikacje')

    with col2:
        st.info("💡 **Czym jest Peak Elo?** To najwyższa wartość punktowa, jaką dany zawodnik wygenerował w dowolnym momencie swojej kariery, będąc w absolutnym 'prime'.")
        # Wykres top 10 Prime
        top_10 = peak_elo.nlargest(10, 'Elo_Ogólne')
        fig_peak = px.bar(top_10, x='Kierowca', y='Elo_Ogólne', color='Elo_Ogólne', 
                          title="Top 10 Kierowców Wszech Czasów (Prime Form)")
        fig_peak.update_yaxes(range=[1500, top_10['Elo_Ogólne'].max() + 50])
        st.plotly_chart(fig_peak, use_container_width=True)

elif menu == "Profile Kierowców":
    st.header("👤 Profile Kierowców")
    
    driver_list = sorted(df_info.index.unique())
    selected_driver = st.selectbox("Wyszukaj kierowcę (cała historia):", driver_list)
    
    if selected_driver:
        info = df_info.loc[selected_driver]
        driver_history = df_history[df_history['Kierowca'] == selected_driver]
        ostatnie = driver_history.sort_values('Data').tail(1).iloc[0]
        
        # Wyliczanie Max i Min
        max_elo_row = driver_history.loc[driver_history['Elo_Ogólne'].idxmax()]
        min_elo_row = driver_history.loc[driver_history['Elo_Ogólne'].idxmin()]
        liczba_wyscigow = len(driver_history)
        
        col_img, col_txt = st.columns([1, 15])
        with col_img:
            if info['Flaga_URL']: st.image(info['Flaga_URL'], width=60)
        with col_txt:
            st.markdown(f"## {selected_driver}")
            st.markdown(f"**Narodowość:** {info['Narodowosc']} | **Data ur.:** {info['Data_Urodzenia']}")
            
        st.markdown(f"🏎️ **Wszystkie zespoły w karierze:** *{info['Wszystkie_Zespoly']}*")
        
        # Super zaawansowane Kafelki
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ostatnie Elo (Pożegnalne/Obecne)", ostatnie['Elo_Ogólne'])
        c2.metric("PEAK Elo (Max)", max_elo_row['Elo_Ogólne'], f"{max_elo_row['Rok']} {max_elo_row['Wyścig']}", delta_color="normal")
        c3.metric("Najniższe Elo (Min)", min_elo_row['Elo_Ogólne'], f"{min_elo_row['Rok']} {min_elo_row['Wyścig']}", delta_color="inverse")
        c4.metric("Liczba wystąpień (GP)", liczba_wyscigow)
        
        st.markdown("---")
        st.subheader("📈 Przebieg kariery")
        
        melted_df = driver_history.melt(id_vars=['Data', 'Wyścig', 'Rok'], 
                                        value_vars=['Elo_Ogólne', 'Elo_Wyścig', 'Elo_Kwalifikacje', 'Elo_Sprint'],
                                        var_name='Rodzaj_Elo', value_name='Wartość')
        melted_df = melted_df[~((melted_df['Rodzaj_Elo'] == 'Elo_Sprint') & (melted_df['Wartość'] == INITIAL_ELO))]
        
        fig2 = px.line(melted_df, x='Data', y='Wartość', color='Rodzaj_Elo', hover_data=['Wyścig', 'Rok'])
        st.plotly_chart(fig2, use_container_width=True)
