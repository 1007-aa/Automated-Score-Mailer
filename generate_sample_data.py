import pandas as pd
import os

def create_sample_data():
    os.makedirs('input_data', exist_ok=True)

    # 1. Scores Data
    scores_data = {
        'Roll No': [202811, 202812, 202813],
        'Student Name': ['Sia Khanna', 'Rahul Sharma', 'Ananya Patel'],
        'Physics': [55, 80, 45],
        'Chemistry': [15, 60, 75],
        'Maths': [40, 85, 90]
    }
    scores_df = pd.DataFrame(scores_data)
    scores_df.to_excel('input_data/student_scores.xlsx', index=False)
    print("Created input_data/student_scores.xlsx")

    # 2. Emails Data
    emails_data = {
        'Roll No': [202811, 202812, 202813],
        'Parent Email': ['sia.parent@example.com', 'rahul.parent@example.com', 'ananya.parent@example.com']
    }
    emails_df = pd.DataFrame(emails_data)
    emails_df.to_excel('input_data/parent_emails.xlsx', index=False)
    print("Created input_data/parent_emails.xlsx")

if __name__ == "__main__":
    create_sample_data()
