## import standard libraries
import abc
import logging
from typing import List, Optional
# import locals
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.utils.Logger import Logger

## @class ExtractorParams
class GeneratorParameters:
    """Dumb struct to hold the data that should be available to every Generator.
    This just makes it easier to add/manage any new params,
    so that we don't need to change the param list for hundreds of individual
    extractor subclasses every time something changes.
    """
    def __init__(self, name:str, description:str, mode:ExtractionMode, count_index:Optional[int]):
        self._name = name
        self._desc = description
        self._mode = mode
        self._count_index = count_index

## @class Extractor
#  Abstract base class for all data extractors (features and detectors)
class Generator(abc.ABC):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or feature since last calculation

    # *** ABSTRACTS ***

    ## Abstract function to get a list of event types the Feature wants.
    @classmethod
    @abc.abstractmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """ Abstract function to get a list of event types the Feature wants.
            The types of event accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: List[str]
        """
        raise TypeError(f"Can't call function on class {cls.__name__} with abstract method _eventFilter")

    @classmethod
    @abc.abstractmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """Base function for getting any features a second-order feature depends upon.
        By default, no dependencies.
        Any feature intented to be second-order should override this function.

        :return: _description_
        :rtype: List[str]
        """
        raise TypeError(f"Can't call function on class {cls.__name__} with abstract method _featureFilter")

    ## Abstract declaration of a function to perform update of a feature from a row.
    @abc.abstractmethod
    def _updateFromEvent(self, event:Event):
        """Abstract declaration of a function to perform update of a feature from a row.

        :param event: An event, used to update the feature's data.
        :type event: Event
        """
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters):
        self._params = params

    def __str__(self):
        return f"{self.Name} : {self.Description}"

    # *** PUBLIC STATICS ***

    @staticmethod
    def WarningMessage(message:str):
        """
        Simple wrapper for the Logger in utils, makes it easier for subclasses to print warning messages without extra imports.

        :param message: The warning message to print
        :type message: str
        """
        Logger.Log(message=message, level=logging.WARN, depth=3)

    ## Base function to get the minimum log version the feature can handle.
    @staticmethod
    def MinVersion() -> Optional[str]:
        """ Base function to get the minimum log version the feature can handle.
            A value of None will set no minimum, so all levels are accepted (unless a max is set).
            Typically default to None, unless there is a required element of the event data that was not added until a certain version.        
            The versions of data accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Optional[str]
        """
        return None

    ## Base function to get the maximum log version the feature can handle.
    @staticmethod
    def MaxVersion() -> Optional[str]:
        """ Base function to get the maximum log version the feature can handle.
            A value of None will set no maximum, so all levels are accepted (unless a min is set).
            Typically default to None, unless the feature is not compatible with new data and is only kept for legacy purposes.
            The versions of data accepted by a feature are a responsibility of the Feature's developer,
            so this is a required part of interface instead of a config item in the schema.

        :return: [description]
        :rtype: Optional[str]
        """
        return None

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Extractor

        Base function to give a list of which ExtractionModes an extractor will handle.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION, ExtractionMode.DETECTOR]

    # *** PUBLIC METHODS ***

    @classmethod
    def EventFilter(cls, mode:ExtractionMode) -> List[str]:
        return cls._eventFilter(mode=mode)

    @classmethod
    def FeatureFilter(cls, mode:ExtractionMode) -> List[str]:
        return cls._featureFilter(mode=mode)

    def UpdateFromEvent(self, event:Event):
        if self._validateEvent(event=event):
            self._updateFromEvent(event=event)

    # *** PROPERTIES ***

    @property
    def Name(self) -> str:
        return self._params._name

    @property
    def Description(self) -> str:
        return self._params._desc

    @property
    def ExtractionMode(self) -> ExtractionMode:
        return self._params._mode

    @property
    def CountIndex(self) -> Optional[int]:
        return self._params._count_index

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
            self._validateVersion(event.LogVersion)
        and self._validateEventType(event_type=event.EventName)
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
        _deps = self.EventFilter(mode=self.ExtractionMode)
        if event_type in _deps or 'all_events' in _deps:
            return True
        else:
            return False