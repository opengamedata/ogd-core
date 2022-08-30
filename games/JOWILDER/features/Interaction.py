# import libraries
import json
from os import environ
from typing import Any, List, Optional
from extractors.Extractor import ExtractorParameters
# import local files
from extractors.features.PerCountFeature import PerCountFeature
from schemas.FeatureData import FeatureData
from schemas.Event import Event
from datetime import datetime, timedelta
from games.JOWILDER import Jowilder_Enumerators as je

# NOTE: Assumptions are: 1. All click events occured in the order like xxxx111xx222x1x3. 2. Use "text_fqid" to identify interactions. 3. The first interaction "tunic.historicalsociety.closet.intro" makes no sense so we don't need to consider it. That is, there are 190 interactions in total, but we only count 189. And we should confirm that, this tunic.historicalsociety.closet.intro doesn't occur anywhere else.
# BUG: Sometimes, dialogues are passed as wildcard click events and there are no text_fqid for that. For example, in chapter2.finale, before answering the bosses's question, some dialogue texts are categorized to wildcard click.
# XXX: Each event will be loaded to feature processor three times since we have three levels of features, player, population, session


class ClickTrack:
    def __init__(self, start_time: datetime = None, game_start: bool = False, this_click:Event=None, last_click:Event=None) -> None:
        self._game_start : bool = game_start
        self._game_start_time : Optional[datetime] = start_time
        self._last_click : Optional[Event] = last_click
        self._this_click : Optional[Event] = this_click
        self._time_between : Optional[timedelta] = None
        # 1 means searching in an interaction; 0 means searching in an non-interaction click.
        self._search_state : int = 0

    # TODO: Add more property decorators fuction
    @property
    def LastClickTime(self):
        return self._last_click.Timestamp

    @property
    def LastInteractionIndex(self):
        _interaction = self._last_click.EventData.get(
            "text_fqid") or self._last_click.EventData.get("cur_cmd_fqid")
        return je.fqid_to_enum.get(_interaction)

    @property
    def GameStart(self):
        return self._game_start

    @property
    def GameStartTime(self):
        return self._game_start_time

    @staticmethod
    def EventEq(event1:Event, event2:Event) -> bool:
        if event1.SessionID == event2.SessionID and event1.EventSequenceIndex == event2.EventSequenceIndex:
            return True
        return False

    def Update(self, event: Event) -> timedelta:
        # event_sequence_index
        if ClickTrack.EventEq(self._this_click, event):
            return self._time_between
        self._last_click = self._this_click
        self._this_click = event
        self._time_between = self._this_click.Timestamp - self._last_click.Timestamp
        return self._time_between
    
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

    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)
        self._interaction : int = None
        self._interaction_time : timedelta = timedelta(0)
        self._first_encounter_time : timedelta = timedelta(0)
        self._num_encounters : int = 0
        self._to : timedelta = timedelta(0)

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    def _validateEventCountIndex(self, event: Event):
        if event.EventName == "CUSTOM.1":
            return True
        self._interaction = je.fqid_to_enum.get(event.EventData.get("text_fqid") or event.EventData.get("cur_cmd_fqid"))
        if self._interaction is None:
            return self.CountIndex == clicks_track.LastInteractionIndex
        else:
            return self._interaction == self.CountIndex

        

    def _getEventDependencies(self) -> List[str]:
        # NOTE: Count all the click events
        return ["CUSTOM." + str(i) for i in range(3,12)] + ["CUSTOM.1"]
        # CUSTOM.X, X in [3,12) = ['navigate_click','notebook_click', 'map_click', 'notification_click', 'object_click', 'observation_click', 'person_click', 'cutscene_click', 'wildcard_click']

    def _getFeatureDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return []

    def _extractFromEvent(self, event: Event) -> None:
        if not clicks_track.GameStart:
            if event.EventName == "CUSTOM.1":
                clicks_track.startGame(event)
                return
            else:
                raise(ValueError("A startgame event needed!"))
        elif event.EventName == "CUSTOM.1": 
            if clicks_track.EventEq(event, clicks_track._this_click):
                return
            else:
                raise(ValueError("Too many startgame events!"))

        if event.EventName == "CUSTOM.11" and event.EventData.get("cur_cmd_type") == 2:
            return
        if self._interaction is None:
            clicks_track.Update(event)
            clicks_track._search_state = 0
            return
        
        clicks_track.Update(event)
        self._interaction_time += event.Timestamp - clicks_track.LastClickTime
        if clicks_track.StartNewInteraction(self._interaction):
            clicks_track._search_state = 1
            if self._num_encounters == 0:
                # The interaction starts from last click but recorded from this click
                self._to = clicks_track.LastClickTime - clicks_track.GameStartTime
            self._num_encounters += 1
        if self._num_encounters <= 1:
            self._first_encounter_time = self._interaction_time
        
        return

    def _extractFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        return [self._interaction_time, self._first_encounter_time, self._num_encounters, self._to]

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["FirstEncounterTime", "NumEncounter", "TimeTo"]

    def BaseFeatureSuffix(self) -> str:
        return "Time"
