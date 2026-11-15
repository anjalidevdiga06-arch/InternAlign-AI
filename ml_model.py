
import os
import pandas as pd
from functools import lru_cache

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------------------
# FILE PATHS
# -----------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ml_training_data.csv"
)


# -----------------------------------------
# LOAD TRAINING DATA
# -----------------------------------------

def load_training_data():

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            "ml_training_data.csv not found inside the data folder."
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = [
        "skill_match",
        "domain_match",
        "degree_match",
        "year_match",
        "experience_match",
        "suitable"
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in training dataset: {missing_columns}"
        )

    if data["suitable"].nunique() < 2:
        raise ValueError(
            "Training data must contain both suitable (1) "
            "and not suitable (0) examples."
        )

    return data


# -----------------------------------------
# TRAIN MACHINE LEARNING MODEL
# -----------------------------------------

@lru_cache(maxsize=1)
def train_model():

    data = load_training_data()

    features = [
        "skill_match",
        "domain_match",
        "degree_match",
        "year_match",
        "experience_match"
    ]

    X = data[features]
    y = data["suitable"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    model = LogisticRegression(
        max_iter=1000,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    report = classification_report(
        y_test,
        predictions,
        zero_division=0
    )

    return model, accuracy, report


# -----------------------------------------
# PREDICT INTERNSHIP SUITABILITY
# -----------------------------------------

def predict_suitability(
    skill_match,
    domain_match,
    degree_match,
    year_match,
    experience_match
):

    model, accuracy, report = train_model()

    # Convert domain match from 0-100 to 0-1

    if domain_match > 1:
        domain_match = domain_match / 100

    input_data = pd.DataFrame([{
        "skill_match": skill_match,
        "domain_match": domain_match,
        "degree_match": degree_match,
        "year_match": year_match,
        "experience_match": experience_match
    }])

    prediction = model.predict(input_data)[0]

    probability = model.predict_proba(input_data)[0][1]

    return {
        "prediction": int(prediction),
        "probability": round(float(probability) * 100, 2),
        "accuracy": round(float(accuracy) * 100, 2),
        "report": report
    }


# -----------------------------------------
# TEST MODEL
# -----------------------------------------

if __name__ == "__main__":

    model, accuracy, report = train_model()

    print("\n================================")
    print("       INTERNALIGN AI MODEL")
    print("================================")

    print("\nModel: Logistic Regression")

    print("\nModel Accuracy:")
    print(f"{accuracy * 100:.2f}%")

    print("\nClassification Report:")
    print(report)

    result = predict_suitability(
        skill_match=85,
        domain_match=1,
        degree_match=1,
        year_match=1,
        experience_match=1
    )

    print("\nSample Internship Prediction:")

    print("Prediction:", result["prediction"])
    print("Suitability Probability:", result["probability"], "%")

    if result["prediction"] == 1:
        print("Result: Suitable Internship")
    else:
        print("Result: Not Suitable Internship")
