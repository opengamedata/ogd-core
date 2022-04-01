## import standard libraries
import abc
from typing import Any, Dict, List, Union
# Local imports
from schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave Detectors.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on Detectors from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Detector(abc.ABC):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or Detector since last calculation

    # *** ABSTRACTS ***

    ## Abstract function to get a list of event types the Detector wants.
    @abc.abstractmethod
    def _getEventDependencies(self) -> List[str]:
        """ Abstract function to get a list of event types the Detector wants.
            The types of event accepted by a Detector are a responsibility of the Detector's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: List[str]
        """
        pass

    ## Abstract declaration of a function to perform update of a Detector from a row.
    @abc.abstractmethod
    def _extractFromEvent(self, event:Event):
        """Abstract declaration of a function to perform update of a Detector from a row.

        :param event: An event, used to update the Detector's data.
        :type event: Event
        """
        pass

    @abc.abstractmethod
    def _trigger(self) -> Union[Event, None]:
        pass

    # *** PUBLIC BUILT-INS ***

    def __init__(self, name:str, description:str, count_index:int):
        self._name = name
        self._desc = description
        self._count_index = count_index

    def __str__(self):
        return f"{self._name} : {self._desc}"

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Name(self):
        return self._name
    
    def GetEventDependencies(self) -> List[str]:
        return self._getEventDependencies()

    def ExtractFromEvent(self, event:Event):
        if self._validateEvent(event=event):
            self._extractFromEvent(event=event)
    
    def Trigger(self) -> Union[Event, None]:
        # TODO: add some logic to fill in empty values of Event with reasonable defaults, where applicable.
        return self._trigger()

    ## Base function to get the minimum game data version the Detector can handle.
    def MinVersion(self) -> Union[str,None]:
        """ Base function to get the minimum game data version the Detector can handle.
            A value of None will set no minimum, so all levels are accepted (unless a max is set).
            Typically default to None, unless there is a required element of the event data that was not added until a certain version.        
            The versions of data accepted by a Detector are a responsibility of the Detector's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Union[str,None]
        """
        return None

    ## Base function to get the maximum game data version the Detector can handle.
    def MaxVersion(self) -> Union[str,None]:
        """ Base function to get the maximum game data version the Detector can handle.
            A value of None will set no maximum, so all levels are accepted (unless a min is set).
            Typically default to None, unless the Detector is not compatible with new data and is only kept for legacy purposes.
            The versions of data accepted by a Detector are a responsibility of the Detector's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Union[str,None]
        """
        return None

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***

    def _validateEvent(self, event:Event) -> bool:
        """Private function to check if a given event has valid version and type for this Detector.

        :param event: The event to be checked.
        :type event: Event
        :return: True if the event has valid version and type, otherwise false.
        :rtype: bool
        """
        return (
            self._validateVersion(event.log_version)
        and self._validateEventType(event_type=event.event_name)
        )

    ## Private function to check whether the given data version from a row is acceptable by this Detector extractor.
    def _validateVersion(self, data_version:str) -> bool:
        """Private function to check whether a given version is valid for this Detector.

        :param data_version: The logging version for some event to be checked.
        :type data_version: str
        :return: True if the given version is valid for this Detector, otherwise false.
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
        """Private function to check whether a given event type is accepted by this Detector.

        :param event_type: The name of the event type to be checked.
        :type event_type: str
        :return: True if the given event type is in this Detector's list, otherwise false.
        :rtype: bool
        """
        if event_type in self.GetEventDependencies():
            return True
        else:
            return False