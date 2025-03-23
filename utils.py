import json
import re


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


def load_data(filename: str):
    """
    Load data from JSON file.

    args:
        - filename (str): JSON filename

    Returns:
        - data (dict): JSON data
    """
    try:
        with open(filename, "rb") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        reset_day_data(filename)
        return data


def save_data(filename: str, data: dict):
    """
    Save data to JSON file.

    args:
        - filename (str): JSON filename
        - data (dict): Dictionary of data to be saved
    """
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


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
    month_path = "data/month_results.json"
    data = load_data(month_path)

    winners = get_day_winners()

    for game, players in winners.items():
        n_winners = len(players)
        for player in players:
            if game == "pinpoint":
                data = update_month_score(data, player, game, 1)
            else:
                data = update_month_score(data, player, game, 1 / n_winners)

    save_data(month_path, data)
    reset_day_data("data/today_results.json")


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
        num_chars = len(re.findall("\.", cell))
        if num_chars % 3 == 0:
            cell = cell.replace(".", "")
            cell += "I" * (num_chars // 3)
    elif score == 1 / 2:
        cell += "i"
        num_chars = len(re.findall("i", cell))
        if num_chars % 2 == 0:
            cell = cell.replace("i", "")
            cell += "I" * (num_chars // 2)
    else:
        cell += "I"

    num_chars = len(re.findall("I", cell))
    if num_chars % 5 == 0:
        cell = cell.replace("I", "")
        cell += "5" * (num_chars // 5)

    cell = cell.replace("0", "")
    cell = sort_cell(cell)

    data[game][player] = cell

    return data


def get_day_winners():
    """
    Returns winners for each game

    Returns:
        - results (dict): Dictionary with game names as keys and lists of winners as values
    """
    today_path = "data/today_results.json"
    today_results = load_data(today_path)

    results = {
        "Queens 👑": [],
        "Tango 🔵🟠": [],
        "Pinpoint 🟦": [],
        "Cross 🧗": [],
        "Zip 🐍": [],
    }

    for game in today_results.keys():
        game: str
        if game == "timestamp":
            continue
        elif game.split(" ")[0].lower() != "pinpoint":
            best_score = 1000
            for name, score in today_results[game].items():
                score = parse_time(score)
                if score < best_score:
                    best_score = score
                    results[game] = [name]
                elif score == best_score:
                    results[game].append(name)
        else:
            for name, score in today_results[game].items():
                if score == "Yes":
                    results[game].append(name)

    return results


def update_global_results():
    """
    Update global results and reset months's results.
    """
    global_path = "data/global_results.json"
    data = load_data(global_path)

    winners = get_month_winners()

    for game, players in winners.items():
        n_winners = len(players)
        for player in players:
            data = update_global_score(data, player, game, n_winners)

    save_data(global_path, data)
    reset_month_data("data/month_results.json")


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


def get_month_winners():
    """
    Returns winners for each game in the month

    Returns:
        - results (dict): Dictionary with game names as keys and lists of winners as values
    """
    month_path = "data/month_results.json"
    month_results = load_data(month_path)

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
    convert_values = {
        "5": 5,
        "I": 1,
        "i": 0.5,
        ".": 1 / 3,
    }
    result = 0
    for char in text_result:
        result += convert_values[char]

    return result
