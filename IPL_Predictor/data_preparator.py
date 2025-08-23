import re
import pandas as pd

def prepare_data():
    """Reads the IPL prediction data from the markdown file, 
    parses it, and saves it as a CSV file.
    """
    with open('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/IPL_Prediction.md', 'r') as f:
        content = f.read()

    # Parse Head-to-Head Records
    h2h_section = content.split('Head-to-Head Records (2022-2023 Seasons)')[1].split('Overall Wins and Losses')[0]
    h2h_lines = h2h_section.strip().split('\n')[2:]
    h2h_data = []
    for line in h2h_lines:
        parts = line.split(',')
        if len(parts) == 5:
            team1, team2, matches, team1_wins, team2_wins = parts
            h2h_data.append({
                'team1': team1.strip(),
                'team2': team2.strip(),
                'matches_played': int(matches.strip()),
                'team1_wins': int(team1_wins.strip()),
                'team2_wins': int(team2_wins.strip())
            })

    # Parse Overall Wins and Losses
    overall_section = content.split('Overall Wins and Losses (2022-2023 Seasons)')[1].split('Home Win Data')[0]
    overall_lines = overall_section.strip().split('\n')[2:]
    overall_data = []
    for line in overall_lines:
        parts = line.split(',')
        if len(parts) == 4:
            team, matches, wins, losses = parts
            overall_data.append({
                'team': team.strip(),
                'total_matches': int(matches.strip()),
                'total_wins': int(wins.strip()),
                'total_losses': int(losses.strip())
            })

    # Create a DataFrame and save it to CSV
    df_h2h = pd.DataFrame(h2h_data)
    df_overall = pd.DataFrame(overall_data)

    # For simplicity, we will just save the head-to-head data for now.
    # We can incorporate the overall data later as features.
    df_h2h.to_csv('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_data.csv', index=False)

if __name__ == '__main__':
    prepare_data()
