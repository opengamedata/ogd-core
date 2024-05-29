# standard imports
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Optional

# ogd imports
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

# local imports
from ogd.core.schemas.datasets.DatasetSchema import DatasetSchema

class FileListConfigSchema(Schema):
    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._files_base     : Optional[str]
        self._templates_base : Optional[str]
        if not isinstance(all_elements, dict):
            all_elements = {}
        if "files_base" in all_elements.keys():
            self._files_base = FileListConfigSchema._parseFilesBase(all_elements["files_base"])
        else:
            self._files_base = None
        if "templates_base" in all_elements.keys():
            self._templates_base = FileListConfigSchema._parseTemplatesBase(all_elements["templates_base"])
        else:
            self._templates_base = None
        _used = {"files_base", "templates_base"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        super().__init__(name=name, other_elements=_leftovers)

    def __str__(self) -> str:
        return str(self.Name)

    @property
    def FilesBase(self) -> Optional[str]:
        return self._files_base
    @property
    def TemplatesBase(self) -> Optional[str]:
        return self._templates_base
    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @staticmethod
    def EmptySchema() -> "FileListConfigSchema":
        return FileListConfigSchema(name="CONFIG NOT FOUND", all_elements={})

    @staticmethod
    def _parseFilesBase(files_base) -> str:
        ret_val : str
        if isinstance(files_base, str):
            ret_val = files_base
        else:
            ret_val = str(files_base)
            Logger.Log(f"Filepath base was unexpected type {type(files_base)}, defaulting to str(files_name)={ret_val}.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseTemplatesBase(templates_base) -> str:
        ret_val : str
        if isinstance(templates_base, str):
            ret_val = templates_base
        else:
            ret_val = str(templates_base)
            Logger.Log(f"Templates base was unexpected type {type(templates_base)}, defaulting to str(templates_name)={ret_val}.", logging.WARN)
        return ret_val

class GameDatasetCollectionSchema(Schema):
    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._game_datasets : Dict[str, DatasetSchema]

        if not isinstance(all_elements, dict):
            all_elements = {}
        self._game_datasets = GameDatasetCollectionSchema._parseGameDatasets(datasets=all_elements)
        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return str(self.Name)

    # *** Properties ***

    @property
    def Datasets(self) -> Dict[str, DatasetSchema]:
        return self._game_datasets
    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    @staticmethod
    def EmptySchema() -> "GameDatasetCollectionSchema":
        return GameDatasetCollectionSchema(name="DATASET COLLECTION NOT FOUND", all_elements={})

    @staticmethod
    def _parseGameDatasets(datasets:Dict[str, Any]) -> Dict[str, DatasetSchema]:
        ret_val : Dict[str, DatasetSchema]
        if isinstance(datasets, dict):
            ret_val = {
                key : DatasetSchema(key, dataset if isinstance(dataset, dict) else {})
                for key,dataset in datasets.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"Collection of datasets was unexpected type {type(datasets)}, defaulting to empty dictionary.", logging.WARN)
        return ret_val

class FileListSchema(Schema):
    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, name:str, all_elements:Dict[str, Any]):
        self._games_file_lists : Dict[str, GameDatasetCollectionSchema]
        self._config           : FileListConfigSchema

        if not isinstance(all_elements, dict):
            all_elements = {}
    # 1. Parse config
        if "CONFIG" in all_elements.keys():
            self._config = FileListSchema._parseConfig(config=all_elements["CONFIG"])
        else:
            self._date_modified = "UNKNOWN"
    # 2. Parse games
        _used = {"CONFIG"}
        _leftovers = { key : val for key,val in all_elements.items() if key not in _used }
        self._games_file_lists = FileListSchema._parseGamesFileLists(games_dict=_leftovers)
        super().__init__(name=name, other_elements={})

    def __str__(self) -> str:
        return self.Name

    # *** Properties ***

    @property
    def Games(self) -> Dict[str, GameDatasetCollectionSchema]:
        return self._games_file_lists
    @property
    def Config(self) -> FileListConfigSchema:
        return self._config
    @property
    def AsMarkdown(self) -> str:
        ret_val : str = self.Name
        return ret_val

    # *** Private Functions ***

    # NOTE: Yes, most of these parse functions are redundant, but that's fine,
    # we just want to have one bit of code to parse each piece of the schema, even if most do the same thing.

    @staticmethod
    def _parseConfig(config) -> FileListConfigSchema:
        ret_val : FileListConfigSchema
        if isinstance(config, dict):
            ret_val = FileListConfigSchema(name="ConfigSchema", all_elements=config)
        else:
            ret_val = FileListConfigSchema.EmptySchema()
            Logger.Log(f"Config was unexpected type {type(config)}, defaulting to empty ConfigSchema.", logging.WARN)
        return ret_val

    @staticmethod
    def _parseGamesFileLists(games_dict:Dict[str, Any]) -> Dict[str, GameDatasetCollectionSchema]:
        ret_val : Dict[str, GameDatasetCollectionSchema]
        if isinstance(games_dict, dict):
            ret_val = {
                key : GameDatasetCollectionSchema(key, datasets if isinstance(datasets, dict) else {})
                for key, datasets in games_dict.items()
            }
        else:
            ret_val = {}
            Logger.Log(f"Collection of games was unexpected type {type(games_dict)}, defaulting to empty dictionary.", logging.WARN)
        return ret_val

