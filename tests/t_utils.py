import logging
import os
import traceback
import unittest
from pathlib import Path
from unittest import TestCase
# local import(s)
from utils import utils

class t_utils(TestCase):
    def RunAll(self):
        self.test_loadJSONFile()
        print("Ran all t_utils tests.")

    def test_loadJSONFile(self):
        json_content = utils.loadJSONFile(filename="t_utils.json", path=Path("./tests"))
        self.assertEqual(json_content['first'], "the worst")
        self.assertEqual(json_content['second'], ["the best", "born, second place"])
        self.assertTrue("fourth" in json_content.keys())
        self.assertEqual(json_content['fourth']['a'], "why's it out of order?")
        self.assertEqual(json_content['fourth']['b'], 4)
        self.assertEqual(json_content['fourth']['c'], False)

if __name__ == '__main__':
    unittest.main()