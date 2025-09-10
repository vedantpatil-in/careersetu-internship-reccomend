# Internship Recommender System - Admin Guide

## Overview
This system recommends internships to candidates based on their qualifications, branch, location, and interests using a machine learning model.

## Setup

### Prerequisites
- Python 3.9+
- Docker and Docker Compose
- Git

### Installation
1. Clone the repository.
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Run data generation scripts if needed.
4. Train the model: `python ai_model_training_script.py`
5. For Docker: `docker-compose up --build`

### Data Files
- `large_training_data.csv`: Training data
- `vacancies.csv`: Vacancy details
- `pincode_latlon.csv`: Pincode to lat/lon mapping
- `internship_recommender.pmml`: Trained model

### Maintenance
- Retrain model periodically with new data.
- Update pincode mappings if needed.
- Monitor logs in backend.

## API Endpoints
- POST /recommend: Get recommendations
- GET /health: Health check
