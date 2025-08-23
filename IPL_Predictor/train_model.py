import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib

def train_model():
    """Loads the prepared data, trains a logistic regression model, 
    and saves the model to a file.
    """
    # Load the data
    df = pd.read_csv('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_data.csv')

    # Feature Engineering
    # We'll create a simple feature: the head-to-head win percentage for team 1.
    # We need to create a balanced dataset for training, so we'll duplicate the data
    # and swap the teams to have a balanced representation of each team winning.

    df_swapped = df.copy()
    df_swapped[['team1', 'team2']] = df_swapped[['team2', 'team1']]
    df_swapped[['team1_wins', 'team2_wins']] = df_swapped[['team2_wins', 'team1_wins']]

    df_combined = pd.concat([df, df_swapped], ignore_index=True)

    # Create the target variable 'winner' (1 if team1 wins, 0 if team2 wins)
    # To avoid division by zero, we add a small epsilon (1e-6)
    df_combined['winner'] = (df_combined['team1_wins'] / (df_combined['team1_wins'] + df_combined['team2_wins'] + 1e-6)).round()

    # Create features (X) and target (y)
    # For simplicity, we will use the team names as categorical features.
    # We will use one-hot encoding to convert them to numerical features.
    X = pd.get_dummies(df_combined[['team1', 'team2']], columns=['team1', 'team2'], drop_first=True)
    y = df_combined['winner']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Evaluate the model
    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy}")

    # Save the model
    joblib.dump(model, 'C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_model.pkl')

if __name__ == '__main__':
    train_model()
