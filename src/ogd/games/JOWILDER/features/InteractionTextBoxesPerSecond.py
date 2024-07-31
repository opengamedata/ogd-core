# import libraries
import json
from datetime import datetime, timedelta
from os import environ
from typing import Any, List, Optional
import numpy as np
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.JOWILDER import Jowilder_Enumerators as je
from ogd.games.JOWILDER.features.Interaction import clicks_track
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

# NOTE: Assumptions are: 1. All click events occured in the order like xxxx111xx222x1x3. 2. Use "text_fqid" to identify interactions. 3. The first interaction "tunic.historicalsociety.closet.intro" makes no sense so we don't need to consider it. That is, there are 190 interactions in total, but we only count 189. And we should confirm that, this tunic.historicalsociety.closet.intro doesn't occur anywhere else.

class InteractionTextBoxesPerSecond(PerCountFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._interaction : Optional[int] = None
        self._interaction_time : List[float] = []
        self._boxes_persecond : Optional[float] = None
        self._bps_variance : Optional[float] = None
        self._first_encounter : Optional[float] = None

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event: Event):
        if event.EventName == "CUSTOM.1":
            return True
        _fqid = event.EventData.get("text_fqid") or event.EventData.get("cur_cmd_fqid") or "FQID NOT FOUND"
        self._interaction = je.fqid_to_enum.get(_fqid)
        if self._interaction is None:
            return self.CountIndex == clicks_track.LastInteractionIndex
        else:
            return self._interaction == self.CountIndex

        

    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        # NOTE: Count all the click events
        return [f"CUSTOM.{i}" for i in range(3,12)] + ["CUSTOM.1"]
        # CUSTOM.X, X in [3,12) = ['navigate_click','notebook_click', 'map_click', 'notification_click', 'object_click', 'observation_click', 'person_click', 'cutscene_click', 'wildcard_click']

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["InteractionName"]

    def _updateFromEvent(self, event: Event) -> None:
        if not clicks_track.GameStart:
            if event.EventName == "CUSTOM.1":
                clicks_track.startGame(event)
                return
            else:
                raise(ValueError("A startgame event needed!"))
        elif event.EventName == "CUSTOM.1": 
            if clicks_track._this_click is not None and clicks_track.EventEq(event, clicks_track._this_click):
                return
            # else:
            #     raise(ValueError("Too many startgame events!"))

        if event.EventName == "CUSTOM.11" and event.EventData.get("cur_cmd_type") == 2:
            return
        if self._interaction is None:
            clicks_track.Update(event)
            clicks_track._search_state = 0
            return
        
        _time_between = clicks_track.Update(event).total_seconds()
        if clicks_track.StartNewInteraction(self._interaction):
            clicks_track._search_state = 1
            self._interaction_time.append(_time_between)
        else:
            self._interaction_time[-1] += _time_between
        
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        if len(self._interaction_time) == 0:
            return
        if feature.CountIndex != self.CountIndex:
            return
        _boxes = feature.FeatureValues[1]
        
        self._boxes_persecond = _boxes/np.mean(self._interaction_time)
        self._first_encounter = _boxes/self._interaction_time[0]
        self._bps_variance = np.var(_boxes/np.array(self._interaction_time))
        return

    def _getFeatureValues(self) -> List[Any]:
        
        return [self._boxes_persecond, self._first_encounter, self._bps_variance]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["FirstEncounter", "Variance"]

