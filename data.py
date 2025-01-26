import pandas as pd

# Load the dataset
dataset = pd.read_csv('further_cleaned_questions_dataset.csv')

# Function to clean the specific column
def clean_column_data(value):
    # Split the data by lines and truncate at the first line that starts with a comma
    lines = value.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.lstrip().startswith(','):
            break
        cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

# Apply the cleaning function to the column (assuming the column name is 'data_column')
dataset['solutions'] = dataset['solutions'].apply(clean_column_data)

# Save the modified dataset to a new CSV file
dataset.to_csv('cleaned_file.csv', index=False)

# Optionally, display the first few rows to verify
print("Modified Dataset Preview:")
print(dataset.head())
