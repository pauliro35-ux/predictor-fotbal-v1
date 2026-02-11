import streamlit as st
import pandas as pd
import math

# --- 1. CONFIGURARE PENTRU MOBIL & PWA ---
st.set_page_config(
    page_title="Predictor Pro GG", 
    page_icon="⚽", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Meta-tag-uri pentru a forța browserul să se comporte ca o aplicație nativă
st.markdown("""
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="theme-color" content="#e63946">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    </head>
    <style>
        /* Fundal și fonturi */
        .stApp { background-color: #ffffff; }
        
        /* Header stilizat */
        .main-header {
            background-color: #e63946;
            color: white;
            padding: 15px;
            border-radius: 0 0 15px 15px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* Carduri rezultate */
        .main-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 12px;
            border-top: 5px solid #e63946;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 15px;
        }

        /* Buton Mare de Mobil */
        .stButton>button {
            width: 100% !important;
            background-color: #e63946 !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            height: 3.5em !important;
            font-size: 1.1rem !important;
            border: none !important;
            box-shadow: 0 4px 10px rgba(230, 57, 70, 0.3);
        }

        /* Metricile compacte */
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            color: #e63946 !important;
        }

        /* Eliminare spații inutile pe mobil */
        .block-container { padding-top: 1rem !important; }
        footer {display: none !important;}
        #MainMenu {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. BAZA DE DATE LIGI ---
CAMPIONATE = {
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Anglia - Premier League": "E0",
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Anglia - Championship": "E1",
    "🇪🇸 Spania - La Liga": "SP1",
    "🇮🇹 Italia - Serie A": "I1",
    "🇩🇪 Germania - Bundesliga": "D1",
    "🇫🇷 Franța - Ligue 1": "F1",
    "🇳🇱 Olanda - Eredivisie": "N1",
    "🇧🇪 Belgia - Pro League": "B1",
    "🇵🇹 Portugalia - Liga I": "P1",
    "🇹🇷 Turcia - Super Lig": "T1",
    "🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scoția - Premiership": "SC0",
    "🇦🇹 Austria - Bundesliga": "A1",
    "🇬🇷 Grecia - Super League": "G1"
}

@st.cache_data(ttl=3600)
def incarca_date(cod, sezon):
    url = f"https://www.football-data.co.uk/mmz4281/{sezon}/{cod}.csv"
    try:
        df = pd.read_csv(url)
        df = df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
        at_g = df.groupby('HomeTeam')['FTHG'].mean()
        at_o = df.groupby('AwayTeam')['FTAG'].mean()
        echipe = sorted(df['HomeTeam'].unique().astype(str))
        return {e: (at_g.get(e, 0) + at_o.get(e, 0)) / 2 for e in echipe}
    except:
        return None

def poisson(m, k):
    if m <= 0: return 0
    return (math.pow(m, k) * math.exp(-m)) / math.factorial(k)

# --- 3. INTERFAȚĂ ---
st.markdown('<div class="main-header"><h1>PREDICTOR GOAL ⚽</h1></div>', unsafe_allow_html=True)

# Sidebar pentru setări (ascuns default pe mobil)
with st.sidebar:
    st.subheader("⚙️ Configurare")
    sezon = st.selectbox("Alege Sezonul", ["2425", "2526"], index=0)
    liga_nume = st.selectbox("Campionat", list(CAMPIONATE.keys()))
    st.info("Datele se actualizează automat la fiecare oră.")

date = incarca_date(CAMPIONATE[liga_nume], sezon)

if date:
    # Container Selecție Echipe
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    g = st.selectbox("🏠 Echipa Gazdă", list(date.keys()))
    o = st.selectbox("🚀 Echipa Oaspete", list(date.keys()))
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("CALCULEAZĂ PREDICȚIA"):
        if g == o:
            st.error("Selectează echipe diferite!")
        else:
            m_g, m_o = date[g], date[o]
            m_total = m_g + m_o
            
            # Calcul Probabilități
            p_peste = (1 - sum([poisson(m_total, i) for i in range(3)])) * 100
            p_gg = (1 - poisson(m_g, 0)) * (1 - poisson(m_o, 0)) * 100

            # Afișare Metrică GG și Goluri
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Peste 2.5", f"{p_peste:.1f}%")
                st.progress(min(int(p_peste), 100))
            with col2:
                st.metric("Șansă GG", f"{p_gg:.1f}%")
                st.progress(min(int(p_gg), 100))

            st.write("---")
            
            # Scoruri Probabile stilizate pentru mobil
            st.subheader("🎯 Profeții Scor")
            scoruri = []
            for h in range(4):
                for a in range(4):
                    prob = (poisson(m_g, h) * poisson(m_o, a)) * 100
                    scoruri.append((f"{h} - {a}", prob))
            
            scoruri = sorted(scoruri, key=lambda x: x[1], reverse=True)[:3]
