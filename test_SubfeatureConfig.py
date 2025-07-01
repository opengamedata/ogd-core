# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.generators.SubfeatureConfig import SubfeatureConfig
from tests.config.t_config import settings

@unittest.skip("Not implemented")
class test_SubfeatureConfig(TestCase):
    """Testbed for the DetectorConfig class.

        TODO : Implement tests
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        _elems = {
            "threshold": 30,
            "enabled": True,
            "type": "ActiveTime",
            "description": "Active time of a player",
            "return_type": "timedelta",
            "subfeatures": {
                "Seconds": {
                    "description": "The number of seconds of active time.",
                    "return_type": "int"
                }
            }
        }
        # cls.test_schema = SubfeatureConfig(
        #     name="ActiveTime Schema",
        #     unparsed_elements=_elems
        # )

    @staticmethod
    def RunAll():
        pass

    @unittest.skip("Not implemented")
    def test_Name(self):
        # _str = self.test_schema.Name
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "ActiveTime Schema")
        pass

    @unittest.skip("Not implemented")
    def test_TypeName(self):
        # _str = self.test_schema.TypeName
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "ActiveTime")
        pass

    @unittest.skip("Not implemented")
    def test_Enabled(self):
        # _enabled = self.test_schema.Enabled
        # self.assertIsInstance(_enabled, bool)
        # self.assertEqual(_enabled, True)
        pass

    @unittest.skip("Not implemented")
    def test_Description(self):
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "Active time of a player")
        pass

    @unittest.skip("Not implemented")
    def test_ReturnType(self):
        # _str = self.test_schema.ReturnType
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "timedelta")
        pass

    @unittest.skip("Not implemented")
    def test_Subfeatures(self):
        # _feats = self.test_schema.Subfeatures
        # seconds = _feats.get("Seconds")
        # _ret  = "int"
        # _desc = "The number of seconds of active time."
        # self.assertIsInstance(_feats, dict)
        # self.assertIsNotNone(seconds)
        # if seconds is not None:
        #     self.assertEqual(seconds.Name, "Seconds")
        #     self.assertEqual(seconds.ReturnType, _ret)
        #     self.assertEqual(seconds.Description, _desc)
        pass

    @unittest.skip("Not implemented")
    def test_NonStandardElements(self):
        # _elems = {
        #     "threshold":30
        # }
        # self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        # self.assertEqual(self.test_schema.NonStandardElements, _elems)
        pass

    @unittest.skip("Not implemented")
    def test_NonStandardElementNames(self):
        # _elem_names = ["threshold"]
        # self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        # self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)
        pass

    @unittest.skip("Not implemented")
    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "threshold": 30,
            "enabled": True,
            "type": "ActiveTime",
            "description": "Active time of a player",
            "return_type": "timedelta",
            "subfeatures": {
                "Seconds": {
                    "description": "The number of seconds of active time.",
                    "return_type": "int"
                }
            }
        }
        # _schema = DetectorConfig.FromDict(name="ActiveTime Schema", unparsed_elements=_dict)
        # self.assertIsInstance(_schema.Name, str)
        # self.assertEqual(_schema.Name, "ActiveTime Schema")
        # self.assertIsInstance(_schema.TypeName, str)
        # self.assertEqual(_schema.TypeName, "ActiveTime")
        # self.assertIsInstance(_schema.Enabled, bool)
        # self.assertEqual(_schema.Enabled, True)
        # self.assertIsInstance(_schema.Description, str)
        # self.assertEqual(_schema.Description, "Active time of a player")
        pass

if __name__ == '__main__':
    unittest.main()
