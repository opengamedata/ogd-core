## import standard libraries
import abc
from typing import Any, Dict, List, Union
# import locals
from extractors.Extractor import Extractor
from features.FeatureData import FeatureData
from schemas.Event import Event

## @class Model
#  Abstract base class for session-level Wave features.
#  Models only have one public function, called Eval.
#  The Eval function takes a list of row data, computes some statistic, and returns a list of results.
#  If the model works on features from session data, it should calculate one result for each row (each row being a session).
#  If the model works on a raw list of recent events, it should calculate a single result (each row being an event).
class Feature(Extractor):
#TODO: use a dirty bit so we only run the GetValue function if we've received an event or feature since last calculation

    # *** ABSTRACTS ***

    ## Abstract declaration of a function to perform update of a feature from a row.
    @abc.abstractmethod
    def _extractFromFeatureData(self, feature:FeatureData):
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

    # *** PUBLIC BUILT-INS and FORMATTERS ***

    def ToFeatureData(self, player_id:Union[str, None]=None, sess_id:Union[str, None]=None) -> FeatureData:
        return FeatureData(
            name=self.Name,
            count_index=self._count_index,
            cols=self.GetFeatureNames(),
            vals=self.GetFeatureValues(),
            player_id=player_id,
            sess_id=sess_id
        )

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

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
        return [self.Name] + [f"{self.Name}-{subfeature}" for subfeature in self.Subfeatures()]

    def ExtractFromEvent(self, event:Event):
        if self._validateEvent(event=event):
            self._extractFromEvent(event=event)

    def ExtractFromFeatureData(self, feature:FeatureData):
        # TODO: add validation for FeatureData, if applicable/possible.
        self._extractFromFeatureData(feature=feature)

    def GetFeatureValues(self) -> List[Any]:
        return self._getFeatureValues()

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
