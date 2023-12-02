import csv
import os
from datetime import timedelta

def sum_hours(time_strings):
    total_seconds = 0
    for time_string in time_strings:
        hours, minutes, seconds = map(int, time_string.split(':'))
        total_seconds += hours * 3600 + minutes * 60 + seconds

    # Calculate total hours, minutes, and seconds
    total_hours, remainder = divmod(total_seconds, 3600)
    total_minutes, total_seconds = divmod(remainder, 60)

    return f"{total_hours:02d}:{total_minutes:02d}:{total_seconds:02d}"

def return_total_hours():
    folder_path = './attachments/'
    for file in os.listdir(folder_path):
        if file.endswith('.csv'):
            first_csv_file = folder_path + file
            break  # Stop the loop after finding the first CSV file
    hms = []
    with open(first_csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if reader.line_num == 1:  # Check if it's the first iteration
                header = row
                continue
            hms.append(row[3]) # This will append each timer in the CSV file
        total_sum = sum_hours(hms)
        return total_sum

if __name__ == "__main__":
    return_total_hours()
