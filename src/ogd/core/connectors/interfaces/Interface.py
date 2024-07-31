"""DataInterface Module
"""
## import standard libraries
import abc
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

# import local files
from ogd.core.connectors.StorageConnector import StorageConnector
from ogd.core.models.Event import Event
from ogd.core.models.enums.IDMode import IDMode
from ogd.core.schemas.tables.TableSchema import TableSchema
from ogd.core.schemas.configs.GameSourceSchema import GameSourceSchema
from ogd.core.utils.Logger import Logger

class Interface(StorageConnector):

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _availableIDs(self, mode:IDMode=IDMode.SESSION) -> List[str]:
        """Private implementation of the logic to retrieve all IDs of given mode from the connected storage.

        :param mode: The type of ID to be listed.
        :type mode: IDMode
        :return: A list of IDs with given mode available through the connected storage.
        :rtype: List[str]
        """
        pass

    @abc.abstractmethod
    def _availableDates(self) -> Dict[str,datetime]:
        """Private implementation of the logic to retrieve the full range of dates/times from the connected storage.

        :return: A dict mapping 'min' and 'max' to the minimum and maximum datetimes
        :rtype: Dict[str,datetime]
        """
        pass

    @abc.abstractmethod
    def _IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]] = None) -> List[str]:
        pass

    @abc.abstractmethod
    def _datesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]] = None) -> Dict[str,datetime]:
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, game_id:str, config:GameSourceSchema, fail_fast:bool):
        super().__init__(config=config)
        self._fail_fast = fail_fast
        self._game_id : str  = game_id
        self._table_schema : TableSchema = TableSchema(schema_name=self._config.TableSchema)

    def __del__(self):
        self.Close()

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def AvailableIDs(self, mode:IDMode=IDMode.SESSION) -> Optional[List[str]]:
        """Function to retrieve all IDs of given mode from the connected storage.

        :param mode: The type of ID to be listed.
        :type mode: IDMode
        :return: A list of IDs with given mode available through the connected storage.
        :rtype: List[str]
        """
        ret_val = None
        if self.IsOpen:
            ret_val = self._availableIDs(mode=mode)
        else:
            Logger.Log("Can't retrieve list of all session IDs, the source interface is not open!", logging.WARNING, depth=3)
        return ret_val

    def AvailableDates(self) -> Union[Dict[str,datetime], Dict[str,None]]:
        """Function to retrieve the full range of dates/times covered by data in the connected storage.

        :return: A dictionary mapping 'min' and 'max' to the min and max datetimes, or to None (if unavailable)
        :rtype: Union[Dict[str,datetime], Dict[str,None]]
        """
        ret_val = {'min':None, 'max':None}
        if self.IsOpen:
            ret_val = self._availableDates()
        else:
            Logger.Log(f"Could not get full date range, the source interface is not open!", logging.WARNING, depth=3)
        return ret_val

    def IDsFromDates(self, min:datetime, max:datetime, versions:Optional[List[int]]=None) -> Optional[List[str]]:
        ret_val = None
        if not self.IsOpen:
            str_min, str_max = min.strftime("%Y%m%d"), max.strftime("%Y%m%d")
            Logger.Log(f"Could not retrieve IDs for {str_min}-{str_max}, the source interface is not open!", logging.WARNING, depth=3)
        else:
            ret_val = self._IDsFromDates(min=min, max=max, versions=versions)
        return ret_val

    def DatesFromIDs(self, id_list:List[str], id_mode:IDMode=IDMode.SESSION, versions:Optional[List[int]]=None) -> Union[Dict[str,datetime], Dict[str,None]]:
        ret_val = {'min':None, 'max':None}
        if not self.IsOpen:
            Logger.Log(f"Could not retrieve date range {len(id_list)} session IDs, the source interface is not open!", logging.WARNING, depth=3)
        else:
            Logger.Log(f"Retrieving date range from IDs with {id_mode.name} ID mode.", logging.DEBUG, depth=3)
            ret_val = self._datesFromIDs(id_list=id_list, id_mode=id_mode, versions=versions)
        return ret_val

    # *** PROPERTIES ***

    @property
    def _TableSchema(self) -> TableSchema:
        return self._table_schema

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
