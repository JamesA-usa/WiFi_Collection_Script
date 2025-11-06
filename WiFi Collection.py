# wifi collection

import subprocess
import time
import pandas as pd
import os

# Configuration parameters
password = "kali"
interface = "wlan0"
interface2 = "wlan0mon"


def start_monitor_mode():
    """Puts device into monitor mode"""
    command = f"echo {password} | sudo -S airmon-ng start {interface}"
    subprocess.run(command, shell=True, check=True)
    print(f"Monitor mode enabled for {interface}. New interface is {interface2}.")
    print(" ")

    # Kill processes
    command = f"echo {password} | sudo -S airmon-ng check kill"
    subprocess.run(command, shell=True, check=True)
    print("Processes killed.")
    print(" ")


def scan_networks(duration):
    """
    Scan for wireless networks for a specified duration

    Args:
        duration: Number of seconds to run the scan

    Returns:
        elapsed_time: Actual time spent on scanning
    """
    print(f"\nStarting airodump-ng on {interface2}...")
    print(f"Scanning for {duration} seconds...\n")

    # Command to run airodump-ng with CSV output
    command = f"echo {password} | sudo -S airodump-ng {interface2} --write scan_results --output-format csv"

    # Execute the command
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    try:
        # Let it run for the specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            # Read output to prevent buffer overflow
            line = process.stdout.readline()
            if line:
                print(line, end='')

            # Check if process is still running
            if process.poll() is not None:
                break

            time.sleep(0.1)

        elapsed_time = time.time() - start_time
        print(f"\nScan completed in {elapsed_time:.2f} seconds.")
        return elapsed_time

    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
    finally:
        if process and process.poll() is None:  # Ensure the process is terminated
            process.terminate()
            process.wait()


def stop_monitor_mode():
    """Stops monitor mode and returns to managed mode"""
    command = f"echo {password} | sudo -S airmon-ng stop {interface2}"
    subprocess.run(command, shell=True, check=True)
    print(f"Monitor mode stopped.")
    print(" ")


def convert_csv_to_excel():
    """Convert CSV scan results to Excel format"""
    csv_file = "scan_results-01.csv"
    excel_file = "scan_results.xlsx"

    try:
        if os.path.exists(csv_file):
            print(f"Converting {csv_file} to Excel format...")
            data = pd.read_csv(csv_file, skip_blank_lines=True, engine="python", error_bad_lines=False)
            data.to_excel(excel_file, index=False)
            print(f"Excel file saved as {excel_file}.")
        else:
            print(f"Error: The CSV file '{csv_file}' does not exist.")
    except Exception as e:
        print(f"An unexpected error occurred during Excel conversion: {e}")


if __name__ == "__main__":
    try:
        # Get duration from user
        max_time = int(input('Enter the amount of seconds you want to run this: '))

        # Start monitor mode
        start_monitor_mode()

        # Scan networks for the specified duration
        elapsed = scan_networks(max_time)
        print(f"Total scan time: {elapsed:.2f} seconds")

        # Convert results to Excel
        convert_csv_to_excel()

    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always ensure monitor mode is stopped before exiting
        stop_monitor_mode()
        print("Program terminated.")

    try:
        # Read the CSV file that was actually created
        df = pd.read_csv("scan_results-01.csv", skipinitialspace=True)

        print("Available columns:", df.columns.tolist())

        # Clean up column names by stripping whitespace
        df.columns = df.columns.str.strip()

        # Create a mapping of column names (case-insensitive)
        column_map = {col.lower(): col for col in df.columns}

        # Define the columns we want and find their actual names
        desired_columns = ['bssid', 'essid', 'privacy', 'cipher', 'authentication']
        actual_columns = []

        for col in desired_columns:
            if col.lower() in column_map:
                actual_columns.append(column_map[col.lower()])
            else:
                print(f"Warning: Column '{col}' not found in the CSV file")

        # Filter DataFrame to only include available desired columns
        if actual_columns:
            df = df[actual_columns]

            # Save to Excel
            df.to_excel('scan_results.xlsx', index=False)
            print("Data saved to scan_results.xlsx")
            print(df.head())
        else:
            print("No matching columns found in the CSV file")

    except FileNotFoundError:
        print("Error: scan_results-01.csv not found. The scan may not have generated output.")
    except Exception as e:
        print(f"An error occurred: {e}")

    df = pd.read_excel('scan_results.xlsx')
    all = df[['BSSID', 'ESSID', 'Privacy', 'Cipher', 'Authentication']]
    wpa2 = all[all['Privacy'] == 'WPA2']

    os.remove('scan_results-01.csv')
    os.remove('scan_results.xlsx')
    all.to_csv('scanall.csv')
    wpa2.to_csv('wpa2.csv')

    print("WiFi Scan Complete!")

