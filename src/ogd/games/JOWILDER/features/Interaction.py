# import libraries
import json
from datetime import datetime, timedelta
from os import environ
from sqlite3 import Timestamp
from typing import Any, List, Optional
from ogd.core.generators.Generator import GeneratorParameters
# import local files
from ogd.core.generators.extractors.PerCountFeature import PerCountFeature
from ogd.games.JOWILDER import Jowilder_Enumerators as je
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

# NOTE: Assumptions are: 1. All click events occured in the order like xxxx111xx222x1x3. 2. Use "text_fqid" to identify interactions. 3. The first interaction "tunic.historicalsociety.closet.intro" makes no sense so we don't need to consider it. That is, there are 190 interactions in total, but we only count 189. And we should confirm that, this tunic.historicalsociety.closet.intro doesn't occur anywhere else.


class ClickTrack:
    def __init__(self, start_time:Optional[datetime] = None, game_start: bool = False, this_click:Optional[Event]=None, last_click:Optional[Event]=None) -> None:
        self._game_start : bool = game_start
        self._game_start_time : Optional[datetime] = start_time
        self._last_click : Optional[Event] = last_click
        self._this_click : Optional[Event] = this_click
        self._time_between : Optional[timedelta] = None
        # 1 means searching in an interaction; 0 means searching in an non-interaction click.
        self._search_state : int = 0

    # TODO: Add more property decorators fuction
    @property
    def LastClickTime(self) -> Optional[datetime]:
        if self._last_click is not None:
            return self._last_click.Timestamp
        else:
            return None

    @property
    def LastInteractionIndex(self) -> Optional[int]:
        if self._last_click is not None:
            _interaction = self._last_click.EventData.get("text_fqid") \
                        or self._last_click.EventData.get("cur_cmd_fqid") \
                        or "FQID NOT FOUND"
            return je.fqid_to_enum.get(_interaction)
        else:
            return None

    @property
    def GameStart(self) -> bool:
        return self._game_start

    @property
    def GameStartTime(self) -> Optional[datetime]:
        return self._game_start_time

    @staticmethod
    def EventEq(event1:Event, event2:Event) -> bool:
        if event1.SessionID == event2.SessionID and event1.EventSequenceIndex == event2.EventSequenceIndex:
            return True
        return False

    def Update(self, event:Event) -> timedelta:
        # event_sequence_index
        ret_val : timedelta = timedelta(0)
        if self._this_click is not None and ClickTrack.EventEq(self._this_click, event):
            ret_val = self._time_between or ret_val # if self._time_between was non-null, return it.
        else:
            self._last_click = self._this_click
            self._this_click = event
            if self._last_click is not None:
                self._time_between = self._this_click.Timestamp - self._last_click.Timestamp
                ret_val = self._time_between
        return ret_val
    
    def StartNewInteraction(self, this_interaction : Optional[int]):
        if this_interaction is not None and (self._search_state == 0 or this_interaction != self.LastInteractionIndex):
            return True
    
    def startGame(self, event: Event):
        self._game_start = True
        self._game_start_time = event.Timestamp
        self._this_click = event
        self._last_click = event


clicks_track = ClickTrack()

class Interaction(PerCountFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)
        self._interaction : Optional[int] = None
        self._interaction_time : timedelta = timedelta(0)
        self._first_encounter_time : timedelta = timedelta(0)
        self._num_encounters : int = 0
        self._to : timedelta = timedelta(0)

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
        return []

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
        
        clicks_track.Update(event)
        if clicks_track.LastClickTime is not None:
            self._interaction_time += event.Timestamp - clicks_track.LastClickTime
            if clicks_track.StartNewInteraction(self._interaction):
                clicks_track._search_state = 1
                if self._num_encounters == 0:
                    if clicks_track.GameStartTime is not None:
                        # The interaction starts from last click but recorded from this click
                        self._to = clicks_track.LastClickTime - clicks_track.GameStartTime
                    else:
                        raise ValueError(f"Interaction feature tried to get _to value, but clicks_track didn't have a game start time.")
                self._num_encounters += 1
            if self._num_encounters <= 1:
                self._first_encounter_time = self._interaction_time
        else:
            raise ValueError(f"Interaction feature tried to get interaction time, but clicks_track didn't have a previous click.")
        
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._interaction_time, self._first_encounter_time, self._num_encounters, self._to]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["FirstEncounterTime", "NumEncounter", "TimeTo"]

    def BaseFeatureSuffix(self) -> str:
        return "Time"
