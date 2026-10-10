import matplotlib.pyplot as plt
import io
import os
import numpy as np

def generate_bar_chart(student_marks, class_averages, subjects, roll_no, student_name, max_marks=100):
    """
    Generates a comparative bar chart and saves it as an image file.
    Returns the file path of the generated image.
    """
    os.makedirs('temp_charts', exist_ok=True)
    
    student_scores = [student_marks[sub] for sub in subjects]
    average_scores = [class_averages[sub] for sub in subjects]
    
    x = np.arange(len(subjects))
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(8, 4))
    
    # Colors matching the reference image: Bright Blue for student, Light Gray for class
    student_color = '#0073E6'
    class_color = '#C0C0C0'
    
    rects1 = ax.bar(x - width/2, student_scores, width, label=f"{student_name}'s Marks", color=student_color)
    rects2 = ax.bar(x + width/2, average_scores, width, label='Class Average', color=class_color)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_title(f'Your Child vs Class Average (out of {max_marks})', fontsize=14, color='#555555', pad=20, weight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(subjects, color='#555555')
    
    # Customize grid and spines
    ax.set_ylim(0, max_marks)
    
    # Dynamically set y-ticks based on max_marks to avoid too many ticks
    step = max(10, max_marks // 10)
    ax.set_yticks(np.arange(0, max_marks + 1, step))
    ax.grid(axis='y', linestyle='-', alpha=0.3, color='#AAAAAA')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')
    
    # Customize legend
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False, labelcolor='#555555')

    fig.tight_layout()
    
    chart_path = f'temp_charts/chart_{roll_no}.png'
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return chart_path
