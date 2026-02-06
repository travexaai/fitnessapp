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
        # Nur echte Übungen für den Chart nutzen
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

    if day_data.empty:
        st.info(f"Noch kein Training am {selected_date}")
        w_name = st.text_input("Name des Trainings (z.B. Brust)", key="new_w_name")
        
        if st.button("Training erstellen"):
            if w_name:
                new_row = pd.DataFrame([[selected_date, w_name, "Start", 0, 0]], 
                                      columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df)
                st.rerun()
    else:
        workout_name = day_data['Workout_Name'].iloc[0]
        st.subheader(f"Programm: {workout_name}")

        with st.expander("➕ Neue Übung hinzufügen", expanded=True):
            with st.form("ex_form", clear_on_submit=True):
                ex_name = st.text_input("Übung")
                col1, col2 = st.columns(2)
                with col1:
                    weight = st.number_input("Gewicht (kg)", step=2.5)
                with col2:
                    reps = st.number_input("Wiederholungen", step=1)
                
                if st.form_submit_button("Speichern"):
                    if ex_name:
                        new_ex = pd.DataFrame([[selected_date, workout_name, ex_name, weight, reps]], 
                                             columns=st.session_state.df.columns)
                        # Platzhalter entfernen
                        st.session_state.df = st.session_state.df[~((st.session_state.df['Datum'] == selected_date) & (st.session_state.df['Übung'] == "Start"))]
                        st.session_state.df = pd.concat([st.session_state.df, new_ex], ignore_index=True)
                        save_data(st.session_state.df)
                        st.rerun()

        st.write("---")
        actual_exercises = day_data[day_data['Übung'] != "Start"]
        
        if not actual_exercises.empty:
            for i, row in actual_exercises.iterrows():
                # Ein kleiner Container für jede Übung mit Lösch-Button
                cols = st.columns([4, 1])
                with cols[0]:
                    st.info(f"**{row['Übung']}**: {row['Gewicht']}kg x {row['Wiederholungen']}")
                with cols[1]:
                    # Lösch-Button mit eindeutigem Key (Index i)
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.df = st.session_state.df.drop(i)
                        save_data(st.session_state.df)
                        st.rerun()
        else:
            st.write("Noch keine Übungen eingetragen.")