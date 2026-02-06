import streamlit as st
import pandas as pd
import datetime
import os

# --- DATEI-LOGIK ---
DATA_FILE = "training_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['Datum'] = pd.to_datetime(df['Datum']).dt.date
        return df
    return pd.DataFrame(columns=['Datum', 'Workout_Name', 'Übung', 'Gewicht', 'Wiederholungen'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- APP CONFIG ---
st.set_page_config(page_title="Fitness Tracker", layout="centered", initial_sidebar_state="collapsed")

# CSS um das Seitenmenü für User fast "unsichtbar" zu machen
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- NAVIGATION OBEN ---
tab1, tab2 = st.tabs(["📈 Fortschritt", "🏋️ Training"])

# --- TAB 1: DASHBOARD ---
with tab1:
    st.title("Dein Fortschritt")
    if st.session_state.df.empty:
        st.info("Noch keine Daten vorhanden.")
    else:
        df = st.session_state.df
        df['Volumen'] = df['Gewicht'] * df['Wiederholungen']
        chart_data = df.groupby('Datum')['Volumen'].sum().reset_index()
        st.line_chart(chart_data.set_index('Datum'))

# --- TAB 2: TRAINING ---
with tab2:
    st.title("Trainings-Planer")
    
    # 1. Kalender-Auswahl
    selected_date = st.date_input("Wähle einen Tag:", datetime.date.today())
    
    # Checken, ob für diesen Tag schon ein Training existiert
    day_data = st.session_state.df[st.session_state.df['Datum'] == selected_date]
    
    if day_data.empty:
        st.warning(f"Kein Training am {selected_date}")
        workout_name = st.text_input("Wie soll das Training heißen?", placeholder="z.B. Leg Day")
        
        if st.button("Training für diesen Tag anlegen"):
            if workout_name:
                # Initialer Dummy-Eintrag oder einfach Start-Signal
                st.success(f"Training '{workout_name}' erstellt! Füge jetzt Übungen hinzu.")
                st.session_state['current_workout'] = workout_name
            else:
                st.error("Bitte gib einen Namen ein.")
    else:
        workout_name = day_data['Workout_Name'].iloc[0]
        st.success(f"Heute: **{workout_name}**")
        
        # 2. Übungen anzeigen/hinzufügen
        with st.expander("➕ Übung hinzufügen"):
            with st.form("add_exercise", clear_on_submit=True):
                ex_name = st.text_input("Übung")
                w = st.number_input("Gewicht (kg)", step=2.5)
                r = st.number_input("Reps", step=1)
                if st.form_submit_button("Speichern"):
                    new_row = pd.DataFrame([[selected_date, workout_name, ex_name, w, r]], 
                                          columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    save_data(st.session_state.df)
                    st.rerun()

        # 3. Liste der bereits gemachten Übungen an diesem Tag
        st.subheader("Heutige Übungen")
        for i, row in day_data.iterrows():
            st.write(f"**{row['Übung']}**: {row['Gewicht']}kg x {row['Wiederholungen']}")