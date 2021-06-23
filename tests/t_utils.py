import datetime
import json
import logging
import os
import traceback
import typing
import unittest
from unittest import TestCase
# local import(s)
from config.config import settings
import utils

class t_utils(TestCase):
    def RunAll(self):
        self.test_loadJSONFile()
        print("Ran all t_utils tests.")

    def test_loadJSONFile(self):
        json_content = utils.loadJSONFile("t_utils.json", "./tests")
        self.assertEqual(json_content['first'], "the worst")
        self.assertEqual(json_content['second'], ["the best", "born, second place"])
        self.assertTrue("fourth" in json_content.keys())
        self.assertEqual(json_content['fourth']['a'], "why's it out of order?")
        self.assertEqual(json_content['fourth']['b'], 4)
        self.assertEqual(json_content['fourth']['c'], False)

if __name__ == '__main__':
    unittest.main()