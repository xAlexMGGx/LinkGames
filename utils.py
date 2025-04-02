import json
import re
import streamlit as st
import requests
import pandas as pd

from pprint import pprint

# File paths
TODAY_PATH = "today_results.json"
MONTH_PATH = "month_results.json"
GLOBAL_PATH = "global_results.json"
LAST_DAY_PATH = "last_day_results.json"
LAST_MONTH_PATH = "last_month_results.json"

# GitHub Gist IDs (replace with your own)
GISTS_IDS = {
    TODAY_PATH: st.secrets["TODAY_GIST_ID"],
    MONTH_PATH: st.secrets["MONTH_GIST_ID"],
    GLOBAL_PATH: st.secrets["GLOBAL_GIST_ID"],
    LAST_DAY_PATH: st.secrets["LAST_DAY_GIST_ID"],
    LAST_MONTH_PATH: st.secrets["LAST_MONTH_GIST_ID"],
}
GIST_URL = "https://api.github.com/gists/"
GITHUB_TOKEN = st.secrets["GISTS_API_TOKEN"]

# GitHub API endpoints
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def load_data(filename: str):
    """
    Fetch JSON data from the GitHub Gist

    args:
        - filename (str): JSON filename

    Returns:
        - dict: JSON data from the GitHub Gist
    """
    url = GIST_URL + str(GISTS_IDS[filename])
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return json.loads(response.json()["files"][filename]["content"])
    else:
        st.error("Failed to load data.")
        return {}


def save_data(filename, new_data):
    """
    Update the JSON data in the GitHub Gist

    args:
        - filename (str): JSON filename
        - new_data (dict): New JSON data to be saved
    """
    updated_content = json.dumps(new_data, indent=4)
    payload = {"files": {filename: {"content": updated_content}}}
    url = GIST_URL + str(GISTS_IDS[filename])
    response = requests.patch(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        st.success("Data updated successfully!")
    else:
        st.error("Failed to update data.")


def reset_day_data(filename):
    """
    Reset JSON data.

    args:
        - filename (str): JSON filename
    """
    data = {
        "Queens 👑": {},
        "Tango 🔵🟠": {},
        "Pinpoint 🟦": {},
        "Cross 🧗": {},
        "Zip 🐍": {},
        "timestamp": {},
    }
    save_data(filename, data)


def reset_month_data(filename):
    """
    Reset JSON data for the current month.

    args:
        - filename (str): JSON filename
    """
    games = [
        "Queens \ud83d\udc51",
        "Tango \ud83d\udd35\ud83d\udfe0",
        "Pinpoint \ud83d\udfe6",
        "Cross \ud83e\uddd7",
        "Zip \ud83d\udc0d",
    ]
    players = ["Alex", "Jorge", "Mazu", "Galo", "Priti"]
    data = {game: {player: "" for player in players} for game in games}
    save_data(filename, data)


def update_data(filename: str, data: dict, player: str):
    """
    Update data in existing JSON file.

    args:
        - filename (str): JSON filename
        - data (dict): Dictionary of data to be updated
    """
    game_names = {
        "queens": "Queens 👑",
        "tango": "Tango 🔵🟠",
        "pinpoint": "Pinpoint 🟦",
        "cross": "Cross 🧗",
        "zip": "Zip 🐍",
    }
    existing_data = load_data(filename)
    for game, result in data.items():
        if game in game_names:
            existing_data[game_names[game]][player] = result
        else:
            if game not in existing_data:
                existing_data[game] = {}
            existing_data[game][player] = result

    save_data(filename, existing_data)


def parse_time(time_str):
    """
    Convert a time string into seconds.

    args:
        - time_str (str): Time string in format "seconds" or "minutes:seconds"

    Returns:
        - time (int): Time in seconds
    """
    if re.fullmatch(r"\d+", time_str):  # Solo segundos
        return int(time_str)
    elif re.fullmatch(r"\d+:\d{2}", time_str):  # Formato minutos:segundos
        minutes, seconds = map(int, time_str.split(":"))
        return minutes * 60 + seconds
    else:
        return None


def update_month_results():
    """
    Update monthly results and reset today's results.
    """
    data = load_data(TODAY_PATH)
    save_data(LAST_DAY_PATH, data)

    data = load_data(MONTH_PATH)

    winners = get_day_winners()

    for game, players in winners.items():
        n_winners = len(players)
        for player in players:
            if game == "pinpoint":
                data = update_month_score(data, player, game, 1)
            else:
                data = update_month_score(data, player, game, 1 / n_winners)

    save_data(MONTH_PATH, data)
    reset_day_data(TODAY_PATH)


def sort_cell(cell):
    """
    Sort a cell according to the specified order.

    args:
        - cell (str): Cell to be sorted

    Returns:
        - sorted_cell (str): Sorted cell
    """
    # Define the custom order
    order = "5Ii."

    # Create a dictionary to map each character to its order
    order_map = {char: index for index, char in enumerate(order)}

    # Sort using the custom order
    sorted_cell = "".join(sorted(cell, key=lambda char: order_map[char]))

    return sorted_cell


def update_month_score(data: dict, player: int, game: str, score: float | int):
    """
    Update the score in the data.

    args:
        - data (dict): Data dictionary
        - player (int): Player ID
        - game (str): Game name
        - score (float | int): Score to be added

    Returns:
        - data (dict): Updated data dictionary
    """
    # Update the score
    cell: str = data[game][player]
    if score == 1 / 3:
        cell += "."
        num_chars = len(re.findall(r"\.", cell))
        if num_chars % 3 == 0:
            cell = cell.replace(".", "")
            cell += "I" * (num_chars // 3)
    elif score == 1 / 2:
        cell += "i"
        num_chars = len(re.findall(r"i", cell))
        if num_chars % 2 == 0:
            cell = cell.replace("i", "")
            cell += "I" * (num_chars // 2)
    else:
        cell += "I"

    num_chars = len(re.findall(r"I", cell))
    if num_chars % 5 == 0:
        cell = cell.replace("I", "")
        cell += "5" * (num_chars // 5)

    cell = cell.replace("0", "")
    cell = sort_cell(cell)

    data[game][player] = cell

    return data


def get_day_winners(data: dict = None, players: list[str] = None, check_game: str = None):
    """
    Returns winners for each game

    args:
        - players (list[str]): List of players to consider for the winners

    Returns:
        - results (dict): Dictionary with game names as keys and lists of winners as values
    """
    if data is None:
        today_results = load_data(TODAY_PATH)
    else:
        today_results = data

    results = {
        "Queens 👑": [],
        "Tango 🔵🟠": [],
        "Pinpoint 🟦": [],
        "Cross 🧗": [],
        "Zip 🐍": [],
    }

    if players is None:
        players = list(today_results["Queens 👑"].keys())

    for game in today_results.keys():
        game: str
        if check_game is not None and game != check_game:
            continue
        elif game == "timestamp":
            continue
        elif game.split(" ")[0].lower() != "pinpoint":
            best_score = 1000
            for name in players:
                score = today_results[game][name]
                score = parse_time(score)
                if score < best_score:
                    best_score = score
                    results[game] = [name]
                elif score == best_score:
                    results[game].append(name)
        else:
            for name in players:
                score = today_results[game][name]
                if score == "Yes":
                    results[game].append(name)

    return results


def update_global_results():
    """
    Update global results and reset months's results.
    """
    data = load_data(MONTH_PATH)
    save_data(LAST_MONTH_PATH, data)

    data = load_data(GLOBAL_PATH)

    winners = get_month_winners()

    for game, players in winners.items():
        n_winners = len(players)
        for player in players:
            data = update_global_score(data, player, game, n_winners)

    save_data(GLOBAL_PATH, data)
    reset_month_data(MONTH_PATH)


def update_global_score(data: dict, player: str, game: str, n_winners: int):
    """
    Update global score in the data.

    args:
        - data (dict): Data dictionary
        - player (str): Player name
        - game (str): Game name
        - n_winners (int): Number of winners

    Returns:
        - data (dict): Updated data dictionary
    """
    curr_score = data[game][player]
    if n_winners == 1:
        data[game][player] = str(int(curr_score) + 1)
    else:
        data[game][player] = curr_score + "?"

    return data


def get_month_winners(data: dict = None):
    """
    Returns winners for each game in the month

    Returns:
        - results (dict): Dictionary with game names as keys and lists of winners as values
    """
    if data is None:
        month_results = load_data(MONTH_PATH)
    else:
        month_results = data

    results = {
        "Queens 👑": [],
        "Tango 🔵🟠": [],
        "Pinpoint 🟦": [],
        "Cross 🧗": [],
        "Zip 🐍": [],
    }

    for game in month_results.keys():
        game: str
        best_score = -1
        for name, score in month_results[game].items():
            score = convert_result(score)
            if score > best_score:
                best_score = score
                results[game] = [name]
            elif score == best_score:
                results[game].append(name)

    return results


def convert_result(text_result: str):
    """
    Converter for the text result to number result.
    """
    convert_values = {"5": 5, "I": 1, "i": 0.5, ".": 1 / 3, "0": 0}
    result = 0
    for char in text_result:
        result += convert_values[char]

    return result


def convert_table(data: dict):
    """
    Return whole table converted using convert_results function.

    args:
        - data (dict): Data dictionary

    Returns:
        - table (dict): Table with converted results
    """
    table = {}
    for game, players in data.items():
        table[game] = {}
        for player, score in players.items():
            table[game][player] = convert_result(score)
    
    return table


def check_tie_breakers():
    """
    Check for tie breakers and update the global results accordingly.
    """
    global_data = load_data(GLOBAL_PATH)

    tied_results = {}
    for game in global_data.keys():
        for player, score in global_data[game].items():
            if re.findall(r"\?", score):
                if game not in tied_results:
                    tied_results[game] = [player]
                else:
                    tied_results[game].append(player)

    for game in tied_results.keys():
        winners = get_day_winners(players=tied_results[game], check_game=game)
        n_winners = len(winners[game])
        if n_winners > 0:
            for player in tied_results[game]:
                global_data[game][player] = global_data[game][player].replace(
                    "?", ""
                )
            for winner in winners[game]:
                global_data = update_global_score(
                    global_data, winner, game, n_winners
                )
    #### NO QUITA LA ?
    save_data(GLOBAL_PATH, global_data)


def show_last_day_winners():
    """
    Show winners of the last day.
    """
    data = load_data(LAST_DAY_PATH)

    # Get winners for each game
    winners = get_day_winners(data=data)

    # Convert the data to a DataFrame
    data = pd.DataFrame(data)

    # Highlight winners in the DataFrame
    styled_data = data.style.apply(highlight_winners, axis=0, winners=winners)
    
    st.subheader("Ganadores del día anterior")
    n_rows = len(data["Queens 👑"])
    if n_rows > 0:
        st.dataframe(styled_data)
    else:
        st.write("No hay registros aún.")


def highlight_winners(s, winners: dict):
    """
    Highlight winners in the DataFrame.

    args:
        - s (pd.Series): Series to be highlighted

    Returns:
        - list: List of styles for each cell
    """
    category = s.name  # Get the column name (category)
    if category not in winners:
        return [""] * len(s)
    winners = winners[category]
    return ["background-color: yellow" if player in winners else "" for player in s.index]


def show_last_month_winners():
    """
    Show winners of the last month.
    """
    data = load_data(LAST_MONTH_PATH)

    # Get winners for each game
    winners = get_month_winners(data)

    # Convert the data to a DataFrame
    data = pd.DataFrame(data)

    # Highlight winners in the DataFrame
    styled_data = data.style.apply(highlight_winners, axis=0, winners=winners)

    st.subheader("Ganadores del mes anterior")
    n_rows = len(data["Queens 👑"])
    if n_rows > 0:
        st.dataframe(styled_data)
    else:
        st.write("No hay registros aún.")
