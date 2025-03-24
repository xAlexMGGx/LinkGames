import streamlit as st
from datetime import datetime
from utils import (
    load_data,
    update_data,
    parse_time,
    update_month_results,
    update_global_results,
    check_tie_breakers,
)
from pytz import timezone


# Archivo donde se guardarán los datos
DATA_FILE = "./data/today_results.json"


# Formulario de entrada
player = st.selectbox(
    "Nombre del jugador",
    ("Alex", "Jorge", "Mazu", "Galo", "Priti"),
    index=None,
    placeholder="Escoge nombre del jugador",
)
queens = st.text_input("Tiempo en Queens (X o X:YY):")
tango = st.text_input("Tiempo en Tango (X o X:YY):")
zip = st.text_input("Tiempo en Zip (X o X:YY):")
cross = st.text_input("Tiempo en Cross (X o X:YY):")
pinpoint = st.checkbox("Adivinó la categoría en Pinpoint?")
submit = st.button("Registrar")

california_tz = timezone("America/Los_Angeles")
current_date = datetime.now().astimezone(california_tz).date()

if submit and player:
    times = {"queens": queens, "tango": tango, "zip": zip, "cross": cross}
    parsed_times = {}
    valid = True

    for key, value in times.items():
        parsed = parse_time(value)
        if parsed is None:
            st.error(f"Formato inválido en {key}. Use 'X' o 'X:YY'.")
            valid = False
        else:
            parsed_times[key] = parsed

    if valid:
        california_tz = timezone("America/Los_Angeles")
        new_data = {
            "queens": times["queens"],
            "tango": times["tango"],
            "zip": times["zip"],
            "cross": times["cross"],
            "pinpoint": "Yes" if pinpoint else "No",
            "timestamp": str(current_date),
        }
        update_data(DATA_FILE, new_data, player)
        st.success("Registro guardado correctamente!")

# Mostrar registros existentes
st.subheader("Registros de hoy")
data = load_data(DATA_FILE)
if len(data["timestamp"]) != 0:
    last_date = list(data["timestamp"].values())[0]
    last_date = datetime.strptime(last_date, "%Y-%m-%d").date()
    if last_date != current_date:
        check_tie_breakers()
        update_month_results()
        if current_date.day == 1:
            update_global_results()
        data = load_data(DATA_FILE)

n_rows = len(data["Queens 👑"])
if n_rows > 0:
    st.dataframe(data)
else:
    st.write("No hay registros aún.")
