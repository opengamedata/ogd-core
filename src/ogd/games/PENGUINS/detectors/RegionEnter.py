# import standard libraries
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
# import local files
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.detectors.Detector import Detector
from ogd.core.generators.detectors.DetectorEvent import DetectorEvent
from ogd.core.schemas.Event import Event
from ogd.core.schemas.ExtractionMode import ExtractionMode

class RegionEnter(Detector):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    # *** Implement abstract functions ***

    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["player_waddle"] # >>> fill in names of events this Detector should use for detecting whatever you're looking for. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        # >>> use the data in the Event object to update state variables as needed. <<<
        # Note that this function runs once on each Event whose name matches one of the strings returned by _getEventDependencies()
        #
        # e.g. check if the event name contains the substring "Click," and if so set self._found_click to True
        # if "Click" in event.EventName:
        #     self._found_click = True
        old_position = { "x" : event.EventData.get("old_posX"), "y" : event.EventData.get("old_posY"), "z" : event.EventData.get("old_posZ")}
        new_position = { "x" : event.EventData.get("posX"),     "y" : event.EventData.get("posY"),     "z" : event.EventData.get("posZ")}

        self._old_region = "NoRegion"
        self._new_region = "NoRegion"

        for region in self._region_map:
            if (old_position['x'] > region['minX'] and 
                old_position['x'] < region['maxX'] and
                old_position['y'] > region['minY'] and
                old_position['y'] < region['maxY'] and
                old_position['z'] > region['minZ'] and
                old_position['z'] < region['maxZ']):
                self._old_region = region['name']
            if (new_position['x'] > region['minX'] and 
                new_position['x'] < region['maxX'] and
                new_position['y'] > region['minY'] and
                new_position['y'] < region['maxY'] and
                new_position['z'] > region['minZ'] and
                new_position['z'] < region['maxZ']):
                self._new_region = region['name']

        self._session_id = event.SessionID
        self._last_timestamp = event.Timestamp
        self._last_index = event.EventSequenceIndex
    
    def _trigger_condition(self) -> bool:
        """_summary_
        """
        # >>> use the detector's state data to determine if conditions are met to trigger an event. <<<
        # Note that this function also runs once for each Event, after the _extractFromEvent(...) function is done.
        #
        # e.g. check if we have found a click event, and if so, we want to trigger the custom detector Event.
        #      in the 'True' case, we also set self._found_click back to False, so that the trigger condition is False until a new click Event is found.
        # if self._found_click == True:
        #     self._found_click = False
        #     return True
        # else:
        #     return False
        # note the code above is redundant, we could just return self._found_click to get the same result;
        # the more-verbose code is here for illustrative purposes.
        if (self._old_region != self._new_region) and (self._new_region != "NoRegion"):
            return True
        else:
            return False

    def _trigger_event(self) -> Optional[Event]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = DetectorEvent(session_id=self._session_id, app_id="PENGUINS", timestamp=self._last_timestamp,
                                        event_name="region_enter", event_data={"region":self._new_region}, event_sequence_index=self._last_index)
        # >>> use state variables to generate the detector's event. <<<
        # >>> definitely don't return all these "Not Implemented" things, unless you really find that useful... <<<
        # e.g. for an (admittedly redundant) Event stating a click of any kind was detected:
        # ret_val : Event = Event(session_id="Unknown", app_id="CustomGame", timestamp=datetime.now(),
        #                         event_name="ClickDetected", event_data={})
        # note the code above doesn't provide much useful information to the Event;
        # we may want to use additional state variables to capture the session_id, app_id, timestamp, etc. from the click Event in _extractFromEvent(...)
        # further note the event_data can contain any extra data you desire; its contents are entirely up to you.
        return ret_val

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, params:GeneratorParameters, trigger_callback:Callable[[Event], None], region_map:List[Dict[str, Any]]):
        super().__init__(params=params, trigger_callback=trigger_callback)
        self._region_map = region_map
        self._old_region = "N/A"
        self._new_region = "N/A"
        self._session_id = "N/A"
        self._last_timestamp = datetime(2020,1,1)
        self._last_index = 0
        # >>> create/initialize any variables to track detector state <<<
        #
        # e.g. To track whether detector found a click event yet:
        # self._found_click : bool = False

    # *** PUBLIC STATICS ***

    # *** PUBLIC METHODS ***

    # *** PRIVATE STATICS ***

    # *** PRIVATE METHODS ***
