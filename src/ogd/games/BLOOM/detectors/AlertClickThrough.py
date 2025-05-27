from datetime import datetime,timedelta
from statistics import mean
from typing import Any, Callable, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from ogd.common.utils.Logger import Logger

class AlertClickThrough(Detector):
    """Detector to estimate when players click straight through the dialog following a local event click.

    There are a few specific design decisions/limitations to keep in mind.
    First, this is based on an estimated "reading rate" across the entirety of lines between "dialog_start" and "dialog_end" following a local alert click.
        The estimated rate is compared to a "maximum reading rate" parameter.
        There is no adjustment for reading difficulty, nor an attempt to account for distracted players leaving a dialog open for some time, but otherwise clicking through.
    Second, word counts are based on spaces, with nothing to account for punctuation.
        For example, "well-known" would be considered a single word.
    Third, there is a strict assumption that local alerts are followed by a dialog_start, and later a dialog_end, and that all dialog in between is given by "character_line" events, as opposed to cutscene-related events.
        Any review of real, logged data will reveal that this second set of assumptions is violated by the logging code with regularity, because of course it is.
    """
    DEFAULT_MAX_RATE = 200*2

    def __init__(self, params: GeneratorParameters, trigger_callback:Callable[[Event], None], max_reading_rate:int=DEFAULT_MAX_RATE):
        """Constructor for an instance of the AlertClickThrough detector, which estimates when players click straight through the dialog following a local event click.

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
        self._last_session        : Optional[str]
        self._current_alert_type  : Optional[str]
        self._current_dialog_node : Optional[str]
        self._in_dialog   : bool
        self._word_counts : List[int]
        self._read_times  : List[timedelta]
        self._last_time   : Optional[datetime]
        self._triggered   : Optional[bool]
        self._reset()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["click_local_alert", "dialogue_start", "dialogue_end", "click_next_character_line", "character_line_displayed"]

    def _updateFromEvent(self, event: Event) -> None:
        # if the session ID changed, assume we reset out of any active alert.
        if event.SessionID != self._last_session:
            self._reset()
        match event.EventName:
            case "click_local_alert":
                _alert_type = event.EventData.get("alert_type", "NOT FOUND")
                if self._current_alert_type is None:
                    if _alert_type.upper() not in {"NOT FOUND", "GLOBAL"}:
                        self._current_alert_type = _alert_type
                else:
                    Logger.Log(f"Got a local alert click when {_alert_type} alert was active!")
            case "dialogue_start":
                if self._current_alert_type is not None:
                    self._in_dialog = True
            case "character_line_displayed":
                if self._in_dialog:
                    _line = event.EventData.get("line_text")
                    self._word_counts.append(len(_line.split(" ")) if _line is not None else 0)
                    self._last_time = event.Timestamp
            case "click_next_character_line":
                if self._in_dialog:
                    _delta = timedelta(0)
                    if self._last_time is not None:
                        _delta = event.Timestamp - self._last_time
                    self._read_times.append(_delta)
                    # blank out last time after use
                    self._last_time = None
            case "dialogue_end":
                _rate = sum(self._word_counts) / sum(self._read_times, timedelta(0)).total_seconds() * 60
                # if rate was too high, they clicked through
                if _rate > self.MAX_RATE:
                    self._triggered = True
                # else, reset for the next time around
                else:
                    self._reset()
                # in either case, blank out alert type and state after use
                self._in_dialog = False
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
        ret_val : DetectorEvent = self.GenerateEvent(
            app_id="BLOOM", event_name="alert_click_through",
            event_data={
                "alert_type":str(self._current_alert_type),
                "node_id":str(self._current_dialog_node),
                "reading_rate":sum(self._word_counts) / sum(self._read_times, timedelta(0)).total_seconds() * 60
            }
        )
        self._reset()
        return ret_val

    def _reset(self):
        self._current_alert_type = None
        self._current_dialog_node = None
        self._in_dialog = False
        self._word_counts = []
        self._read_times = []
        self._last_time = None
        self._triggered = None
