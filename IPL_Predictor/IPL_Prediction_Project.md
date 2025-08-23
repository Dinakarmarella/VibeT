# IPL Winner Prediction Agent

This document outlines the project to build an agent that predicts the winner of the Indian Premier League (IPL).

## 1. Project Plan

The project will be executed in the following phases:

1.  **Framework and Model Selection:** We will use Python with the `scikit-learn` library. The initial model will be `Logistic Regression`.
2.  **Data Preparation:** We will parse the data from `IPL_Prediction.md` to create a structured dataset for model training.
3.  **Model Training:** We will train the `Logistic Regression` model on the prepared dataset.
4.  **Prediction Agent:** We will create a Python script that takes two team names as input and predicts the winner of a match between them.

## 2. Model Selection Rationale

### 2.1. Scikit-learn

`scikit-learn` is a widely-used and well-documented Python library for machine learning. It provides a robust and efficient implementation of various algorithms, making it an ideal choice for this project.

### 2.2. Logistic Regression

`Logistic Regression` was chosen for the following reasons:

*   **Simplicity and Interpretability:** It is a straightforward and easy-to-understand model, which is great for establishing a baseline.
*   **Memory Efficiency:** Logistic Regression has a very small memory footprint, which aligns with the project's constraint on memory usage.
*   **Good for Small Datasets:** It is a linear model, which makes it less likely to overfit on a small dataset like the one we are using.

## 3. Progress Log

*   **2025-08-23:**
    *   Project initiated.
    *   Project plan and model selection rationale documented.
    *   Data preparation script created and executed.
    *   Model training script created and executed.
    *   Prediction agent script created.
    *   Tournament simulation script created and executed.

## 4. How to Use the Prediction Agent

The prediction agent is a command-line script that you can run from your terminal.

### 4.1. Predicting a Single Match

1.  Open a terminal or command prompt.
2.  Navigate to the `IPL_Predictor` directory:
    ```
    cd C:\Users\DINAKARMARELLA\Documents\Dins\VibeT\IPL_Predictor
    ```
3.  Run the `predict_winner.py` script with two team names as arguments:
    ```
    python predict_winner.py <team1> <team2>
    ```

**Example:**

```
python predict_winner.py rcb MI
The predicted winner of the match between rcb and MI is: MI
```

### 4.2. Simulating a Tournament

1.  Open a terminal or command prompt.
2.  Navigate to the `IPL_Predictor` directory:
    ```
    cd C:\Users\DINAKARMARELLA\Documents\Dins\VibeT\IPL_Predictor
    ```
3.  Run the `simulate_tournament.py` script:
    ```
    python simulate_tournament.py
    ```

## 5. How the Prediction Works

The model predicted MI as the winner based on the historical data from the 2022 and 2023 seasons that we used for training. Here's a simplified explanation of how it works:

1.  **Data Driven:** The model was trained on the head-to-head match data. In the historical data, MI has a better win record against RCB.
2.  **Feature Importance:** The model learns to assign importance to each team based on their past performance. In this case, the model has learned that MI has a higher probability of winning against RCB based on the data it has seen.
3.  **Prediction:** When we ask the model to predict the winner of a match between RCB and MI, it uses the learned patterns to calculate the probability of each team winning. In this case, the probability of MI winning was higher, so it was chosen as the winner.

It's important to remember that this prediction is based on a limited amount of data and a simple model. More data and a more complex model could yield different results.

## 6. Tournament Simulation Results

Based on the historical data from the 2022 and 2023 seasons, the predicted winner for the next three years is **GT (Gujarat Titans)**.

**Final Points Table (from one of the simulated years):**
*   GT: 36
*   RR: 30
*   LSG: 24
*   KKR: 22
*   CSK: 20
*   RCB: 20
*   MI: 16
*   DC: 6
*   PBKS: 6
*   SRH: 0

## 7. Project Artifacts

### 7.1. `data_preparator.py`

```python
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

    # Create a DataFrame and save it to CSV
    df_h2h = pd.DataFrame(h2h_data)
    df_h2h.to_csv('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_data.csv', index=False)

if __name__ == '__main__':
    prepare_data()
```

### 7.2. `train_model.py`

```python
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
    df_swapped = df.copy()
    df_swapped[['team1', 'team2']] = df_swapped[['team2', 'team1']]
    df_swapped[['team1_wins', 'team2_wins']] = df_swapped[['team2_wins', 'team1_wins']]

    df_combined = pd.concat([df, df_swapped], ignore_index=True)

    df_combined['winner'] = (df_combined['team1_wins'] / (df_combined['team1_wins'] + df_combined['team2_wins'] + 1e-6)).round()

    X = pd.get_dummies(df_combined[['team1', 'team2']], columns=['team1', 'team2'], drop_first=True)
    y = df_combined['winner']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)

    print(f"Model Accuracy: {model.score(X_test, y_test)}")

    joblib.dump(model, 'C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_model.pkl')

if __name__ == '__main__':
    train_model()
```

### 7.3. `predict_winner.py`

```python
import joblib
import pandas as pd
import sys

def predict_winner(team1, team2):
    """Loads the trained model and predicts the winner of a match."""
    model = joblib.load('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_model.pkl')

    training_columns = model.feature_names_in_

    input_data = pd.DataFrame({'team1': [team1], 'team2': [team2]})
    input_encoded = pd.get_dummies(input_data)
    input_aligned = input_encoded.reindex(columns=training_columns, fill_value=0)

    prediction = model.predict(input_aligned)

    if prediction[0] == 1:
        return team1
    else:
        return team2

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python predict_winner.py <team1> <team2>")
        sys.exit(1)

    team1 = sys.argv[1]
    team2 = sys.argv[2]

    winner = predict_winner(team1, team2)

    print(f"The predicted winner of the match between {team1} and {team2} is: {winner}")
```

### 7.4. `simulate_tournament.py`

```python
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
    model = joblib.load('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_model.pkl')
    training_columns = model.feature_names_in_

    df = pd.read_csv('C:/Users/DINAKARMARELLA/Documents/Dins/VibeT/IPL_Predictor/ipl_data.csv')
    teams = pd.unique(df[['team1', 'team2']].values.ravel('K'))

    points_table = {team: 0 for team in teams}

    schedule = []
    for team1, team2 in combinations(teams, 2):
        schedule.append((team1, team2))
        schedule.append((team2, team1))

    for team1, team2 in schedule:
        winner = predict_winner(team1, team2, model, training_columns)
        points_table[winner] += 2

    sorted_points_table = sorted(points_table.items(), key=lambda item: item[1], reverse=True)

    winner = sorted_points_table[0][0]

    return winner, sorted_points_table

if __name__ == '__main__':
    print("Simulating IPL tournament...")
    for year in range(1, 4):
        winner, points_table = simulate_tournament()
        print(f"\n--- Year {year} Simulation ---")
        print("Final Points Table:")
        for team, points in points_table:
            print(f"{team}: {points}")
        print(f"\nPredicted Winner for Year {year}: {winner}")
```
```