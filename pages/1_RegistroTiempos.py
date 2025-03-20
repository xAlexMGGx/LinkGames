import streamlit as st
import json
import re
from datetime import datetime

# Archivo donde se guardarán los datos
DATA_FILE = "resultados.json"


def load_data():
    """Carga los datos existentes del archivo JSON."""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_data(data):
    """Guarda los datos en el archivo JSON."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def parse_time(time_str):
    """Convierte el tiempo en formato válido a segundos."""
    if re.fullmatch(r"\d+", time_str):  # Solo segundos
        return int(time_str)
    elif re.fullmatch(r"\d+:\d{2}", time_str):  # Formato minutos:segundos
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds
    else:
        return None


st.title("Registro de Tiempos")

# Formulario de entrada
player = st.text_input("Nombre del jugador:")
queens = st.text_input("Tiempo en Queens (X o X:YY):")
tango = st.text_input("Tiempo en Tango (X o X:YY):")
zip = st.text_input("Tiempo en Zip (X o X:YY):")
cross = st.text_input("Tiempo en Cross (X o X:YY):")
pinpoint = st.checkbox("Adivinó la categoría en Pinpoint?")
submit = st.button("Registrar")

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
        data = load_data()
        data[player.lower()] = {
            "queens": parsed_times["queens"],
            "tango": parsed_times["tango"],
            "zip": parsed_times["zip"],
            "cross": parsed_times["cross"],
            "pinpoint": pinpoint,
            "timestamp": datetime.now().isoformat(),
        }
        save_data(data)
        st.success("Registro guardado correctamente!")

# Mostrar registros existentes
st.subheader("Registros previos")
data = load_data()
if data:
    st.write(data)
else:
    st.write("No hay registros aún.")
