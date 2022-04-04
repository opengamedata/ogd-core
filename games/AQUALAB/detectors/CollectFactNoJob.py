# import standard libraries
from datetime import datetime
from typing import Any, List, Union
# import local files
from features.Feature import Feature
from features.FeatureData import FeatureData
from schemas.Event import Event

class CustomFeaature(Feature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """
    def __init__(self, name:str, description:str, job_map:dict):
        super().__init__(name=name, description=description, count_index=0)
        # >>> create/initialize any variables to track feature extractor state <<<
        #
        # e.g. To track whether extractor found a click event yet:
        # self._found_click : bool = False

    # *** Implement abstract functions ***
    def _getEventDependencies(self) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [] # >>> fill in names of events this Feature should use for extraction. <<<

    def _extractFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        # >>> use the data in the Event object to update state variables as needed. <<<
        # Note that this function runs once on each Event whose name matches one of the strings returned by _getEventDependencies()
        #
        # e.g. check if the event name contains the substring "Click," and if so set self._found_click to True
        # if "Click" in event.event_name:
        #     self._found_click = True
        return

    def _trigger(self) -> Union[Event, None]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : Event = Event(session_id="Not Implemented", app_id="Not Implemented", timestamp=datetime.now(),
                                event_name="CustomDetector", event_data={})
        # >>> use state variables to calculate the return value(s) of the base Feature and any Subfeatures. <<<
        # >>> put the calculated value(s) into a list as the function return value. <<<
        # >>> definitely don't return ["template"], unless you really find that useful... <<<
        #
        # e.g. use the self._found_click, which was created/initialized in __init__(...), and updated in _extractFromEvent(...):
        # if self._found_click:
        #     ret_val = [True]
        # else:
        #     ret_val = [False]
        # return ret_val
        #
        # note the code above is redundant, we could just return [self._found_click] to get the same result;
        # the more-verbose code is here for illustrative purposes.
        return ret_val

    def MinVersion(self) -> Union[str,None]:
        # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
        return super().MinVersion()

    def MaxVersion(self) -> Union[str, None]:
        # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
        return super().MaxVersion()
