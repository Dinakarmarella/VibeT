import pandas as pd
import joblib
from itertools import combinations

def predict_winner(team1, team2, model, training_columns):
    """Predicts the winner of a match using the loaded model."""
    input_data = pd.DataFrame({'team1': [team1], 'team2': [team2]})
    input_encoded = pd.get_dummies(input_data)
    input_aligned = input_encoded.reindex(columns=training_columns, fill_value=0)
    prediction = model.predict(input_aligned)
    if prediction[0] == 1:
        return team1
    else:
        return team2

def simulate_tournament():
    """Simulates an IPL tournament and predicts the winner."""
    # Load the model and training columns
    model = joblib.load('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_model.pkl')
    training_columns = model.feature_names_in_

    # Get the list of teams
    df = pd.read_csv('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_data.csv')
    teams = pd.unique(df[['team1', 'team2']].values.ravel('K'))

    # Initialize points table
    points_table = {team: 0 for team in teams}

    # Generate schedule (each team plays every other team twice)
    schedule = []
    for team1, team2 in combinations(teams, 2):
        schedule.append((team1, team2))
        schedule.append((team2, team1))

    # Simulate matches
    for team1, team2 in schedule:
        winner = predict_winner(team1, team2, model, training_columns)
        points_table[winner] += 2  # 2 points for a win

    # Sort the points table
    sorted_points_table = sorted(points_table.items(), key=lambda item: item[1], reverse=True)

    # Get the winner
    winner = sorted_points_table[0][0]

    return winner, sorted_points_table

if __name__ == '__main__':
    print("Simulating IPL tournament...")
    # Simulate for 3 years
    for year in range(1, 4):
        winner, points_table = simulate_tournament()
        print(f"\n--- Year {year} Simulation ---")
        print("Final Points Table:")
        for team, points in points_table:
            print(f"{team}: {points}")
        print(f"\nPredicted Winner for Year {year}: {winner}")
