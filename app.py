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

if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- TABS ---
tab1, tab2 = st.tabs(["📈 Fortschritt", "🏋️ Training"])

with tab1:
    st.title("Dein Fortschritt")
    if not st.session_state.df.empty:
        df = st.session_state.df.copy()
        chart_df = df[df['Übung'] != "Start"].copy()
        if not chart_df.empty:
            chart_df['Volumen'] = pd.to_numeric(chart_df['Gewicht']) * pd.to_numeric(chart_df['Wiederholungen'])
            chart_data = chart_df.groupby('Datum')['Volumen'].sum().reset_index()
            st.line_chart(chart_data.set_index('Datum'))
        else:
            st.info("Füge Übungen hinzu, um Fortschritte zu sehen.")

with tab2:
    st.title("Trainings-Planer")
    selected_date = st.date_input("Tag wählen", datetime.date.today())
    
    # Daten für diesen Tag
    day_data = st.session_state.df[st.session_state.df['Datum'] == selected_date]

    # --- NEUES PROGRAMM HINZUFÜGEN ---
    with st.expander("🆕 Neues Programm hinzufügen (z.B. Bizeps)", expanded=False):
        new_prog_name = st.text_input("Name des Programms")
        if st.button("Programm erstellen"):
            if new_prog_name:
                # Prüfen ob Programm am Tag schon existiert
                if not ((st.session_state.df['Datum'] == selected_date) & 
                        (st.session_state.df['Workout_Name'] == new_prog_name)).any():
                    new_row = pd.DataFrame([[selected_date, new_prog_name, "Start", 0, 0]], 
                                          columns=st.session_state.df.columns)
                    st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                    save_data(st.session_state.df)
                    st.rerun()

    st.write("---")

    # --- ANZEIGE DER PROGRAMME ---
    if not day_data.empty:
        programs = day_data['Workout_Name'].unique()
        
        for prog in programs:
            st.subheader(f"📂 {prog}")
            
            # Übungen für dieses spezifische Programm filtern
            prog_exercises = day_data[(day_data['Workout_Name'] == prog) & (day_data['Übung'] != "Start")]
            
            # Formular für neue Übung in diesem Programm
            with st.expander(f"➕ Übung zu '{prog}' hinzufügen"):
                with st.form(f"form_{prog}", clear_on_submit=True):
                    ex_name = st.text_input("Übung")
                    c1, c2 = st.columns(2)
                    w = c1.number_input("Gewicht (kg)", step=2.5, key=f"w_{prog}")
                    r = c2.number_input("Reps", step=1, key=f"r_{prog}")
                    
                    if st.form_submit_button("Speichern"):
                        if ex_name:
                            new_ex = pd.DataFrame([[selected_date, prog, ex_name, w, r]], 
                                                 columns=st.session_state.df.columns)
                            # Start-Platzhalter für dieses Programm entfernen
                            st.session_state.df = st.session_state.df[~((st.session_state.df['Datum'] == selected_date) & 
                                                                       (st.session_state.df['Workout_Name'] == prog) & 
                                                                       (st.session_state.df['Übung'] == "Start"))]
                            st.session_state.df = pd.concat([st.session_state.df, new_ex], ignore_index=True)
                            save_data(st.session_state.df)
                            st.rerun()
            
            # Übungen auflisten
            for i, row in prog_exercises.iterrows():
                cols = st.columns([4, 1])
                with cols[0]:
                    st.info(f"**{row['Übung']}**: {row['Gewicht']}kg x {row['Wiederholungen']}")
                with cols[1]:
                    if st.button("🗑️", key=f"del_{row.name}"): # row.name ist der echte Index im großen DF
                        st.session_state.df = st.session_state.df.drop(i)
                        save_data(st.session_state.df)
                        st.rerun()
            st.write("") # Abstand zwischen Programmen
    else:
        st.info("Noch kein Programm für heute angelegt.")