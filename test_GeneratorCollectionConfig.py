# import libraries
import logging
import unittest
from unittest import TestCase
# import ogd libraries.
from ogd.common.configs.TestConfig import TestConfig
from ogd.common.utils.Logger import Logger
# import locals
from src.ogd.common.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from src.ogd.common.configs.generators.DetectorMapConfig import DetectorMapConfig
from src.ogd.common.configs.generators.FeatureMapConfig import FeatureMapConfig
from tests.config.t_config import settings

class test_GeneratorCollectionConfig(TestCase):
    """Testbed for the GeneratorCollectionConfig class.

        TODO : Implement and enable tests.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # 1. Get testing config
        _testing_cfg = TestConfig.FromDict(name="SchemaTestConfig", unparsed_elements=settings)
        _level     = logging.DEBUG if _testing_cfg.Verbose else logging.INFO
        Logger.std_logger.setLevel(_level)

        # 2. Set up local instance of testing class
        cls.test_schema = GeneratorCollectionConfig(
            name="available_building Schema", game_id="FakeGame",
            detector_map=DetectorMapConfig.Default(), extractor_map=FeatureMapConfig.Default(),
            subunit_range=range(0,2), other_ranges={},
            other_elements={ "foo":"bar" }
        )

    @staticmethod
    def RunAll():
        pass

    def test_Name(self):
        _str = self.test_schema.Name
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "available_building Schema")

    def test_GameName(self):
        _str = self.test_schema.GameName
        self.assertIsInstance(_str, str)
        self.assertEqual(_str, "FakeGame")

    @unittest.skip("Not implemented")
    def test_Detectors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_DetectorNames(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_PerCountDetectors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_AggregateDetectors(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_Features(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_FeatureNames(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_LegacyPerLevelFeatures(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_PerCountFeatures(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_AggregateFeatures(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_LevelRange(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_OtherRanges(self):
        pass
        # _str = self.test_schema.Description
        # self.assertIsInstance(_str, str)
        # self.assertEqual(_str, "The buildings available for the player to construct")

    @unittest.skip("Not implemented")
    def test_NonStandardElements(self):
        _elems = {
            "foo":"bar"
        }
        self.assertIsInstance(self.test_schema.NonStandardElements, dict)
        self.assertEqual(self.test_schema.NonStandardElements, _elems)

    @unittest.skip("Not implemented")
    def test_NonStandardElementNames(self):
        _elem_names = ["foo"]
        self.assertIsInstance(self.test_schema.NonStandardElementNames, list)
        self.assertEqual(self.test_schema.NonStandardElementNames, _elem_names)

    @unittest.skip("Not implemented")
    def test_FromDict(self):
        """Test case for whether the FromDict function is working properly.
        """
        _dict = {
            "features": {
                "per_count": {
                    "MoveShapeCount": {
                        "type": "MoveShapeCount",
                        "enabled": True,
                        "description":"Total number of shape moves in a given session",
                        "return_type": "int"
                    }
                },
                "aggregate":{
                    "SessionID": {
                        "type": "SessionID",
                        "enabled": True,
                        "description":"The player's session ID number for this play session",
                        "return_type": "str"
                    },
                    "FunnelByUser": {
                        "type": "FunnelByUser",
                        "enabled": False,
                        "description":"Funnel of puzzles for this play session",
                        "return_type": "List[float | int]"
                    },
                    "LevelsOfDifficulty": {
                        "type": "LevelsOfDifficulty",
                        "enabled": True,
                        "description":"Set of features for each level describing the difficulty of a puzzle (on-going-work)",
                        "return_type": "List[bool | int | timedelta]"
                    },
                    "SequenceBetweenPuzzles": {
                        "type": "SequenceBetweenPuzzles",
                        "enabled": False,
                        "description":"Sequence of puzzles and its funnel stage reached of a given session"
                    }
                }
            },

            "config": {
                "SUPPORTED_VERS": [1]
            }
        }
        _schema = GeneratorCollectionConfig.FromDict(name="available_buildings Schema", unparsed_elements=_dict)
        self.assertIsInstance(_schema.Name, str)
        self.assertEqual(_schema.Name, "available_buildings Schema")

if __name__ == '__main__':
    unittest.main()
