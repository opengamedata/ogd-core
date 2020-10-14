## import standard libraries
import json
import logging
import typing
import logging
## import local files
from models.DeathPredModel import SimpleDeathPredModel, SimpleFoodDeathPredModel, SimpleMoneyDeathPredModel
from models.SingleFeatureModel import SingleFeatureModel
from models.NthEventModel import NthEventModel
from models.LogisticModel import LogisticModel
from models.FeatSeqPercent import FeatSeqPercentModel
from models.FeatVelocity import FeatVelocityModel
from models.TimeSinceEventTypes import TimeSinceEventTypesModel
from models.PopulationModel import PopulationModel
from models.TownCompositionModel import TownCompositionModel
from models.DiagonalFarmDetectorModel import DiagonalFarmDetectorModel
from models.RecentPurchasesModel import RecentPurchasesModel
from models.MoneyAccumulationModel import MoneyAccumulationModel
from models.TimeSinceLastSaleModel import TimeSinceLastSaleModel
from models.MapSummaryModel import MapSummaryModel
import utils

## @class ModelManager
class ModelManager():
    def __init__(self, game_name):
        self._models = utils.loadJSONFile(filename=f"{game_name}_models.json", path="./models/")
        #print(f"In ModelManager, got the following list: {self._models}")
        # in the future, extend this with other ways of loading models.
    
    def AddModelInfo(self, model_info):
        self._models.append(model_info)

    def LoadModel(self, model_name: str):
        model_info = self._models[model_name]
        if model_info["type"] == "SingleFeature":
            return SingleFeatureModel(**model_info["params"])
        if model_info["type"] == "NthEvent":
            return NthEventModel(**model_info["params"])
        elif model_info["type"] == "Logistic":
            return LogisticModel(**model_info["params"])
        elif model_info["type"] == "SimpleDeathPrediction":
            return SimpleDeathPredModel(**model_info["params"])
        elif model_info["type"] == "FoodDeathPrediction":
            return SimpleFoodDeathPredModel(**model_info["params"])
        elif model_info["type"] == "MoneyDeathPrediction":
            return SimpleMoneyDeathPredModel(**model_info["params"])
        elif model_info["type"] == "BloomAchSeqPercent":
            return FeatSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "BloomAchVelocity":
            return FeatVelocityModel(**model_info["params"])
        elif model_info["type"] == "MoneyAchSeqPercent":
            return FeatSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "MoneyAchVelocity":
            return FeatVelocityModel(**model_info["params"])
        elif model_info["type"] == "PopAchSeqPercent":
            return FeatSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "PopAchVelocity":
            return FeatVelocityModel(**model_info["params"])
        elif model_info["type"] == "FarmAchSeqPercent":
            return FeatSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "FarmAchVelocity":
            return FeatVelocityModel(**model_info["params"])
        elif model_info["type"] == "ReqTutSeqPercent":
            return FeatSeqPercentModel(**model_info["params"])
        elif model_info["type"] == "ReqTutVelocity":
            return FeatVelocityModel(**model_info["params"])
        elif model_info["type"] == "TimeSinceImpact":
            return TimeSinceEventTypesModel(**model_info["params"])
        elif model_info["type"] == "TimeSinceActive":
            return TimeSinceEventTypesModel(**model_info["params"])
        elif model_info["type"] == "TimeSinceExploratory":
            return TimeSinceEventTypesModel(**model_info["params"])
        elif model_info["type"] == "TimeSinceLastFarmHouseDairy":
            return TimeSinceEventTypesModel(**model_info["params"])
        elif model_info["type"] == "Population":
            return PopulationModel(**model_info["params"])
        elif model_info["type"] == "TownComposition":
            return TownCompositionModel(**model_info["params"])
        elif model_info["type"] == "DiagonalFarmDetector":
            return DiagonalFarmDetectorModel(**model_info["params"])
        elif model_info["type"] == "RecentPurchases":
            return RecentPurchasesModel(**model_info["params"])
        elif model_info["type"] == "MoneyAccumulation":
            return MoneyAccumulationModel(**model_info["params"])
        elif model_info["type"] == "TimeSinceLastSale":
            return TimeSinceLastSaleModel(**model_info["params"])
        elif model_info["type"] == "MapSummary":
            return MapSummaryModel(**model_info["params"])

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
