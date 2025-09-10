from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn2pmml import PMMLPipeline
import logging
import math
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load PMML model
# model = PMMLPipeline.load('internship_recommender.pmml')
model = None  # Temporary for testing

# Load vacancies and pincode data
vacancies_df = pd.read_csv('vacancies.csv')
pincode_df = pd.read_csv('pincode_latlon.csv')
pincode_map = pincode_df.set_index('pincode')[['latitude', 'longitude']].to_dict('index')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    logger.info(f"Received request: {data}")

    candidate = {
        'qualification': data['qualification'],
        'branch': data['branch'],
        'interest_emoji': data['interest_emoji'],
        'district_pin': data['pincode']
    }

    # Prepare data for all vacancies
    recs = []
    for _, vac in vacancies_df.iterrows():
        input_data = {
            'qualification': candidate['qualification'],
            'branch': candidate['branch'],
            'interest_emoji': candidate['interest_emoji'],
            'district_pin': candidate['district_pin'],
            'district_pin_vac': vac['pincode'],
            'min_qualification': vac['required_qualification'],
            'branch_wanted': vac['required_branch']
        }

        # Calculate distance
        pin1 = candidate['district_pin']
        pin2 = vac['pincode']
        if pin1 in pincode_map and pin2 in pincode_map:
            lat1, lon1 = pincode_map[pin1]['latitude'], pincode_map[pin1]['longitude']
            lat2, lon2 = pincode_map[pin2]['latitude'], pincode_map[pin2]['longitude']
            distance = haversine(lat1, lon1, lat2, lon2)
        else:
            distance = np.nan

        input_data['distance_km'] = distance

        # Create DataFrame for prediction
        df = pd.DataFrame([input_data])

        # Feature engineering
        qual_map = {'12th': 1, 'ITI': 2, 'Diploma': 3, 'BA': 4, 'B.Tech': 4, 'MBA': 5}
        df['qualification_numeric'] = df['qualification'].map(qual_map)
        df['min_qualification_numeric'] = df['min_qualification'].map(qual_map)
        df['R1_qual_met'] = (df['qualification_numeric'] >= df['min_qualification_numeric']).astype(int)
        df['R3_branch_match'] = ((df['branch'] == df['branch_wanted']) | (df['branch_wanted'].str.lower() == 'any')).astype(int)
        df['R2_dist_ok'] = (df['distance_km'] <= 100).astype(int)

        # Predict
        try:
            score = model.predict_proba(df[['qualification', 'branch', 'interest_emoji', 'distance_km', 'R1_qual_met', 'R2_dist_ok', 'R3_branch_match']])[0][1]
        except:
            score = 0.5  # default

        recs.append({
            'vacancy_id': vac['vacancy_id'],
            'title': vac['vacancy_title'],
            'required_qualification': vac['required_qualification'],
            'required_branch': vac['required_branch'],
            'pincode': vac['pincode'],
            'stipend': vac['stipend'],
            'distance_km': distance,
            'score': score
        })

    # Sort by score descending, take top 10
    recs.sort(key=lambda x: x['score'], reverse=True)
    top_recs = recs[:10]

    return jsonify({'recommendations': top_recs})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
