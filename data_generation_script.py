import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
random.seed(42)
np.random.seed(42)

# Define possible values
qualifications = ['12th', 'ITI', 'Diploma', 'BA', 'B.Tech', 'MBA']
branches = ['Mech', 'Elec', 'Civil', 'CS', 'Comm', 'Arts']
emojis = ['people', 'computer', 'books', 'design', 'finance', 'tools']
titles = ['Office Asst', 'Solar Tech', 'Site Engg', 'Marketing Exec', 'Data Analyst', 'HR Intern']

# Qualification mapping for logic
qual_map = {'12th': 1, 'ITI': 2, 'Diploma': 3, 'BA': 4, 'B.Tech': 4, 'MBA': 5}

# Generate 200,000 rows
num_rows = 200000

data = []

for i in range(num_rows):
    candidate_id = i + 1
    candidate_name = f"Candidate_{candidate_id}"
    qualification = random.choice(qualifications)
    branch = random.choice(branches)
    district_pin = random.randint(100000, 999999)
    interest_emoji = random.choice(emojis)

    vacancy_id = random.randint(1, 1000)  # Assume 1000 unique vacancies
    vacancy_title = random.choice(titles)
    min_qualification = random.choice(qualifications)
    branch_wanted = random.choice(branches + ['any'])
    district_pin_vac = random.randint(100000, 999999)
    stipend = random.randint(5000, 12000)

    # Simple logic for accepted: 1 if qual >= min_qual and branch match or any, else random
    qual_num = qual_map[qualification]
    min_qual_num = qual_map[min_qualification]
    branch_match = (branch == branch_wanted) or (branch_wanted == 'any')
    if qual_num >= min_qual_num and branch_match:
        accepted = 1 if random.random() > 0.3 else 0  # 70% chance if match
    else:
        accepted = 1 if random.random() > 0.9 else 0  # 10% chance if not

    data.append({
        'candidate_id': candidate_id,
        'candidate_name': candidate_name,
        'qualification': qualification,
        'branch': branch,
        'district_pin': district_pin,
        'interest_emoji': interest_emoji,
        'vacancy_id': vacancy_id,
        'vacancy_title': vacancy_title,
        'min_qualification': min_qualification,
        'branch_wanted': branch_wanted,
        'district_pin_vac': district_pin_vac,
        'stipend': stipend,
        'accepted': accepted
    })

df = pd.DataFrame(data)
df.to_csv('large_training_data.csv', index=False)
print("Generated large_training_data.csv with 200,000 rows.")
