import re
import pandas as pd
import argparse
from datetime import time
import os

def determine_shift(records):
    """
    Determines the shift (day or night) for each employee based on their check-in times.

    Args:
        records (list): A list of dictionaries, where each dictionary represents a record.

    Returns:
        dict: A dictionary mapping employee IDs to their name and determined shift.
    """
    employee_shifts = {}
    
    # Define shift boundaries
    DAY_SHIFT_START = time(7, 0)
    DAY_SHIFT_END = time(19, 0)

    for record in records:
        personnel_id = record.get("Personnel ID")
        employee_name = record.get("Employee Name")
        device_info = record.get("Device", "")
        
        if not personnel_id or "CHECK-IN" not in device_info:
            continue

        time_str = str(record.get("Time", "")).split(" ")[-1]
        if not re.match(r'\d{2}:\d{2}:\d{2}', time_str):
            continue
            
        check_in_time = time.fromisoformat(time_str)

        if personnel_id not in employee_shifts:
            employee_shifts[personnel_id] = {
                "name": employee_name,
                "day_check_ins": 0,
                "night_check_ins": 0
            }
        
        if DAY_SHIFT_START <= check_in_time < DAY_SHIFT_END:
            employee_shifts[personnel_id]["day_check_ins"] += 1
        else:
            employee_shifts[personnel_id]["night_check_ins"] += 1

    # Determine the dominant shift
    results = {}
    for pid, data in employee_shifts.items():
        shift = "Undetermined"
        if data["day_check_ins"] > data["night_check_ins"]:
            shift = "Day Shift"
        elif data["night_check_ins"] > data["day_check_ins"]:
            shift = "Night Shift"
        
        results[pid] = {
            "name": data["name"],
            "shift": shift
        }
        
    return results

def determine_time_shifts(records):
    """
    Determines the exact check-in and check-out time shifts for each employee.

    Args:
        records (list): A list of dictionaries, where each dictionary represents a record.

    Returns:
        dict: A dictionary mapping employee IDs to their name and a list of shifts.
    """
    employee_activity = {}

    for record in records:
        personnel_id = record.get("Personnel ID")
        if not personnel_id:
            continue

        employee_name = record.get("Employee Name")
        device_info = record.get("Device", "")
        
        try:
            time_record = pd.to_datetime(record.get("Time"))
            if pd.isna(time_record):
                continue
        except (ValueError, TypeError):
            continue
        
        date_str = time_record.date()
        time_val = time_record.time()

        if personnel_id not in employee_activity:
            employee_activity[personnel_id] = {"name": employee_name, "dates": {}}
        
        if date_str not in employee_activity[personnel_id]["dates"]:
            employee_activity[personnel_id]["dates"][date_str] = {"check_ins": [], "check_outs": []}

        if "CHECK-IN" in device_info:
            employee_activity[personnel_id]["dates"][date_str]["check_ins"].append(time_val)
        elif "CHECK-OUT" in device_info:
            employee_activity[personnel_id]["dates"][date_str]["check_outs"].append(time_val)

    employee_shifts = {}
    for pid, pdata in employee_activity.items():
        employee_shifts[pid] = {"name": pdata["name"], "shifts": []}
        for date, daily_activity in pdata["dates"].items():
            check_ins = sorted(daily_activity["check_ins"])
            check_outs = sorted(daily_activity["check_outs"])
            
            if check_ins and check_outs:
                # Simple pairing: first check-in with last check-out
                shift_start = check_ins[0]
                shift_end = check_outs[-1]
                employee_shifts[pid]["shifts"].append((shift_start.isoformat(), shift_end.isoformat()))
                
    return employee_shifts

def process_file(filepath, verbose=False, set_time_shift=False, csv_output=False, output_filename=None, start_row=None):
    """
    Reads an XLSX file, converts it to CSV, and determines employee shifts.

    Args:
        filepath (str): The path to the XLSX file.
        verbose (bool): If True, prints additional information.
        set_time_shift (bool): If True, determines exact time shifts.
        csv_output (bool): If True, outputs time shifts to a CSV file.
        output_filename (str): The name of the output CSV file.
    """
    try:
        # If start_row is provided, skip rows before it (Excel is 1-based, pandas is 0-based)
        if start_row is not None:
            df = pd.read_excel(filepath, skiprows=start_row-1)
        else:
            df = pd.read_excel(filepath)

        if verbose:
            csv_filepath = filepath.replace('.xlsx', '.csv')
            df.to_csv(csv_filepath, index=False)
            print(f"Successfully converted {filepath} to {csv_filepath}")

        records = df.to_dict('records')

        if set_time_shift:
            employee_shifts = determine_time_shifts(records)
            
            if csv_output or output_filename:
                output_data = []
                for pid, info in employee_shifts.items():
                    for shift_start, shift_end in info['shifts']:
                        output_data.append({
                            "Personnel ID": pid,
                            "Employee Name": info['name'],
                            "Shift Start": shift_start,
                            "Shift End": shift_end
                        })
                
                if not output_data:
                    if verbose:
                        print("No shift data to write to CSV.")
                    return

                output_df = pd.DataFrame(output_data)
                
                if output_filename:
                    out_csv_path = output_filename
                else:
                    base, _ = os.path.splitext(filepath)
                    out_csv_path = f"{base}_shifts.csv"
                
                output_df.to_csv(out_csv_path, index=False)
                if verbose:
                    print(f"Shift data successfully saved to {out_csv_path}")

            else:
                for pid, info in employee_shifts.items():
                    if info['shifts']:
                        print(f"Personnel ID: {pid}, Employee Name: {info['name']}, Possible Shifts: {info['shifts']}")
        else:
            employee_shifts = determine_shift(records)
            for pid, info in employee_shifts.items():
                print(f"Personnel ID: {pid}, Employee Name: {info['name']}, Shift: {info['shift']}")

    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Determine employee shifts from an XLSX file.")
    parser.add_argument("filepath", help="The path to the XLSX file.")
    parser.add_argument("--verbose", action="store_true", help="Print additional information.")
    parser.add_argument("--set-time-shift", action="store_true", help="Determine possible time shifts for each employee.")
    parser.add_argument("-csv", "--csv_output", action="store_true", help="Output the time shifts to a CSV file.")
    parser.add_argument("-o", "--output", help="Specify the output CSV file name.")
    parser.add_argument("--start-row", type=int, help="Specify the starting row (1-based) for reading the Excel file.")

    args = parser.parse_args()

    process_file(args.filepath, args.verbose, args.set_time_shift, args.csv_output, args.output, args.start_row)
