import re
import os
import time
from tqdm import tqdm  # Progress bar library

# Function to extract valid SMTP lines from the list
def extract_smtp_info(line):
    smtp_pattern = re.compile(r"(smtp://|https?://)?(?P<host>[^:/]+)(:(?P<port>\d+))?[:/]?(?P<user>[^:@]+)@(?P<domain>[^:]+)(:(?P<pass>[^:@/]+))?")
    
    match = smtp_pattern.search(line.strip())
    if match:
        host = match.group("host")
        # Extract the full host (e.g., smtp.office365.com)
        full_host = host if host else None
        port = match.group("port") if match.group("port") else "587"
        user = f"{match.group('user')}@{match.group('domain')}"
        password = match.group("pass")

        if full_host and user and password:
            return full_host, f"{full_host}|{port}|{user}|{password}"
    return None, None

# Function to get the SMTP file from the user
def get_smtp_file():
    file_path = input("Please enter the path to the SMTP file (e.g., 'smtps.txt'): ").strip()
    try:
        return open(file_path, 'r', encoding='utf-8')
    except (FileNotFoundError, UnicodeDecodeError) as e:
        print(f"Error: {e}")
        return None

# Function to save SMTP entries to host-specific and combined files
def save_to_files(smtp_entries_by_host, combined_file_path):
    output_dir = "smtp_output"
    os.makedirs(output_dir, exist_ok=True)

    combined_file = open(combined_file_path, 'w', encoding='utf-8')

    try:
        for host, entries in smtp_entries_by_host.items():
            host_file_path = os.path.join(output_dir, f"{host}.txt")
            with open(host_file_path, 'w', encoding='utf-8') as host_file:
                for entry in entries:
                    host_file.write(entry + '\n')
                    combined_file.write(entry + '\n')
    finally:
        combined_file.close()

    print(f"\nOutput files saved to '{output_dir}' folder.")
    print(f"All results saved to '{combined_file_path}'.")

# Main function to read the file, process SMTP entries, and write to output
def main():
    smtp_file = get_smtp_file()
    if not smtp_file:
        return

    smtp_entries_by_host = {}
    combined_file_path = "all_results.txt"

    # Count total lines for the progress bar
    total_lines = sum(1 for line in smtp_file)
    smtp_file.seek(0)  # Reset file pointer to the start

    # Process each line with a progress bar
    for line in tqdm(smtp_file, total=total_lines, desc="Processing SMTP Entries"):
        host, smtp_entry = extract_smtp_info(line)
        if host and smtp_entry:
            if host not in smtp_entries_by_host:
                smtp_entries_by_host[host] = []
            smtp_entries_by_host[host].append(smtp_entry)

    smtp_file.close()  # Close the input file after processing

    if smtp_entries_by_host:
        save_to_files(smtp_entries_by_host, combined_file_path)
    else:
        print("No valid SMTP entries found.")

# Run the script with timing and a progress bar
if __name__ == "__main__":
    start_time = time.time()  # Start the timer
    main()
    end_time = time.time()  # End the timer
    print(f"\nExecution Time: {end_time - start_time:.2f} seconds")
