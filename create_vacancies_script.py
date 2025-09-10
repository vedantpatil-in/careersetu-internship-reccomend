import pandas as pd

# Load the large training data
df = pd.read_csv('large_training_data.csv')

# Extract unique vacancies
vacancies_df = df[['vacancy_id', 'vacancy_title', 'min_qualification', 'branch_wanted', 'district_pin_vac', 'stipend']].drop_duplicates(subset='vacancy_id')

# Rename columns for clarity
vacancies_df = vacancies_df.rename(columns={
    'district_pin_vac': 'pincode',
    'min_qualification': 'required_qualification',
    'branch_wanted': 'required_branch'
})

# Save to CSV
vacancies_df.to_csv('vacancies.csv', index=False)
print("Created vacancies.csv with unique vacancies.")
