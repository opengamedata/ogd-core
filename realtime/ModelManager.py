## import standard libraries
import json
import logging
import typing
import logging
## import local files
from models.SimpleDeathPredictionModel import SimpleDeathPredictionModel
from models.SingleFeatureModel import SingleFeatureModel
from models.LogisticModel import LogisticModel
from models.Lakeland_featseq_velocity import FarmAchSeqPercentModel, FarmAchVelocityModel
from models.Lakeland_featseq_velocity import BloomAchSeqPercentModel, BloomAchVelocityModel
from models.Lakeland_featseq_velocity import MoneyAchSeqPercentModel, MoneyAchVelocityModel
from models.Lakeland_featseq_velocity import PopAchSeqPercentModel, PopAchVelocityModel
from models.Lakeland_featseq_velocity import ReqTutSeqPercentModel, ReqTutVelocityModel
import utils

## @class ModelManager
class ModelManager():
    def __init__(self, game_name):
        self._models = utils.loadJSONFile(filename=f"{game_name}_models.json", path="./models/")
        print(f"In ModelManager, got the following list: {self._models}")
        # in the future, extend this with other ways of loading models.
    
    def AddModelInfo(self, model_info):
        self._models.append(model_info)

    def LoadModel(self, model_name: str):
        model_info = self._models[model_name]
        if model_info["type"] == "SingleFeature":
            return SingleFeatureModel(**model_info["params"])
        elif model_info["type"] == "Logistic":
            return LogisticModel(**model_info["params"])
        elif model_info["type"] == "SimpleDeathPrediction":
            return SimpleDeathPredictionModel(**model_info["params"])
        elif model_info["type"] == "BloomAchSeqPercent":
            return BloomAchSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "BloomAchVelocity":
            return BloomAchVelocityModel(**model_info["params"])
        elif model_info["type"] == "MoneyAchSeqPercent":
            return MoneyAchSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "MoneyAchVelocity":
            return MoneyAchVelocityModel(**model_info["params"])
        elif model_info["type"] == "PopAchSeqPercent":
            return PopAchSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "PopAchVelocity":
            return PopAchVelocityModel(**model_info["params"])
        elif model_info["type"] == "FarmAchSeqPercent":
            return FarmAchSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "FarmAchVelocity":
            return FarmAchVelocityModel(**model_info["params"])
        elif model_info["type"] == "ReqTutSeqPercent":
            return ReqTutSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "ReqTutVelocity":
            return ReqTutVelocityModel(**model_info["params"])

    def _validLevel(self, model_name: str, level: int):
        # print(f"Checking validity of model {model_name} for level {level}")
        levels = self._models[model_name]["levels"]
        if levels == None or levels == []:
            return True
        elif level in levels:
            return True
        else:
            return False
    
    def ListModels(self, level: int = None):
        if level is None:
            return list(self._models.keys())
        else:
            valid_models = [key for key in self._models.keys() if self._validLevel(model_name=key, level=level)]
            # print(f"Listing models for level {level}: {valid_models}")
            return valid_models