import streamlit as st
import pandas as pd
import math

# --- CONFIGURARE ---
st.set_page_config(page_title="Predictor GG & Goluri", page_icon="⚽", layout="wide")

# CSS pentru tema Roșu-Alb (Modern & Simplu)
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    h1, h2, h3 {
        color: #e63946 !important; /* Roșu sportiv */
        font-family: 'Arial Black', sans-serif;
    }
    .main-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #e63946;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #e63946 !important;
        color: white !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        border: none !important;
        height: 3em;
    }
    .stProgress > div > div > div > div {
        background-color: #e63946;
    }
    label { color: #1d3557 !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# TOATE CAMPIONATELE (Update zilnic via Football-Data.co.uk)
CAMPIONATE = {
    "Anglia - Premier League": "E0",
    "Anglia - Championship": "E1",
    "Anglia - League 1": "E2",
    "Anglia - League 2": "E3",
    "Spania - La Liga": "SP1",
    "Spania - Segunda": "SP2",
    "Germania - Bundesliga": "D1",
    "Germania - Bundesliga 2": "D2",
    "Italia - Serie A": "I1",
    "Italia - Serie B": "I2",
    "Franța - Ligue 1": "F1",
    "Franța - Ligue 2": "F2",
    "Olanda - Eredivisie": "N1",
    "Belgia - Pro League": "B1",
    "Portugalia - Liga I": "P1",
    "Turcia - Super Lig": "T1",
    "Grecia - Super League": "G1",
    "Austria - Bundesliga": "A1",
    "Scoția - Premiership": "SC0"
}

@st.cache_data(ttl=3600) # Se reîmprospătează la fiecare oră
def incarca_date(cod, sezon):
    url = f"https://www.football-data.co.uk/mmz4281/{sezon}/{cod}.csv"
    try:
        df = pd.read_csv(url)
        df = df[['HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']].dropna()
        at_g = df.groupby('HomeTeam')['FTHG'].mean()
        at_o = df.groupby('AwayTeam')['FTAG'].mean()
        echipe = sorted(df['HomeTeam'].unique().astype(str))
        return {e: (at_g.get(e, 0) + at_o.get(e, 0)) / 2 for e in echipe}
    except: return None

def poisson(m, k):
    if m <= 0: return 0
    return (math.pow(m, k) * math.exp(-m)) / math.factorial(k)

# --- INTERFAȚĂ ---
st.title("⚽ PREDICTOR ZILNIC: GG & GOLURI")
st.write("Analiză bazată pe ultimele rezultate din baza de date globală.")

with st.sidebar:
    st.header("SELECȚIE")
    sezon = st.selectbox("Sezon", ["2425", "2526"], index=0)
    liga_nume = st.selectbox("Campionat", list(CAMPIONATE.keys()))

date = incarca_date(CAMPIONATE[liga_nume], sezon)

if date:
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: g = st.selectbox("Echipa Gazdă", list(date.keys()))
        with c2: o = st.selectbox("Echipa Oaspete", list(date.keys()))
        btn = st.button("CALCULEAZĂ PREDICȚIA")
        st.markdown('</div>', unsafe_allow_html=True)

    if btn and g != o:
        m_g, m_o = date[g], date[o]
        m_total = m_g + m_o
        
        # Calcul probabilități
        p_peste = (1 - sum([poisson(m_total, i) for i in range(3)])) * 100
        p_gg = (1 - poisson(m_g, 0)) * (1 - poisson(m_o, 0)) * 100

        # Afișare rezultate
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Șansă Peste 2.5 Goluri", f"{p_peste:.1f}%")
            st.progress(int(p_peste))
        with col_res2:
            st.metric("Șansă Ambele Marchează (GG)", f"{p_gg:.1f}%")
            st.progress(int(p_gg))

        st.divider()
        st.subheader("🎯 Cele mai probabile scoruri")
        scoruri = []
        for h in range(4):
            for a in range(4):
                prob = (poisson(m_g, h) * poisson(m_o, a)) * 100
                scoruri.append((f"{h} - {a}", prob))
        
        scoruri = sorted(scoruri, key=lambda x: x[1], reverse=True)[:3]
        s1, s2, s3 = st.columns(3)
        for i, (sc, pr) in enumerate(scoruri):
            [s1, s2, s3][i].warning(f"**{sc}** ({pr:.1f}%)")
    elif g == o:
        st.error("Selectează echipe diferite!")
else:
    st.error("Datele nu pot fi accesate momentan.")