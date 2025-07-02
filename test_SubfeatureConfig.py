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
        cls.test_schema = SubfeatureConfig(
            name="Seconds",
            return_type="int",
            description="The number of seconds of active time.",
            other_elements={"foo":"bar"}
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "Seconds")
        pass


    def test_Description(self):
        _str = self.test_schema.Description
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "The number of seconds of active time.")
        pass

    def test_ReturnType(self):
        _str = self.test_schema.ReturnType
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "int")
        pass

    def test_NonStandardElements(self):
        _elems = { "foo":"bar" }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)
        pass

    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)
        pass

    @unittest.skip("Not implemented")
    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "description": "The number of seconds of active time.",
            "return_type": "int",
            "foo":"bar"
        }
        _schema = SubfeatureConfig.FromDict(name="Seconds", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "Seconds")
        self.assertIsInstance(_schema.Description, str)
        self.assertEqual(_schema.Description, "Active time of a player")
        self.assertIsInstance(_schema.ReturnType, str)
        self.assertEqual(_schema.ReturnType, "int")
        self.assertIsInstance(_schema.NonStandardElements, dict)
        self.assertEqual(_schema.NonStandardElements, {"foo":"bar"})
        self.assertIsInstance(_schema.NonStandardElementNames, list)
        self.assertEqual(_schema.NonStandardElementNames, ["foo"])
        pass

if __name__ == '__main__':
    unittest.main()
