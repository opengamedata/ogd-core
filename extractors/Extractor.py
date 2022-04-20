## import standard libraries
import abc
from typing import Any, Dict, List, Union
# import locals
from features.FeatureData import FeatureData
from schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Extractor(abc.ABC):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or feature since last calculation

    # *** ABSTRACTS ***

    ## Abstract function to get a list of event types the Feature wants.
    @abc.abstractmethod
    def _getEventDependencies(self) -> List[str]:
        """ Abstract function to get a list of event types the Feature wants.
            The types of event accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: List[str]
        """
        pass

    @abc.abstractmethod
    def _getFeatureDependencies(self) -> List[str]:
        """Base function for getting any features a second-order feature depends upon.
        By default, no dependencies.
        Any feature intented to be second-order should override this function.

        :return: _description_
        :rtype: List[str]
        """
        pass

    ## Abstract declaration of a function to perform update of a feature from a row.
    @abc.abstractmethod
    def _extractFromEvent(self, event:Event):
        """Abstract declaration of a function to perform update of a feature from a row.

        :param event: An event, used to update the feature's data.
        :type event: Event
        """
        pass

    # *** PUBLIC BUILT-INS and FORMATTERS ***

    def __init__(self, name:str, description:str, count_index:int):
        self._name = name
        self._desc = description
        self._count_index = count_index

    def __str__(self):
        return f"{self._name} : {self._desc}"

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    @property
    def Name(self):
        return self._name

    def GetEventDependencies(self) -> List[str]:
        return self._getEventDependencies()

    def GetFeatureDependencies(self) -> List[str]:
        return self._getFeatureDependencies()

    def ExtractFromEvent(self, event:Event):
        if self._validateEvent(event=event):
            self._extractFromEvent(event=event)

    ## Base function to get the minimum game data version the feature can handle.
    def MinVersion(self) -> Union[str,None]:
        """ Base function to get the minimum game data version the feature can handle.
            A value of None will set no minimum, so all levels are accepted (unless a max is set).
            Typically default to None, unless there is a required element of the event data that was not added until a certain version.        
            The versions of data accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Union[str,None]
        """
        return None

    ## Base function to get the maximum game data version the feature can handle.
    def MaxVersion(self) -> Union[str,None]:
        """ Base function to get the maximum game data version the feature can handle.
            A value of None will set no maximum, so all levels are accepted (unless a min is set).
            Typically default to None, unless the feature is not compatible with new data and is only kept for legacy purposes.
            The versions of data accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Union[str,None]
        """
        return None

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEvent(self, event:Event) -> bool:
        """Private function to check if a given event has valid version and type for this Feature.

        :param event: The event to be checked.
        :type event: Event
        :return: True if the event has valid version and type, otherwise false.
        :rtype: bool
        """
        return (
            self._validateVersion(event.log_version)
        and self._validateEventType(event_type=event.event_name)
        )

    ## Private function to check whether the given data version from a row is acceptable by this feature extractor.
    def _validateVersion(self, data_version:str) -> bool:
        """Private function to check whether a given version is valid for this Feature.

        :param data_version: The logging version for some event to be checked.
        :type data_version: str
        :return: True if the given version is valid for this feature, otherwise false.
        :rtype: bool
        """
        if data_version != 'None':
            min = self.MinVersion()
            if min is not None:
                if Event.CompareVersions(data_version, min) < 0:
                    return False # too old, not valid.
            max = self.MaxVersion()
            if max is not None:
                if Event.CompareVersions(data_version, max) > 0:
                    return False # too new, not valid
            return True # passed both cases, valid.
        else:
            return False # data_version of None is invalid.

    def _validateEventType(self, event_type:str) -> bool:
        """Private function to check whether a given event type is accepted by this Feature.

        :param event_type: The name of the event type to be checked.
        :type event_type: str
        :return: True if the given event type is in this feature's list, otherwise false.
        :rtype: bool
        """
        _deps = self.GetEventDependencies()
        if event_type in _deps or 'all_events' in _deps:
            return True
        else:
            return False