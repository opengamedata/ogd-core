# import libraries
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Type
# import local files
from ogd.core.generators.extractors.builtin.BuiltinExtractor import BuiltinExtractor
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event

class Timespan(BuiltinExtractor):
    """Universal feature for finding the span of time between the first occurrence of a "start" event, and last occurrence of an "end" event."""
    _start_event = "NO EVENT"
    _end_event   = "NO EVENT"

    def __init__(self, params:GeneratorParameters, schema_args:Dict[str,Any]):
        if params._count_index is not None and params._count_index != 0:
            self.WarningMessage(f"Session feature {params._name} got non-zero count index of {params._count_index}!")
        params._count_index = 0
        super().__init__(params=params, schema_args=schema_args)
        self._start_time : Optional[datetime] = None
        self._end_time   : Optional[datetime] = None
        self._span = timedelta()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***

    @classmethod
    def _createDerivedGenerator(cls, params:GeneratorParameters, schema_args:Dict[str,Any]) -> Type[BuiltinExtractor]:
        class_params = {
            "_start_event" : schema_args.get("start_event", cls._start_event),
            "_end_event"   : schema_args.get("end_event",   cls._end_event)
        }
        return type(params._name, (Timespan,), class_params)

    @classmethod
    def _eventFilter(cls) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return [cls._start_event, cls._end_event]

    @classmethod
    def _featureFilter(cls) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return []

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        match event.EventName:
            case self._start_event:
                if self._start_time is not None:
                    self.WarningMessage(f"{self.Name} received a second {self._start_event} (start-of-span) event! This occurred {event.Timestamp - self._start_time} after the initial {self._start_event} event.")
                else:
                    self._start_time = event.Timestamp
            case self._end_event:
                if self._start_time is not None:
                    if self._end_time is not None:
                        self.WarningMessage(f"{self.Name} received a second {self._end_event} (end-of-span) event! This occurred {event.Timestamp - self._end_time} after the initial {self._end_event} event. Using the later event's timestamp for span.")
                    self._end_time = event.Timestamp
                else:
                    self.WarningMessage(f"{self.Name} received a {self._end_event} event (end-of-span event) when no {self._start_event} event (start-of-span event) had occurred!")
            case _:
                pass
        return

    def _updateFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        ret_val : List[float]
        if self._start_time is not None and self._end_time is not None:
            ret_val = [(self._end_time - self._start_time).total_seconds()]
        else:
            ret_val = [0]
        return ret_val

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return [] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def MinVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
        return None

    @staticmethod
    def MaxVersion() -> Optional[str]:
        # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
        return None
