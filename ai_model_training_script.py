




import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_score
import lightgbm as lgb
from sklearn2pmml import sklearn2pmml, PMMLPipeline
import warnings

def main():
    """Main function to run the data processing, training, and export."""

    # 1. Load Data from the large training CSV
    file = "large_training_data.csv"

    print(f"Loading data from '{file}'...")
    try:
        df = pd.read_csv(file)
    except FileNotFoundError as e:
        print(f"Error: {e.filename} not found.")
        print("Please make sure the CSV file is in the same directory as the script.")
        return

    print(f"Dataset size: {len(df)} rows")

    # 2. Feature Engineering: Convert rules into model features
    print("\nEngineering features from recommendation rules...")

    # Rule R1: qualification >= min_qualification
    qualification_map = {
        '12th': 1, 'ITI': 2, 'Diploma': 3, 'BA': 4,
        'B.Tech': 4, 'MBA': 5
    }
    df['qualification_numeric'] = df['qualification'].map(qualification_map)
    df['min_qualification_numeric'] = df['min_qualification'].map(qualification_map)
    # Create a binary feature: 1 if candidate's qualification is sufficient, 0 otherwise.
    df['R1_qual_met'] = (df['qualification_numeric'] >= df['min_qualification_numeric']).astype(int)
    print("Created feature 'R1_qual_met' from Qualification rule.")

    # Rule R3: Branch match
    # Create a binary feature: 1 if branches match or if any branch is acceptable.
    df['R3_branch_match'] = ((df['branch'] == df['branch_wanted']) | (df['branch_wanted'].str.lower() == 'any')).astype(int)
    print("Created feature 'R3_branch_match' from Branch rule.")

    # Rule R2: distance_km <= 100
    # First, create the distance feature itself from pin codes.
    # Update to use haversine distance from lat/lon mapping
    import math

    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # Load pincode lat/lon mapping
    pincode_df = pd.read_csv('pincode_latlon.csv')
    pincode_map = pincode_df.set_index('pincode')[['latitude', 'longitude']].to_dict('index')

    def get_distance(row):
        pin1 = row['district_pin']
        pin2 = row['district_pin_vac']
        if pin1 in pincode_map and pin2 in pincode_map:
            lat1, lon1 = pincode_map[pin1]['latitude'], pincode_map[pin1]['longitude']
            lat2, lon2 = pincode_map[pin2]['latitude'], pincode_map[pin2]['longitude']
            return haversine(lat1, lon1, lat2, lon2)
        else:
            return np.nan

    df['distance_km'] = df.apply(get_distance, axis=1)
    # Create a binary feature: 1 if the distance is within the preferred 100km range.
    df['R2_dist_ok'] = (df['distance_km'] <= 100).astype(int)
    print("Created feature 'R2_dist_ok' from Distance rule.")


    # 3. Define features (X) and target (y) for the model
    print("\nPreparing data for model training...")

    # We include the original features PLUS our new rule-based features
    features_to_use = [
        'qualification', 'branch', 'interest_emoji', 'distance_km',
        'R1_qual_met', 'R2_dist_ok', 'R3_branch_match'
    ]

    # The 'candidate_name' column is not used for training.
    df.dropna(subset=features_to_use + ['accepted'], inplace=True)

    print(f"Final training set size after dropping rows with missing values: {len(df)} rows.")

    X = df[features_to_use]
    y = df['accepted'].astype(int)

    # 4. Define Preprocessing Steps
    categorical_features = ['qualification', 'branch']
    text_feature = 'interest_emoji'
    numeric_features = ['distance_km', 'R1_qual_met', 'R2_dist_ok', 'R3_branch_match']

    # Preprocessor now handles text (TF-IDF), categorical (OneHotEncode), and numeric (passthrough) features
    preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(norm=None), text_feature),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('numeric', 'passthrough', numeric_features)
        ]
    )

    # 5. Define the Model
    lgbm = lgb.LGBMClassifier(n_estimators=100, max_depth=8, subsample=0.8, colsample_bytree=0.8, random_state=42)

    # 6. Create the Full Pipeline
    pipeline = PMMLPipeline([
        ('preprocessor', preprocessor),
        ('classifier', lgbm)
    ])

    # 7. Split Data and Train the Model
    if y.nunique() < 2:
        print("\nWarning: Only one class ('accepted' or 'not accepted') present in the data.")
        print("Training cannot proceed with only one outcome.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("\nTraining the model pipeline...")
    pipeline.fit(X_train, y_train)
    print("Training complete.")

    # 8. Evaluate the Model
    print("\nEvaluating model performance...")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="X does not have valid feature names")
        y_pred = pipeline.predict(X_test)

    precision = precision_score(y_test, y_pred, zero_division=0)
    print(f"Precision on held-out test data: {precision:.2f}")

    # 9. Export the Model to PMML
    pmml_file_path = "internship_recommender.pmml"
    print(f"\nExporting the trained pipeline to {pmml_file_path}...")

    # Pass the original X_train DataFrame to sklearn2pmml
    sklearn2pmml(pipeline, pmml_file_path, with_repr=True)

    print("PMML export complete.")
    print("The file 'internship_recommender.pmml' is ready for deployment.")


if __name__ == "__main__":
    main()
