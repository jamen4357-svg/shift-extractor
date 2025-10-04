import unittest
import os
import pandas as pd
from main import determine_time_shifts

def create_sample_xlsx(filepath):
    data = [
        {
            "Department Number": "0001",
            "Department Name": "Chinese",
            "Personnel ID": "CH015",
            "Employee Name": "WANG PING",
            "Time": "2025-09-25 06:51:01",
            "Verification": "Face",
            "Device": "FAC1245200002(CHECK-IN(KITCHEN))"
        },
        {
            "Department Number": "0001",
            "Department Name": "Chinese",
            "Personnel ID": "CH015",
            "Employee Name": "WANG PING",
            "Time": "2025-09-25 18:05:00",
            "Verification": "Face",
            "Device": "FAC1245200002(CHECK-OUT(KITCHEN))"
        },
        {
            "Department Number": "0001",
            "Department Name": "Chinese",
            "Personnel ID": "CH015",
            "Employee Name": "WANG PING",
            "Time": "2025-09-26 07:05:00",
            "Verification": "Face",
            "Device": "FAC1245200002(CHECK-IN(KITCHEN))"
        },
        {
            "Department Number": "0001",
            "Department Name": "Chinese",
            "Personnel ID": "CH015",
            "Employee Name": "WANG PING",
            "Time": "2025-09-26 18:00:00",
            "Verification": "Face",
            "Device": "FAC1245200002(CHECK-OUT(KITCHEN))"
        }
    ]
    df = pd.DataFrame(data)
    df.to_excel(filepath, index=False)

class TestTimeShiftCSV(unittest.TestCase):
    def setUp(self):
        self.xlsx_path = os.path.join(os.path.dirname(__file__), "sample_checkinout.xlsx")
        create_sample_xlsx(self.xlsx_path)
        self.records = pd.read_excel(self.xlsx_path).to_dict('records')

    def tearDown(self):
        if os.path.exists(self.xlsx_path):
            os.remove(self.xlsx_path)

    def test_time_shifts(self):
        shifts = determine_time_shifts(self.records)
        self.assertIn("CH015", shifts)
        self.assertEqual(shifts["CH015"]["name"], "WANG PING")
        # Should have two shifts for two days
        self.assertEqual(len(shifts["CH015"]["shifts"]), 2)
        # Check the first shift times
        self.assertEqual(shifts["CH015"]["shifts"][0][0], "06:51:01")
        self.assertEqual(shifts["CH015"]["shifts"][0][1], "18:05:00")
        # Check the second shift times
        self.assertEqual(shifts["CH015"]["shifts"][1][0], "07:05:00")
        self.assertEqual(shifts["CH015"]["shifts"][1][1], "18:00:00")

if __name__ == "__main__":
    unittest.main()
