import joblib
import pandas as pd
import sys

def predict_winner(team1, team2):
    """Loads the trained model and predicts the winner of a match."""
    # Load the model
    model = joblib.load('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_model.pkl')

    # Create a DataFrame for the input
    input_data = pd.DataFrame({'team1': [team1], 'team2': [team2]})

    # Load the training columns to ensure the input has the same one-hot encoded columns
    training_columns = model.feature_names_in_

    # One-hot encode the input data
    input_encoded = pd.get_dummies(input_data)

    # Align the columns of the input data with the training data
    input_aligned = input_encoded.reindex(columns=training_columns, fill_value=0)

    # Make the prediction
    prediction = model.predict(input_aligned)

    if prediction[0] == 1:
        return team1
    else:
        return team2

if __name__ == '__main__':
    # Get user input from command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python predict_winner.py <team1> <team2>")
        sys.exit(1)

    team1 = sys.argv[1]
    team2 = sys.argv[2]

    # Predict the winner
    winner = predict_winner(team1, team2)

    # Display the result
    print(f"The predicted winner of the match between {team1} and {team2} is: {winner}")