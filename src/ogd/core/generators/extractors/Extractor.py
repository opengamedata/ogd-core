## import standard libraries
import abc
from typing import Any, Dict, List, Optional
# import locals
from ogd.core.generators.Generator import Generator, GeneratorParameters
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData

class Extractor(Generator):
    """
    Base class for feature extractors.

    In addition to event/feature filters and an update-from-event rule,
    the Feature base class requires subclasses to implement an update-from-feature rule and a calculate rule.
    """

#TODO: use a dirty bit so we only run the GetValue function if we've received an event or feature since last calculation

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to perform update of a feature from a row.
    @abc.abstractmethod
    def _updateFromFeatureData(self, feature:FeatureData):
        """Abstract declaration of a function to perform update of a feature from a row.

        :param event: An event, used to update the feature's data.
        :type event: Event
        """
        pass

    ## Abstract declaration of a function to get the calculated value of the feature, given data seen so far.
    @abc.abstractmethod
    def _getFeatureValues(self) -> List[Any]:
        """Abstract declaration of a function to get the calculated value of the feature, given data seen so far.

        :return: Returns the values of all columns for the Feature, based on data the feature has seen so far.
        :rtype: typing.Tuple
        """
        pass

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._up_to_date = False
        # by default, latest values should just be None, with length equal to number of columns for the feature.
        self._latest_values : List[Any] = [None for i in range(len(self.GetFeatureNames())) ]

    # *** PUBLIC STATICS ***

    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        """List of ExtractionMode supported by the Feature.

        Overridden from Extractor's version of the function, only makes the Feature-related modes supported.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION]

    @staticmethod
    def FeatureDependencyModes() -> List[ExtractionMode]:
        """List of ExtractionModes .

        Overridden from Extractor's version of the function, only makes the Feature-related modes supported.
        :return: _description_
        :rtype: List[ExtractionMode]
        """
        return [ExtractionMode.POPULATION, ExtractionMode.PLAYER, ExtractionMode.SESSION]

    # *** PUBLIC METHODS ***

    def ToFeatureData(self, player_id:Optional[str]=None, sess_id:Optional[str]=None) -> FeatureData:
        return FeatureData(
            name=self.Name,
            feature_type=type(self).__name__,
            count_index=self.CountIndex,
            cols=self.GetFeatureNames(),
            vals=self.GetFeatureValues(),
            mode=self.ExtractionMode,
            player_id=player_id,
            sess_id=sess_id
        )

    def BaseFeatureSuffix(self) -> str:
        """Base function to add a suffix to the base feature name, which will not affect the naming of subfeatures.
        By default, returns ""; override to set a suffix.
        Example use-case: Suppose you want a feature that captures the number of times a player enters a given state,
        as well as the time spent in that state.
        The feature can be named "State", with BaseFeatureSuffix returning "EntryCount" and a subfeature named "Time."
        Then the columns will be named "StateEntryCount" and "StateTime."

        :return: _description_
        :rtype: str
        """
        return ""

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
        return [f"{self.Name}{self.BaseFeatureSuffix()}"] + [f"{self.Name}-{subfeature}" for subfeature in self.Subfeatures()]

    def UpdateFromEvent(self, event:Event):
        """Overridden version of function from Extractor base class;
        In this case, set the "up to date" value to False whenever we see a new event.

        :param event: _description_
        :type event: Event
        """
        if self._validateEvent(event=event):
            self._updateFromEvent(event=event)
            self._up_to_date = False

    def UpdateFromFeatureData(self, feature:FeatureData):
        # TODO: add validation for FeatureData, if applicable/possible.
        # TODO: figure out a way to invalidate/reset if more events are given to features on which the given feature depends.
        self._updateFromFeatureData(feature=feature)
        self._up_to_date = False

    def GetFeatureValues(self) -> List[Any]:
        # Only call calculation feature if new events were seen since last call.
        # Practically, this doesn't matter because we always process all data before using GetFeatureValues.
        # Someday, however, this may be useful when dealing with a caching system.
        if not self._up_to_date:
            self._latest_value = self._getFeatureValues()
            self._up_to_date = True
        return self._latest_value

    # *** PROPERTIES ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***