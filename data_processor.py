import pandas as pd

def process_data(scores_path, emails_path, subjects):
    """Reads the Excel files, calculates class averages, and merges the data."""
    # Read Excel files, skipping the first row for scores
    scores_df = pd.read_excel(scores_path, skiprows=1)
    
    # Rename columns to match expected format
    scores_df = scores_df.rename(columns={
        'Name': 'Student Name',
        'User Id': 'Roll No',
        'P': 'Physics',
        'C': 'Chemistry',
        'M': 'Maths'
    })
    
    # Read emails and rename columns to what we expect
    emails_df = pd.read_excel(emails_path)
    
    # Map the email columns
    if 'email_id' in emails_df.columns:
        emails_df = emails_df.rename(columns={'email_id': 'Parent Email 1'})
    if 'email_id_1' in emails_df.columns:
        emails_df = emails_df.rename(columns={'email_id_1': 'Parent Email 1'})
    if 'email_id_2' in emails_df.columns:
        emails_df = emails_df.rename(columns={'email_id_2': 'Parent Email 2'})
        
    # User requested to add 'student_name' before email_id
    if 'student_name' in emails_df.columns:
        emails_df = emails_df.rename(columns={'student_name': 'Student Name'})
    elif 'name_of_parents' in emails_df.columns:
        emails_df = emails_df.rename(columns={'name_of_parents': 'Student Name'})
    
    # Ensure all requested subjects exist in the dataframe to avoid KeyError
    available_subjects = [sub for sub in subjects if sub in scores_df.columns]
    if len(available_subjects) < len(subjects):
        missing = set(subjects) - set(available_subjects)
        print(f"Warning: The following configured subjects were not found in the report: {missing}")

    # Keep only required columns in scores_df to avoid taking extra irrelevant subjects/columns
    required_cols = ['Student Name', 'Roll No'] + available_subjects
    scores_df = scores_df[[col for col in required_cols if col in scores_df.columns]]
    
    # Calculate Class Averages for subjects
    class_averages = scores_df[available_subjects].mean().round(1).to_dict()
    
    # Merge scores with emails on 'Student Name' securely as requested
    if 'Student Name' in emails_df.columns:
        merged_df = pd.merge(scores_df, emails_df, on='Student Name', how='left')
    else:
        # Fallback if somehow student_name is not found, merge on Roll No
        merged_df = pd.merge(scores_df, emails_df, on='Roll No', how='left')
    
    # Add rank calculation based on total marks
    merged_df['Total Marks'] = merged_df[available_subjects].sum(axis=1)
    merged_df['Rank'] = merged_df['Total Marks'].rank(ascending=False, method='min').astype(int)
    
    return merged_df, class_averages, available_subjects
