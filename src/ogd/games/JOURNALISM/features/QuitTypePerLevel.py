# import libraries
import json
from typing import Any, Final, List, Optional
import json
# import local files
from ogd.core.generators.extractors.PerLevelFeature import PerLevelFeature
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode
from ogd.core.models.FeatureData import FeatureData
from ogd.core.generators.Generator import GeneratorParameters


"""

"""


class QuitTypePerLevel(PerLevelFeature):
    """Template file to serve as a guide for creating custom Feature subclasses for games.

    :param Feature: Base class for a Custom Feature class.
    :type Feature: _type_
    """

    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        
        ##event boolean watchers
        self._store_event: Optional[Event] = None
        self._display_feedback: bool = False
        self._start_level: bool = False
        self._resumed_checkpoint: bool = False
        self._reached_checkpoint: bool = False
        self._level_fail: bool = False

        self._event_watchers : List[str] = ["complete_level", "display_feedback_dialog", "resumed_checkpoint", "level_fail", "reached_checkpoint"]

        ##feature booleans:
        self._between_levels : bool = False
        self._on_fail : bool = False
        self._on_checkpoint : bool = False
        self._other : bool = False

        

        #buffer for event margin before quit type is no longer considered something besides "other"
        self._BUFFER_LIMIT: Final[int] = 9
        #counters            
        self._event_counter : int = 0
    

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["all_events"] # >>> fill in names of events this Feature should use for extraction. <<<

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        """_summary_

        :return: _description_
        :rtype: List[str]
        """
        return ["QuitType"] # >>> fill in names of first-order features this Feature should use for extraction. <<<

    def _updateFromEvent(self, event:Event) -> None:
        """_summary_

        :param event: _description_
        :type event: Event
        """
        if(self._store_event == None):
            self._store_event= event
        # >>> use the data in the Event object to update state variables as needed. <<<
        # Note that this function runs once on each Event whose name matches one of the strings returned by _eventFilter()
        #
        # e.g. check if the event name contains the substring "Click," and if so set self._found_click to True
        if(self._event_counter >= self._BUFFER_LIMIT):
            self._event_counter = 0
            self._store_event = event
        elif(self._event_counter != -1 and not('display_' in event.EventName)):
            self._event_counter += 1
        
        if(event.EventName in self._event_watchers):
            #these events have a window of margin longer than BUFFER_LIMIT
            if(event.EventName == "display_feedback_dialog" or event.EventName == "level_fail"):
                self._event_counter=-1
                self._store_event = event

            else:
                self._event_counter = 0
                if(event.EventName=="resumed_checkpoint"):
                    if(event.EventData["origin"]=="LevelFail"):
                        #do NOT overwrite the level_fail in store_event with a resumed_checkpoint from level_fail(preserve level_fail)
                        #start counting with buffer again at this point though
                        pass
                    else:
                        self._store_event = event
                elif(event.EventName=="complete_level"):
                    #do NOT overwrite the display_feedback in store_event
                    #start counting again though
                    pass
                #only store "reached_checkpoint" if we aren't on a new level begin
                elif(not(event.EventName == "reached_checkpoint" and self._store_event != "display_feedback")):
                    self._store_event = event
                    
                else:
                    pass
                    #self._store_event = event
                    


                

        


        return

    def _updateFromFeatureData(self, feature: FeatureData):
        """_summary_

        :param feature: _description_
        :type feature: FeatureData
        """
        # >>> use data in the Feature Data object to update state variables as needed. <<<
        # Note: This function runs on data from each Feature whose name matches one of the strings returned by _featureFilter().
        #       The number of instances of each Feature may vary, depending on the configuration and the unit of analysis at which this CustomFeature is run.
        return

    def _getFeatureValues(self) -> List[Any]:
        """_summary_

        :return: _description_
        :rtype: List[Any]
        """
        
       

        string_val : Optional[str]
        try:
            if(self._store_event.EventName == "display_feedback_dialog"):
                string_val = "BetweenLevels"
                self._between_levels = True
            elif(self._store_event.EventName == "level_fail"):
                string_val = "OnFail"
                self._on_fail = True
            elif(self._store_event.EventName == "reached_checkpoint"):
                string_val= "OnCheckpoint"
                self._on_checkpoint = True

            else:
                string_val = "Other"
                self._other = True
        except:
            string_val = "null"

        return [string_val, self._between_levels, self._on_fail, self._on_checkpoint, self._other]


    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["BetweenLevels","OnFail", "OnCheckpoint", "Other"] # >>> fill in names of Subfeatures for which this Feature should extract values. <<<
    
    @staticmethod
    def AvailableModes() -> List[ExtractionMode]:
        ##don't make available for grouping by playerID
        return [ExtractionMode.POPULATION,ExtractionMode.PLAYER, ExtractionMode.SESSION] # >>> delete any modes you don't want run for your Feature. <<<
    
    # @staticmethod
    # def MinVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the minimum logging version for events to be processed by this Feature. <<<
    #     return super().MinVersion()

    # @staticmethod
    # def MaxVersion() -> Optional[str]:
    #     # >>> replace return statement below with a string defining the maximum logging version for events to be processed by this Feature. <<<
    #     return super().MaxVersion()
