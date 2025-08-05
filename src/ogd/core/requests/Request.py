# import standard libraries
import abc
from datetime import datetime, date
from typing import Dict, List, Optional, Set
# import local files
from ogd.common.models.enums.IDMode import IDMode
from ogd.common.models.enums.ExportMode import ExportMode
from ogd.common.filters.collections.DatasetFilterCollection import DatasetFilterCollection
from ogd.common.filters.collections.IDFilterCollection import IDFilterCollection
from ogd.common.filters.collections.SequencingFilterCollection import SequencingFilterCollection
from ogd.common.filters.collections.VersioningFilterCollection import VersioningFilterCollection, Version
from ogd.common.storage.interfaces import Interface
from ogd.common.storage.outerfaces.Outerface import Outerface
from ogd.common.configs.GameStoreConfig import GameStoreConfig
from ogd.common.utils.Logger import Logger
from ogd.common.models.SemanticVersion import SemanticVersion

class ExporterRange:
    """
    Simple class to define a range of data for export.
    """
    def __init__(self, date_min:Optional[datetime | date], date_max:Optional[datetime | date], ids:Optional[List[str]], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[Version]]=None):
        self._date_min : Optional[datetime | date] = date_min
        self._date_max : Optional[datetime | date] = date_max
        self._ids      : Optional[List[str]]       = ids
        self._id_mode  : IDMode                    = id_mode
        self._versions : Optional[List[Version]] = versions

    @staticmethod
    def FromDateRange(source:Interface.Interface, dates:SequencingFilterCollection, versions:VersioningFilterCollection):
        ids = source.AvailableIDs(mode=IDMode.SESSION, filters=DatasetFilterCollection(sequence_filters=dates, version_filters=versions))
        return ExporterRange(date_min=dates.Timestamps.Min, date_max=dates.Timestamps.Max, ids=ids, id_mode=IDMode.SESSION, versions=versions.LogVersions.AsList)

    @staticmethod
    def FromIDs(source:Interface.Interface, ids:IDFilterCollection, id_mode:IDMode=IDMode.SESSION, versions:VersioningFilterCollection=VersioningFilterCollection()):
        date_range = source.AvailableDates(filters=DatasetFilterCollection(id_filters=ids, version_filters=versions))
        id_list = ids.Sessions.AsList if id_mode==IDMode.SESSION else ids.Players.AsList
        return ExporterRange(date_min=date_range['min'], date_max=date_range['max'], ids=id_list, id_mode=id_mode, versions=versions.LogVersions.AsList)

    @property
    def DateRange(self) -> Dict[str,Optional[datetime | date]]:
        return {'min':self._date_min, 'max':self._date_max}

    @property
    def IDs(self) -> Optional[List[str]]:
        return self._ids

    @property
    def IDMode(self):
        return self._id_mode

## @class Request
#  Dumb struct to hold data related to requests for data export.
#  This way, we've at least got a list of what is available in a request.
#  Acts as a base class for more specific types of request.
class Request(abc.ABC):
    ## Constructor for the request base class.
    #  Just stores whatever data is given. No checking done to ensure we have all
    #  necessary data, this can be checked wherever Requests are actually used.
    #  @param game_id An identifier for the game from which we want to extract data.
    #                 Should correspond to the app_id in the database.
    #  @param start_date   The starting date for our range of data to process.
    #  @param end_date     The ending date for our range of data to process.
    def __init__(self, filters:DatasetFilterCollection, exporter_modes:Set[ExportMode],
                interface:Interface.Interface,    outerfaces:Set[Outerface],
                feature_overrides:Optional[List[str]]=None):
        # TODO: kind of a hack to just get id from interface, figure out later how this should be handled.
        self._game_id        : str                     = str(interface._game_id)
        self._interface      : Interface.Interface     = interface
        self._filters        : DatasetFilterCollection = filters
        self._exports        : Set[ExportMode]         = exporter_modes
        self._outerfaces     : Set[Outerface]          = outerfaces
        self._feat_overrides : Optional[List[str]]     = feature_overrides

    ## String representation of a request. Just gives game id, and date range.
    def __str__(self):
        _fmt = "%Y-%m-%d"
        _min = "Unkown"
        _max = "Unkown"
        try:
            _range = self.Range.DateRange
            _min = _range['min'].strftime(_fmt) if _range['min'] is not None else "None"
            _max = _range['max'].strftime(_fmt) if _range['max'] is not None else "None"
        except Exception as err:
            Logger.Log(f"Got an error when trying to stringify a Request: {type(err)} {str(err)}")
        finally:
            return f"{self._game_id}: {_min}<->{_max} ({[str(export) for export in self._exports]})"

    @property
    def GameID(self):
        return self._game_id

    @property
    def Interface(self) -> Interface.Interface:
        return self._interface

    @property
    def Range(self) -> ExporterRange:
        return self._filters

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