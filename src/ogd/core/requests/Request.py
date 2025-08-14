# import standard libraries
import abc
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
# import local files
from ogd.core.configs.CoreConfig import CoreConfig
from ogd.core.configs.generators.GeneratorCollectionConfig import GeneratorCollectionConfig
from ogd.common.configs.storage.DatasetRepositoryConfig import DatasetRepositoryConfig
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.filters.RangeFilter import RangeFilter
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.filters.collections.IDFilterCollection import IDFilterCollection
from ogd.common.filters.collections.SequencingFilterCollection import SequencingFilterCollection
from ogd.common.filters.collections.VersioningFilterCollection import VersioningFilterCollection, Version
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.FilterMode import FilterMode
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.storage.interfaces import Interface
from ogd.common.storage.interfaces.InterfaceFactory import InterfaceFactory
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.storage.outerfaces.OuterfaceFactory import OuterfaceFactory
from ogd.common.schemas.datasets.DatasetSchema import DatasetKey
from ogd.common.utils.Logger import Logger
from ogd.common.utils.typing import Date, Map

class ExporterRange:
    """
    Simple class to define a range of data for export.
    """
    def __init__(self, date_min:Date, date_max:Date, ids:Optional[List[str]], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[Version]]=None):
        self._date_min : Date = date_min
        self._date_max : Date = date_max
        self._ids      : Optional[List[str]]       = ids
        self._id_mode  : IDMode                    = id_mode
        self._versions : Optional[List[Version]] = versions

    @staticmethod
    def FromDateRange(source:Interface.Interface, dates:SequencingFilterCollection, versions:VersioningFilterCollection):
        if dates.Timestamps.Min and dates.Timestamps.Max:
            ids = source.AvailableIDs(mode=IDMode.SESSION, filters=DatasetFilterCollection(sequence_filters=dates, version_filters=versions))
            return ExporterRange(date_min=dates.Timestamps.Min, date_max=dates.Timestamps.Max, ids=ids, id_mode=IDMode.SESSION, versions=versions.LogVersions.AsList)
        else:
            raise ValueError(f"Tried to create exporter range from open-ended set of dates {dates.Timestamps.Min}-{dates.Timestamps.Max}, this is not supported!")

    @staticmethod
    def FromIDs(source:Interface.Interface, ids:IDFilterCollection, id_mode:IDMode=IDMode.SESSION, versions:VersioningFilterCollection=VersioningFilterCollection()):
        date_range = source.AvailableDates(filters=DatasetFilterCollection(id_filters=ids, version_filters=versions))
        if date_range['min'] is not None and date_range['max'] is not None:
            id_list = ids.Sessions.AsList if id_mode==IDMode.SESSION else ids.Players.AsList
            return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=id_list, id_mode=id_mode, versions=versions.LogVersions.AsList)
        else:
            raise ValueError(f"Tried to create exporter range from set of IDs, but this resulted in open-ended date range {date_range['min']}-{date_range['max']}, this is not supported!")

    @property
    def DateRange(self) -> Dict[str, Date]:
        return {'min':self._date_min, 'max':self._date_max}

    @property
    def IDs(self) -> Optional[List[str]]:
        return self._ids

    @property
    def IDMode(self):
        return self._id_mode

class Request(abc.ABC):
    """Request class

    Dumb struct to hold data related to requests for data export.
    This way, we've at least got a list of what is available in a request.
    Acts as a base class for more specific types of request.
    """

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, exporter_modes:Set[ExportMode], filters:DatasetFilterCollection,
                 global_cfg:CoreConfig, game_cfg:GeneratorCollectionConfig,
                 custom_source:Optional[GameStoreConfig]=None, custom_dest:Optional[GameStoreConfig]=None,
                 custom_data_directory:Optional[DatasetRepositoryConfig | Dict | Path | str]=None):
        """ Constructor for the request base class.
            Just stores whatever data is given.
            No checking done to ensure we have all necessary data, this can be checked wherever Requests are actually used.

        :param filters: _description_
        :type filters: DatasetFilterCollection
        :param exporter_modes: _description_
        :type exporter_modes: Set[ExportMode]
        :param source: _description_
        :type source: GameStoreConfig
        :param dest: _description_
        :type dest: GameStoreConfig
        :param feature_overrides: _description_, defaults to None
        :type feature_overrides: Optional[List[str]], optional
        """
        # TODO: kind of a hack to just get id from interface, figure out later how this should be handled.
        self._game_id    : str                       = game_cfg.GameName
        self._exports    : Set[ExportMode]           = exporter_modes
        self._filters    : DatasetFilterCollection   = filters
        self._generators : GeneratorCollectionConfig = game_cfg
        self._global_cfg : CoreConfig                = global_cfg
        self._repository : DatasetRepositoryConfig   = self._toRepository(repository=custom_data_directory)
        source = custom_source or self._global_cfg.GameSourceMap.get(self._game_id, GameStoreConfig.Default())
        dest   = custom_dest   or self._global_cfg.GameSourceMap.get(self._game_id, GameStoreConfig.Default())

        self._interface  : Interface.Interface     = InterfaceFactory.FromConfig(config=source, fail_fast=self._global_cfg.FailFast)
        self._range      : ExporterRange
        if filters.Sequences.Timestamps.Active:
            self._range = ExporterRange.FromDateRange(source=self._interface, dates=filters.Sequences, versions=filters.Versions)
        elif filters.IDFilters.Sessions.Active:
            self._range = ExporterRange.FromIDs(source=self._interface, ids=filters.IDFilters, id_mode=IDMode.SESSION, versions=filters.Versions)
        elif filters.IDFilters.Players.Active:
            self._range = ExporterRange.FromIDs(source=self._interface, ids=filters.IDFilters, id_mode=IDMode.USER, versions=filters.Versions)
        else:
            Logger.Log("Request filters did not define a time range, nor session set, nor player set! Defaulting to filter for yesterday's data!", logging.WARNING)
            yesterday = datetime.now() - timedelta(days=1)
            filters.Sequences.Timestamps = RangeFilter[date](mode=FilterMode.INCLUDE, minimum=yesterday.date(), maximum=datetime.now().date())
            self._range = ExporterRange.FromDateRange(source=self._interface, dates=filters.Sequences, versions=filters.Versions)
        dataset_key = DatasetKey.FromDateRange(game_id=self.GameID, start_date=self.Range.DateRange['min'], end_date=self.Range.DateRange['max'])
        self._outerfaces     : Set[Outerface]          = {OuterfaceFactory.FromConfig(config=dest, export_modes=exporter_modes, repository=repository, dataset_id=str(dataset_key))}

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
    def Interface(self) -> Interface.Interface:
        return self._interface

    @property
    def Range(self) -> ExporterRange:
        return self._range

    @property
    def Overrides(self) -> Optional[List[str]]:
        return self._feat_overrides

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
    def Outerfaces(self) -> Set[Outerface]:
        return self._outerfaces

    def RemoveExportMode(self, mode:ExportMode):
        self._exports.discard(mode)
        for outerface in self.Outerfaces:
            outerface.RemoveExportMode(mode=mode)

    ## Method to retrieve the list of IDs for all sessions covered by the request.
    #  Note, this will use the 
    def RetrieveIDs(self) -> Optional[List[str]]:
        return self.Range.IDs

    @staticmethod
    def _toRepository(data_directory:Optional[DatasetRepositoryConfig | Dict | Path | str], fallbacks:Map) -> DatasetRepositoryConfig:
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
