## import standard libraries
import abc
from typing import Any, Dict, List, Union
# Local imports
from schemas.Event import Event
from features.Feature import Feature

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class SecondOrderFeature(Feature):

    # *** ABSTRACTS ***

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

    ## Abstract function to get a list of first-order Features the SecondOrderFeature wants.
    @abc.abstractmethod
    def GetFOFeatureTypes(self) -> List[str]:
        """ Abstract function to get a list of event types the Feature wants.
            The types of event accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: List[str]
        """
        # TODO: Figure out how to generate names properly for per-count features
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def GetFeatureValues(self) -> List[Any]:
        """Abstract declaration of a function to get the calculated value of the feature, given data seen so far.

        :return: Returns the values of all columns for the Feature, based on data the feature has seen so far.
        :rtype: typing.Tuple
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

    ## Abstract declaration of a function to perform update of a SecondOrderFeature from a first-order Feature.
    @abc.abstractmethod
    def _extractFromFOFeature(self, event:Event):
        """Abstract declaration of a function to perform update of a feature from a row.

        :param event: An event, used to update the feature's data.
        :type event: Event
        """
        pass

    # *** PUBLIC BUILT-INS ***

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    def Name(self):
        return self._name

    def Subfeatures(self) -> List[str]:
        """Base function to get a list of names of the sub-feature(s) a given Feature class outputs.
        By default, a Feature class has no subfeatures.
        However, if a Feature class is written to output multiple values, it will need to override this function to return an appropriate list.
        Note, Subfeatures **must** match the ordering from the override of GetFeatureNames, if returning a list of length > 0.

        :return: A list of names of subfeatures for the Feature sub-class.
        :rtype: Tuple[str]
        """
        return []

    def GetFeatureNames(self) -> List[str]:
        """Base function to get a list of names of the feature(s) a given Feature class outputs.
        By default, a Feature class just generates one value, and uses its own name (defined in the schema.json file).
        If Subfeatures was overridden, and returns a non-empty list, there will be additional feature names in the list this function returns.
        Each subfeature will have the base feature's name as a prefix.

        :return: [description]
        :rtype: List[str]
        """
        return [self.Name()] + [f"{self.Name()}_{subfeature}" for subfeature in self.Subfeatures()]

    def ExtractFromEvent(self, event:Event):
        if self._validateEvent(event):
            self._extractFromEvent(event)

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
            self._validateVersion(event.app_version)
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
        """Private function to check whether a given event type is accepted by this Feature.

        :param event_type: The name of the event type to be checked.
        :type event_type: str
        :return: True if the given event type is in this feature's list, otherwise false.
        :rtype: bool
        """
        if event_type in self.GetEventTypes():
            return True
        else:
            return False