import csv

# Input and output file paths
input_file = "medicines.txt"
output_file = "output.csv"

# Open the input file and create the output file
with (
    open(input_file, "r", encoding="utf-8") as infile,
    open(output_file, "w", newline="", encoding="utf-8") as outfile,
):
    # Create CSV reader and writer
    reader = csv.reader(infile, delimiter="|")
    writer = csv.writer(outfile, delimiter=",", quoting=csv.QUOTE_MINIMAL)

    # Write each row from input to output
    for row in reader:
        writer.writerow(row)

print(f"✅ Conversion complete! '{output_file}' has been created.")
