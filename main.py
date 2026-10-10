import os
import glob
import re
import pandas as pd
from dotenv import load_dotenv
from data_processor import process_data
from chart_generator import generate_bar_chart
from mailer import EmailSender

def get_rank_suffix(rank):
    if 11 <= (rank % 100) <= 13:
        return f"{rank}th"
    return f"{rank}{['th', 'st', 'nd', 'rd', 'th'][min(rank % 10, 4)]}"

def parse_test_name(filepath):
    filename = os.path.basename(filepath)
    # Search for "WT <number>" (case insensitive)
    match = re.search(r'WT\s*(\d+)', filename, re.IGNORECASE)
    if match:
        test_num = match.group(1)
        return f"Weekly Test-{test_num}"
    
    # Check for other abbreviations
    match_pt = re.search(r'PT\s*(\d+)', filename, re.IGNORECASE)
    if match_pt:
        return f"Part Test-{match_pt.group(1)}"
        
    match_ft = re.search(r'FT\s*(\d+)', filename, re.IGNORECASE)
    if match_ft:
        return f"Full Test-{match_ft.group(1)}"
        
    return "Weekly Test"

def main():
    load_dotenv()
    
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("Error: Missing email credentials in .env file.")
        return
        
    SUBJECTS_ENV = os.getenv('SUBJECTS', 'Physics,Chemistry,Maths')
    configured_subjects = [s.strip() for s in SUBJECTS_ENV.split(',')]
    
    max_marks_env = os.getenv('MAX_MARKS', '100')
    try:
        max_marks = int(max_marks_env)
    except ValueError:
        max_marks = 100
        
    # Dynamically find the Rank Report excel file
    scores_files = glob.glob('input_data/Rank-Report-*.xlsx')
    if not scores_files:
        print("Error: No scores file found matching 'input_data/Rank-Report-*.xlsx'")
        return
        
    scores_file = scores_files[0]
    emails_file = 'input_data/parent_emails.xlsx'
    
    if not os.path.exists(emails_file):
        print(f"Error: Emails file missing at {emails_file}")
        return
        
    test_name = parse_test_name(scores_file)
    print(f"Found scores file: {scores_file}")
    print(f"Parsed test name: {test_name}")
    
    print("Processing data...")
    merged_df, class_averages, subjects = process_data(scores_file, emails_file, configured_subjects)
    total_class_average = round(sum(class_averages.values()), 1)
    max_total = len(subjects) * max_marks
    
    with EmailSender(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD
    ) as mailer:
    
        for index, row in merged_df.iterrows():
            student_name = row['Student Name']
            roll_no = row['Roll No']
            rank = row['Rank']
            
            emails = []
            if 'Parent Email 1' in row and pd.notna(row['Parent Email 1']):
                emails.append(str(row['Parent Email 1']).strip())
            if 'Parent Email 2' in row and pd.notna(row['Parent Email 2']):
                emails.append(str(row['Parent Email 2']).strip())
                
            if not emails:
                print(f"Skipping {student_name} - No email found.")
                continue
                
            # Join emails with comma for SMTP
            parent_emails_str = ", ".join(emails)
            
            print(f"Generating report for {student_name} (Roll No: {roll_no})")
            
            # Prepare marks dictionary
            student_marks = {sub: row[sub] for sub in subjects}
            total_marks = row['Total Marks']
            
            # Generate Chart
            chart_path = generate_bar_chart(student_marks, class_averages, subjects, roll_no, student_name, max_marks)
            
            # Prepare template data
            template_data = {
                'student_name': student_name,
                'roll_no': roll_no,
                'rank_suffix': get_rank_suffix(rank),
                'subjects': subjects,
                'student_marks': student_marks,
                'class_averages': class_averages,
                'total_marks': total_marks,
                'total_class_average': total_class_average,
                'max_total': max_total,
                'test_name': test_name
            }
            
            # Create and Send Email
            msg = mailer.create_message(
                recipient_email=parent_emails_str,
                subject=f"Performance Report - {student_name} ({test_name})",
                template_data=template_data,
                chart_image_path=chart_path
            )
            
            # In a real run, this sends the email. For testing without credentials, we can comment it out.
            mailer.send_email(msg)
            
            # Cleanup chart image (optional)
            # if os.path.exists(chart_path):
            #    os.remove(chart_path)
            
    print("Done!")

if __name__ == "__main__":
    main()
