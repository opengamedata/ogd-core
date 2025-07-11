import logging
from datetime import datetime,timedelta
from typing import Callable, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.utils.Logger import Logger

class CutsceneClickThrough(Detector):
    """Detector to estimate when players click straight through the dialog following a local event click.

    There are a few specific design decisions/limitations to keep in mind.
    First, this is based on an estimated "reading rate" across the entirety of lines between "cutscene_start" and "cutscene_end".
        The estimated rate is compared to a "maximum reading rate" parameter.
        There is no adjustment for reading difficulty, nor an attempt to account for distracted players leaving a dialog open for some time, but otherwise clicking through.
    Second, word counts are based on spaces, with nothing to account for punctuation.
        For example, "well-known" would be considered a single word.
    """
    # We use a max rate of twice the average reading rate for fiction suggested by Brysbaert in "How many words do we read per minute? A review and meta-analysis of reading rate"
    # This is ultimately arbitrary, but not unreasonable as a cutoff for "reading too fast"
    DEFAULT_MAX_RATE = 260*2

    def __init__(self, params: GeneratorParameters, trigger_callback:Callable[[Event], None], max_reading_rate:int=DEFAULT_MAX_RATE):
        """Constructor for an instance of the CutsceneClickThrough detector, which estimates when players click straight through the dialog following a local event click.

        :param params: The general initialization parameters used by the Generator base class.
        :type params: GeneratorParameters
        :param trigger_callback: A callback function for use when the detector is triggered, used by the Detector base class.
        :type trigger_callback: Callable[[Event], None]
        :param max_reading_rate: The rate, in words per minute, at which the fastest "real" readers are assumed to read.
            Players who "read" at more than the max reading rate are treated as click-throughs.
            defaults to DEFAULT_READING_RATE of 400 (twice the average estimated reading rate of 200 WPM from https://www.prsa.org/article/how-to-determine-average-reading-time)
        :type max_reading_rate: int, optional
        """
        super().__init__(params=params, trigger_callback=trigger_callback)
        self.MAX_RATE = max_reading_rate
        self._last_session        : Optional[str] = None
        self._current_cutscene : Optional[str]
        self._in_cutscene : bool
        self._word_counts : List[int]
        self._read_times  : List[timedelta]
        self._last_time   : Optional[datetime]
        self._triggered   : Optional[bool]
        self._reset()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["cutscene_start", "cutscene_end",
                "click_next_character_line", "character_line_displayed",
                "click_cutscene_next", "cutscene_page_displayed"
                ]

    def _updateFromEvent(self, event: Event) -> None:
        # if the session ID changed, assume we reset out of any active cutscene.
        if event.SessionID != self._last_session and self._last_session is not None:
            self._reset()
        match event.EventName:
            case "cutscene_start":
                self._in_cutscene = True
                self._current_cutscene = event.EventData.get("cutscene_id", "NOT FOUND")
            case "cutscene_page_displayed" | "character_line_displayed":
                if self._in_cutscene:
                    _line : Optional[str]
                    if event.EventName == "cutscene_page_displayed":
                        _line = event.EventData.get("page_text")
                    else:
                        _msg = f"In CutsceneClickThrough, found cutscene with ID {event.EventData.get('cutscene_id')} that had character lines displayed!"
                        Logger.Log(_msg, logging.DEBUG)
                        _line = event.EventData.get("line_text")
                    self._word_counts.append(len(_line.split(" ")) if _line is not None else 0)
                    self._last_time = event.Timestamp
            case "click_next_character_line" | "click_cutscene_next":
                if self._in_cutscene:
                    if event.EventName == "click_next_character_line":
                        _msg = f"In CutsceneClickThrough, found cutscene with ID {event.EventData.get('cutscene_id')} that had character lines clicked!"
                        Logger.Log(_msg, logging.DEBUG)
                    _delta = timedelta(0)
                    if self._last_time is not None:
                        _delta = event.Timestamp - self._last_time
                    self._read_times.append(_delta)
                    # blank out last time after use
                    self._last_time = None
            case "cutscene_end":
                _rate = 0
                if len(self._word_counts) != 0 and len(self._read_times) != 0:
                    if len(self._word_counts) == len(self._read_times):
                        _rate = sum(self._word_counts) / sum(self._read_times, timedelta(0)).total_seconds() * 60
                    else:
                        _msg = f"The number of word counts and read times for {self._last_session} do not match! For cutscene with node ID of {self._current_cutscene}, # word counts = {len(self._word_counts)}, # read times = {len(self._read_times)}"
                        Logger.Log(_msg, logging.WARNING)
                # if rate was too high, they clicked through
                if _rate > self.MAX_RATE:
                    self._triggered = True
                # else, reset for the next time around, if this end was the end of what we started...
                elif self._current_cutscene == event.EventData.get("node_id"):
                    self._reset()
                # in either case, blank out state after use
                self._in_cutscene = False
        self._last_session = event.SessionID

    def _trigger_condition(self) -> bool:
        if self._triggered:
            return True
        else:
            return False

    def _trigger_event(self) -> DetectorEvent:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        # For now, include the triggering event's EventData, for better debugging.
        ret_val : DetectorEvent
        
        _total_words = sum(self._word_counts)
        _total_time = sum(self._read_times, timedelta(0))
        
        ret_val = self.GenerateEvent(
            app_id="BLOOM", event_name="cutscene_click_through",
            event_data={
                "cutscene_id":str(self._current_cutscene),
                "word_count": _total_words,
                "total_reading_time": _total_time,
                "reading_rate": _total_words / _total_time.total_seconds() * 60
            }
        )
        self._reset()
        return ret_val

    def _reset(self):
        self._current_cutscene = None
        self._in_cutscene = False
        self._word_counts = []
        self._read_times = []
        self._last_time = None
        self._triggered = None
