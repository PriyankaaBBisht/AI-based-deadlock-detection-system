
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

def train_and_save_model():
    df = pd.read_csv("data/system_logs.csv")
    X = df[['cpu', 'memory', 'io_wait', 'threads']]
    y = df['deadlock']
    model = RandomForestClassifier()
    model.fit(X, y)

    os.makedirs("models", exist_ok=True)
    with open("models/deadlock_predictor.pkl", "wb") as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    train_and_save_model()
