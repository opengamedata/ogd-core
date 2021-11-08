from schemas import Event
from typing import Any, List, Union
# local imports
from extractors.PerLevelFeature import PerLevelFeature
from schemas.Event import Event

class OffsetGoodMoveCount(PerLevelFeature):
    def __init__(self, name:str, description:str, count_index:int):
        PerLevelFeature.__init__(self, name=name, description=description, count_index=count_index)
        self._count = 0

    def GetEventTypes(self) -> List[str]:
        return ["CUSTOM.1", "CUSTOM.2"]
        # return ["SLIDER_MOVE_RELEASE", "ARROW_MOVE_RELEASE"]

    def CalculateFinalValues(self) -> Any:
        return self._count

    def _extractFromEvent(self, event:Event) -> None:
        if event.event_data['slider'].upper() == 'OFFSET':
            if ('end_closeness' in event.event_data.keys() and 'begin_closeness' in event.event_data.keys()):
                if event.event_data['end_closeness'] > event.event_data['begin_closeness']:
                    self._count += 1
            else:
                print(f"Weird feature extraction error - didn't find closeness in a supposed offset event. Data: event_name={event.event_name}, event_data keys={event.event_data.keys()}")

    def MinVersion(self) -> Union[str,None]:
        return None

    def MaxVersion(self) -> Union[str,None]:
        return None
