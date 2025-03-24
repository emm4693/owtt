import requests
import csv
import os
from collections import defaultdict

# === USER SETTINGS ===
battletags = ["factor-11595", "factor-11975", "factor-11726"]
platform = "pc"
region = "us"

# === Time Helpers ===
def parse_time_string(time_str):
    try:
        hours, minutes = map(int, time_str.strip().split(":"))
        return hours * 60 + minutes
    except:
        return 0

def format_minutes_to_string(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m" if hours else f"{mins}m"

# === Load previous total time from CSV ===
def load_csv_data(filename):
    data = {}
    if not os.path.exists(filename):
        return data
    with open(filename, "r", newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            hero = row["Hero"]
            time_str = row["Time"]
            data[hero] = parse_time_string(time_str)
    return data

# === Save updated time to CSV ===
def save_csv_data(filename, data):
    with open(filename, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Hero", "Time"])
        for hero, minutes in sorted(data.items()):
            writer.writerow([hero, f"{minutes // 60}:{minutes % 60:02d}"])

# === Extract time from OW-API ===
def extract_all_modes_time(stats):
    result = defaultdict(int)
    for hero, info in stats.get("careerStats", {}).items():
        time_str = info.get("game", {}).get("timePlayed")
        if time_str:
            result[hero] += parse_time_string(time_str)
    return result

# === Track global combined totals ===
combined_totals = defaultdict(int)

# === MAIN PROCESS ===
for tag in battletags:
    filename = f"{tag}.csv"
    previous_data = load_csv_data(filename)

    url = f"https://ow-api.com/v1/stats/{platform}/{region}/{tag}/complete"
    response = requests.get(url)

    if response.status_code != 200:
        continue

    data = response.json()
    quick = extract_all_modes_time(data.get("quickPlayStats", {}))
    comp = extract_all_modes_time(data.get("competitiveStats", {}))

    # Sum all modes
    current_totals = defaultdict(int)
    for hero, minutes in quick.items():
        current_totals[hero] += minutes
    for hero, minutes in comp.items():
        current_totals[hero] += minutes

    # Update and write new per-account data
    updated_data = previous_data.copy()
    for hero, current_minutes in current_totals.items():
        prev_minutes = previous_data.get(hero, 0)
        if current_minutes > prev_minutes:
            updated_data[hero] = current_minutes

    save_csv_data(filename, updated_data)

    # Add to global totals
    for hero, minutes in updated_data.items():
        combined_totals[hero] += minutes

# === Role-based Sorted Output ===

roles = {
    "Tank": [
        "D.Va", "Doomfist", "Junker Queen", "Mauga", "Orisa", "Ramattra",
        "Reinhardt", "Roadhog", "Sigma", "Winston", "Wrecking Ball", "Zarya"
    ],
    "DPS": [
        "Ashe", "Bastion", "Cassidy", "Echo", "Genji", "Hanzo", "Junkrat",
        "Mei", "Pharah", "Reaper", "Sojourn", "Soldier:76", "Sombra",
        "Symmetra", "Torbjörn", "Tracer", "Widowmaker"
    ],
    "Support": [
        "Ana", "Baptiste", "Brigitte", "Illari", "Kiriko", "Lifeweaver",
        "Lúcio", "Mercy", "Moira", "Zenyatta"
    ]
}

# Organize by role
role_columns = {"Tank": [], "DPS": [], "Support": []}

for role, heroes in roles.items():
    for hero in heroes:
        if hero in combined_totals:
            role_columns[role].append(f"{hero}: {format_minutes_to_string(combined_totals[hero])}")

# Determine longest column for layout
max_rows = max(len(role_columns["Tank"]), len(role_columns["DPS"]), len(role_columns["Support"]))

print("\n🎯 Total Time Played Per Hero (Sorted by Role)\n")
print(f"{'Tank':<30}{'DPS':<30}{'Support'}")
print("-" * 90)

# === Role-based Sorted Output (by time played) ===

roles = {
    "Tank": [
        "D.Va", "Doomfist", "Junker Queen", "Mauga", "Orisa", "Ramattra",
        "Reinhardt", "Roadhog", "Sigma", "Winston", "Wrecking Ball", "Zarya"
    ],
    "DPS": [
        "Ashe", "Bastion", "Cassidy", "Echo", "Genji", "Hanzo", "Junkrat",
        "Mei", "Pharah", "Reaper", "Sojourn", "Soldier:76", "Sombra",
        "Symmetra", "Torbjörn", "Tracer", "Widowmaker"
    ],
    "Support": [
        "Ana", "Baptiste", "Brigitte", "Illari", "Kiriko", "Lifeweaver",
        "Lúcio", "Mercy", "Moira", "Zenyatta"
    ]
}

# Collect heroes and times by role, then sort by time played descending
role_columns = {"Tank": [], "DPS": [], "Support": []}

for role, heroes in roles.items():
    hero_times = [
        (hero, combined_totals[hero])
        for hero in heroes if hero in combined_totals
    ]
    sorted_heroes = sorted(hero_times, key=lambda x: -x[1])
    role_columns[role] = [f"{hero}: {format_minutes_to_string(minutes)}" for hero, minutes in sorted_heroes]

# Print headers and aligned columns
max_rows = max(len(role_columns["Tank"]), len(role_columns["DPS"]), len(role_columns["Support"]))

print("\n🎯 Total Time Played Per Hero (Sorted by Role & Time Played)\n")
print(f"{'Tank':<30}{'DPS':<30}{'Support'}")
print("-" * 90)

for i in range(max_rows):
    tank = role_columns["Tank"][i] if i < len(role_columns["Tank"]) else ""
    dps = role_columns["DPS"][i] if i < len(role_columns["DPS"]) else ""
    support = role_columns["Support"][i] if i < len(role_columns["Support"]) else ""
    print(f"{tank:<30}{dps:<30}{support}")

