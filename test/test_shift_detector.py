import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import determine_shift

class TestShiftDetector(unittest.TestCase):

    def test_day_shift_employee(self):
        """Test for an employee who predominantly works the day shift."""
        data = [
            {"Personnel ID": "D001", "Employee Name": "Day Worker", "Time": "2025-09-25 08:00:00", "Device": "CHECK-IN"},
            {"Personnel ID": "D001", "Employee Name": "Day Worker", "Time": "2025-09-26 09:00:00", "Device": "CHECK-IN"},
            {"Personnel ID": "D001", "Employee Name": "Day Worker", "Time": "2025-09-27 20:00:00", "Device": "CHECK-IN"},
        ]
        result = determine_shift(data)
        self.assertEqual(result["D001"]["shift"], "Day Shift")

    def test_night_shift_employee(self):
        """Test for an employee who predominantly works the night shift."""
        data = [
            {"Personnel ID": "N001", "Employee Name": "Night Worker", "Time": "2025-09-25 20:00:00", "Device": "CHECK-IN"},
            {"Personnel ID": "N001", "Employee Name": "Night Worker", "Time": "2025-09-26 21:00:00", "Device": "CHECK-IN"},
            {"Personnel ID": "N001", "Employee Name": "Night Worker", "Time": "2025-09-27 08:00:00", "Device": "CHECK-IN"},
        ]
        result = determine_shift(data)
        self.assertEqual(result["N001"]["shift"], "Night Shift")

    def test_undetermined_shift(self):
        """Test for an employee with an equal number of day and night check-ins."""
        data = [
            {"Personnel ID": "U001", "Employee Name": "Undetermined Worker", "Time": "2025-09-25 08:00:00", "Device": "CHECK-IN"},
            {"Personnel ID": "U001", "Employee Name": "Undetermined Worker", "Time": "2025-09-26 20:00:00", "Device": "CHECK-IN"},
        ]
        result = determine_shift(data)
        self.assertEqual(result["U001"]["shift"], "Undetermined")

    def test_no_check_in_records(self):
        """Test with data that contains no CHECK-IN records."""
        data = [
            {"Personnel ID": "C001", "Employee Name": "Checkout Worker", "Time": "2025-09-25 18:00:00", "Device": "CHECK-OUT"},
        ]
        result = determine_shift(data)
        self.assertEqual(len(result), 0)

    def test_empty_data(self):
        """Test with an empty list of records."""
        data = []
        result = determine_shift(data)
        self.assertEqual(len(result), 0)

    def test_missing_personnel_id(self):
        """Test records with missing 'Personnel ID'."""
        data = [
            {"Employee Name": "No ID", "Time": "2025-09-25 08:00:00", "Device": "CHECK-IN"},
        ]
        result = determine_shift(data)
        self.assertEqual(len(result), 0)

    def test_invalid_time_format(self):
        """Test records with invalid time format."""
        data = [
            {"Personnel ID": "T001", "Employee Name": "Invalid Time", "Time": "2025-09-25", "Device": "CHECK-IN"},
        ]
        result = determine_shift(data)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()
