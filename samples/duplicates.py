import pandas as pd

# Input and output files
input_file = "output.csv"
output_file = "output_no_duplicates.csv"

# Column to check for duplicates
key_column = "RXCUI"  # change this to the column name you want to base uniqueness on

# Read CSV
df = pd.read_csv(input_file)

# Drop duplicates, keeping the first occurrence
df_no_duplicates = df.drop_duplicates(subset=[key_column], keep="first")

# Save to new CSV
df_no_duplicates.to_csv(output_file, index=False)

print(f"✅ Duplicates removed based on '{key_column}'. Saved to '{output_file}'.")
