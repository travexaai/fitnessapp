import streamlit as st
import pandas as pd
import datetime
import os

# --- DATEI-EINSTELLUNGEN ---
DATA_FILE = "training_data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=['Datum'])
    return pd.DataFrame(columns=['Datum', 'Übung', 'Gewicht', 'Wiederholungen'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- APP CONFIG ---
st.set_page_config(page_title="Fitness Tracker", layout="centered")

# Daten beim Start laden
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# --- NAVIGATION ---
menu = ["📈 Dashboard", "🏋️ Training"]
choice = st.sidebar.selectbox("Menü", menu)

# --- DASHBOARD ---
if choice == "📈 Dashboard":
    st.title("Dein Fortschritt")
    
    if st.session_state.df.empty:
        st.info("Noch keine Daten vorhanden. Geh zum Training-Tab!")
    else:
        df = st.session_state.df
        # Volumen berechnen (Gewicht * Wiederholungen)
        df['Volumen'] = df['Gewicht'] * df['Wiederholungen']
        
        # Grafik anzeigen (Fortschritt über die Zeit)
        st.subheader("Gesamtvolumen Entwicklung")
        chart_data = df.groupby('Datum')['Volumen'].sum().reset_index()
        st.line_chart(chart_data.set_index('Datum'))
        
        # Letzte Einträge
        st.subheader("Letzte Einheiten")
        st.dataframe(df.sort_values(by='Datum', ascending=False).head(5))

# --- TRAINING ---
elif choice == "🏋️ Training":
    st.title("Neues Training")

    with st.form("training_form", clear_on_submit=True):
        date = st.date_input("Datum", datetime.date.today())
        exercise = st.text_input("Übung (z.B. Kniebeugen)")
        weight = st.number_input("Gewicht (kg)", min_value=0.0, step=2.5)
        reps = st.number_input("Wiederholungen", min_value=0, step=1)
        
        submit = st.form_submit_button("Eintragen")
        
        if submit:
            if exercise:
                new_entry = pd.DataFrame([[pd.to_datetime(date), exercise, weight, reps]], 
                                         columns=['Datum', 'Übung', 'Gewicht', 'Wiederholungen'])
                st.session_state.df = pd.concat([st.session_state.df, new_entry], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"{exercise} gespeichert!")
            else:
                st.error("Bitte gib einen Namen für die Übung ein.")

    # Detail-Ansicht
    st.divider()
    st.subheader("Übungshistorie")
    if not st.session_state.df.empty:
        exercises = st.session_state.df['Übung'].unique()
        selected_ex = st.selectbox("Wähle eine Übung aus, um Details zu sehen:", exercises)
        
        history = st.session_state.df[st.session_state.df['Übung'] == selected_ex]
        st.table(history.sort_values(by='Datum', ascending=False))