# Python script for AdiLeague
# Last changed: 19.12.2024

import itertools
from collections import defaultdict


# -------------------------------------
# Local paramateres
# ! Swap with real team names ! 
divisions = {
    "Division 1": [f"Div1_Team{i}" for i in range(1, 9)],
    "Division 2": [f"Div2_Team{i}" for i in range(1, 9)],
}
# Slot A - 17:00 / Slot B - 18:00
time_slots = ["Slot A", "Slot B"]
rounds = len(divisions["Division 1"]) - 1  # 7 rounds for 8 teams

# Game day pattern
game_day_patterns = [
    ["Monday", "Tuesday"],  # Week 1
    ["Monday", "Thursday"],  # Week 2
]
# -------------------------------------

# -------------------------------------
# Setting up the schedule
# Defaultdict to store games for each day/round, the list with the keys (days) will automaticlly grow as we add more games 
schedule = defaultdict(list)

# Function to generate round-robin pairings
# Each team plays against each other once 
def generate_round_robin(teams):
    n = len(teams)
    pairings = []
    for i in range(n - 1):
        round_pairings = []
        for j in range(n // 2):
            round_pairings.append((teams[j], teams[n - j - 1]))
        # Remove the last team from the list, puts it into position number #2 
        teams.insert(1, teams.pop())  # Rotate teams
        pairings.append(round_pairings)
    return pairings

# Assign referees and ensure fairness
def assign_referees(games, teams):
    referees = defaultdict(int)
    assignments = []
    for game in games:
        non_playing_teams = [team for team in teams if team not in game]
        referee = min(non_playing_teams, key=lambda x: referees[x])
        referees[referee] += 1
        assignments.append((game, referee))
    return assignments

# Generate the schedule for each division
# Create 'teams' - i in divisions
for division, teams in divisions.items():
    # Generate pairings
    pairings = generate_round_robin(teams)
    slot_tracker = defaultdict(lambda: {"Slot A": 0, "Slot B": 0})
    day_tracker = defaultdict(int)

    for rnd, games in enumerate(pairings, start=1):
        # Determine the week's game-day pattern
        days = game_day_patterns[(rnd - 1) % len(game_day_patterns)]
        games_with_referees = assign_referees(games, teams)

        for idx, ((team1, team2), referee) in enumerate(games_with_referees):
            # Assign time slots
            slot = "Slot A" if slot_tracker[team1]["Slot A"] <= slot_tracker[team1]["Slot B"] else "Slot B"
            slot_tracker[team1][slot] += 1
            slot_tracker[team2][slot] += 1

            # Assign day based on the current game index
            day = days[idx % len(days)]

            # Add to the schedule
            game_info = {
                "Round": rnd,
                "Day": day,
                "Slot": slot,
                "Game": f"{team1} vs {team2}",
                "Referee": referee,
            }
            schedule[division].append(game_info)

# Display the schedule
for division, games in schedule.items():
    print(f"\n{division} Schedule:")
    for game in games:
        print(f"Round {game['Round']} | {game['Day']} {game['Slot']} | Game: {game['Game']} | Referee: {game['Referee']}")
