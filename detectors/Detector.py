## import standard libraries
import abc
from typing import Any, Callable, List, Union
# import locals
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave Detectors.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on Detectors from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Detector(Feature):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or Detector since last calculation

    # *** ABSTRACTS ***

    @abc.abstractmethod
    def _trigger_condition(self) -> bool:
        pass

    @abc.abstractmethod
    def _trigger_event(self) -> Event:
        pass

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _getFeatureDependencies(self) -> List[str]:
        """Base function for getting any features a second-order feature depends upon.
        By default, no dependencies.
        Any feature intented to be second-order should override this function.

        :return: _description_
        :rtype: List[str]
        """
        return []

    def _extractFromFeatureData(self, feature:FeatureData):
        """Abstract declaration of a function to perform update of a feature from a row.

        :param event: An event, used to update the feature's data.
        :type event: Event
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        """Abstract declaration of a function to get the calculated value of the feature, given data seen so far.

        :return: Returns the values of all columns for the Feature, based on data the feature has seen so far.
        :rtype: typing.Tuple
        """
        return []

    # *** PUBLIC BUILT-INS ***

    def __init__(self, name:str, description:str, count_index:int, trigger_callback:Callable[[Event], None]):
        self._name        = name
        self._desc        = description
        self._count_index = count_index
        self._callback    = trigger_callback

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
            if self._trigger_condition():
                _event = self._trigger_event()
                # TODO: add some logic to fill in empty values of Event with reasonable defaults, where applicable.
                self._callback(_event)

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