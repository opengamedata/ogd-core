## import standard libraries
import abc
import typing
from typing import Any, Dict, List, Union
# Local imports
from ..schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Feature(abc.ABC):
    def __init__(self, name:str, description:str, count_index:int):
        self._name = name
        self._desc = description
        self._count_index = count_index

    def __str__(self):
        return f"{self._name} : {self._desc}"

    ## Abstract function to get a list of event types the Feature wants.
    @abc.abstractmethod
    def GetEventTypes(self) -> List[str]:
        """ Abstract function to get a list of event types the Feature wants.
            The types of event accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: List[str]
        """
        pass

    ## Abstract function to get the minimum game data version the feature can handle.
    @abc.abstractmethod
    def MinVersion(self) -> Union[str,None]:
        """ Abstract function to get the minimum game data version the feature can handle.
            A value of None will set no minimum, so all levels are accepted (unless a max is set).
            Typically default to None, unless there is a required element of the event data that was not added until a certain version.        
            The versions of data accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Union[str,None]
        """
        pass

    ## Abstract function to get the maximum game data version the feature can handle.
    @abc.abstractmethod
    def MaxVersion(self) -> Union[str,None]:
        """ Abstract function to get the maximum game data version the feature can handle.
            A value of None will set no maximum, so all levels are accepted (unless a min is set).
            Typically default to None, unless the feature is not compatible with new data and is only kept for legacy purposes.
            The versions of data accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Union[str,None]
        """
        pass
    
    @abc.abstractmethod
    def CalculateFinalValues(self) -> typing.Tuple:
        pass

    def ExtractFromEvent(self, event:Event):
        event_type = event.event_name.split('.')[0]
        if self._validateVersion(event.app_version) and self._validateEventType(event_type if event_type != "CUSTOM" else event.event_data["event_custom"]):
            self._extractFromEvent(event)

    ## Abstract declaration of a function to perform update of a feature from a row.
    #
    #  @param row : A row, which will be used to update the feature's data.
    @abc.abstractmethod
    def _extractFromEvent(self, event:Event):
        pass

    ## Private function to check whether the given data version from a row is acceptable by this feature extractor.
    def _validateVersion(self, data_version:str) -> bool:
        min = self.MinVersion()
        if min is not None:
            if Event.CompareVersions(data_version, min) < 0:
                return False # too old, not valid.
        max = self.MaxVersion()
        if max is not None:
            if Event.CompareVersions(data_version, max) > 0:
                return False # too new, not valid
        return True # passed both cases, valid.

    def _validateEventType(self, event_type:str) -> bool:
        if event_type in self.GetEventTypes():
            return True
        else:
            return False