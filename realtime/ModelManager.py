## import standard libraries
import json
import logging
import typing
import logging
## import local files
from models.SingleFeatureModel import SingleFeatureModel
import utils

## @class ModelManager
class ModelManager():
    def __init__(self, game_name):
        self._models = utils.loadJSONFile(filename=f"{game_name}_models.json", path="./models/")
        # in the future, extend this with other ways of loading models.
    
    def AddModelInfo(self, model_info):
        self._models.append(model_info)

    def LoadModel(self, model_name: str):
        model_info = self._models[model_name]
        if model_info["type"] == "SingleFeature":
            return SingleFeatureModel(**model_info["params"])
    
    def ListModels(self, level: int = None):
        if level is None:
            return list(self._models.keys())
        else:
            return [key for key in self._models.keys() if level in self._models[key]['levels']]