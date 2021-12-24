import unittest

from helper import adjust_data


class Test12weeksData(unittest.TestCase):
    
    # Check if all the spots for "missed weeks" data are being filled with zeros. 
    # It is needed for correct work of a "12 weeks" chart.
    def test_12weeks(self):
        week_of_year_for_data = [[2, 2021], [3, 2021], [5, 2021], [8, 2021]]
        raw_these_12weeks_d = [1, 2, 3, 4]
        week_of_year_for_labels = [[1, 2021], [2, 2021], [3, 2021], [4, 2021], [5, 2021], [6, 2021], [7, 2021], [8, 2021], [9, 2021]]
        result = adjust_data(week_of_year_for_data, raw_these_12weeks_d, week_of_year_for_labels)
        self.assertEqual(result, [0, 1, 2, 0, 3, 0, 0, 4, 0])
        
        
if __name__ == '__main__':
    unittest.main()
    
