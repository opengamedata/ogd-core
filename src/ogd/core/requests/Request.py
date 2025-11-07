# import standard libraries
import abc
from pathlib import Path
from typing import Dict, Optional, Set
# import local files
from ogd.core.configs.CoreConfig import CoreConfig
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.core.configs.GameStoreConfig import GameStoreConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.schemas.datasets.DatasetSchema import DatasetKey

class Request(abc.ABC):
    """Request class

    Dumb struct to hold data related to requests for data export.
    This way, we've at least got a list of what is available in a request.
    Acts as a base class for more specific types of request.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, exporter_modes:Set[ExportMode],
                 filters:DatasetFilterCollection,
                 global_cfg:CoreConfig,
                 game_cfg:GeneratorCollectionConfig,
                 custom_dataset_key:Optional[DatasetKey] = None,
                 custom_game_stores:Optional[GameStoreConfig] = None,
                 custom_data_directory:Optional[DatasetRepositoryConfig | Dict | Path | str] = None): # pylint: disable=unsupported-binary-operation
        """ Constructor for the request base class.
            Just stores whatever data is given.
            No checking done to ensure we have all necessary data, this can be checked wherever Requests are actually used.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        :param exporter_modes: _description_
        :type exporter_modes: Set[ExportMode]
        :param source: _description_
        :type source: DataTableConfig
        :param dest: _description_
        :type dest: DataTableConfig
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Optional[List[str]], optional
        """
        # TODO: kind of a hack to just get id from interface, figure out later how this should be handled.
        self._game_id      : str                       = game_cfg.GameName
        self._exports      : Set[ExportMode]           = exporter_modes
        self._filters      : DatasetFilterCollection   = filters
        self._generators   : GeneratorCollectionConfig = game_cfg
        self._global_cfg   : CoreConfig                = global_cfg
        self._game_stores  : GameStoreConfig           = custom_game_stores or self._global_cfg.GameSourceMap.get(self._game_id, GameStoreConfig.Default())
        self._dataset_key  : DatasetKey                = custom_dataset_key or DatasetKey(game_id=self.GameID, from_date=self._filters.Sequences.Timestamps.Min, to_date=self._filters.Sequences.Timestamps.Max)
        self._repository   : DatasetRepositoryConfig   = self._toRepository(data_directory=custom_data_directory)

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        return "Request Object"
        # _min = "Unkown"
        # _max = "Unkown"
        # try:
        #     _fmt = "%Y-%m-%d"
        #     _min = self.Range.DateRange['min'].strftime(_fmt) if self.Range.DateRange['min'] is not None else "None"
        #     _max = self.Range.DateRange['max'].strftime(_fmt) if self.Range.DateRange['max'] is not None else "None"
        # except Exception as err:
        #     Logger.Log(f"Got an error when trying to stringify a Request: {type(err)} {str(err)}")
        # finally:
        #     return f"{self._game_id}: {_min}<->{_max} ({[str(export) for export in self._exports]})"

    @property
    def GameID(self):
        return self._game_id

    @property
    def Generators(self) -> GeneratorCollectionConfig:
        return self._generators

    @property
    def DatasetID(self) -> DatasetKey:
        return self._dataset_key

    @property
    def Config(self) -> CoreConfig:
        return self._global_cfg

    @property
    def GameStores(self) -> GameStoreConfig:
        return self._game_stores

    @property
    def ExportModes(self) -> Set[ExportMode]:
        return self._exports
    @property
    def ExportRawEvents(self) -> bool:
        return ExportMode.EVENTS in self._exports
    @property
    def ExportProcessedEvents(self) -> bool:
        return ExportMode.DETECTORS in self._exports
    @property
    def ExportSessions(self) -> bool:
        return ExportMode.SESSION in self._exports
    @property
    def ExportPlayers(self) -> bool:
        return ExportMode.PLAYER in self._exports
    @property
    def ExportPopulation(self) -> bool:
        return ExportMode.POPULATION in self._exports

    @property
    def Filters(self) -> DatasetFilterCollection:
        return self._filters

    @property
    def Repository(self) -> DatasetRepositoryConfig:
        return self._repository

    def RemoveExportMode(self, mode:ExportMode):
        self._exports.discard(mode)

    @staticmethod
    def _toRepository(data_directory:Optional[DatasetRepositoryConfig | Dict | Path | str]) -> DatasetRepositoryConfig: # pylint: disable=unsupported-binary-operation
        ret_val: DatasetRepositoryConfig

        if isinstance(data_directory, DatasetRepositoryConfig):
            ret_val = data_directory
        elif isinstance(data_directory, dict):
            ret_val = DatasetRepositoryConfig.FromDict(name="CustomRequestRepository", unparsed_elements=data_directory)
        elif isinstance(data_directory, Path) or isinstance(data_directory, str):
            ret_val = DatasetRepositoryConfig(name="CustomRequestRepository", indexing=data_directory, datasets=None)
        else:
            ret_val = DatasetRepositoryConfig.Default()

        return ret_val
