from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from collections import defaultdict
from .utils import _getIndexNameFromEvent

# This feature tracks the puzzle destinations after completing a puzzle.
class TopJobCompletionDestinations(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        self.cur_session = None
        self.previous_completed_puzzle = None
        self.puzzle_completion_pairs = defaultdict(lambda: defaultdict(list)) 

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["start_puzzle", "complete_puzzle"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        puzzle_name = _getIndexNameFromEvent(event)
        session_id = event.SessionID

        # If the session changes, reset the previous completed puzzle
        if session_id != self.cur_session:
            self.cur_session = session_id
            self.previous_completed_puzzle = None

        # If the previous puzzle was completed, add the current puzzle to the completion pairs, regardless of whether it was completed or started
        if self.previous_completed_puzzle != None and self.previous_completed_puzzle != puzzle_name:
            self.puzzle_completion_pairs[self.previous_completed_puzzle][puzzle_name].append(session_id)
            self.previous_completed_puzzle = None # Reset the previous completed puzzle
   
        if event.EventName == "complete_puzzle":
            self.previous_completed_puzzle = puzzle_name

    def _updateFromFeatureData(self, feature: FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        print(f"Puzzle completion pairs: {dict(self.puzzle_completion_pairs)}")
        ret_val = {}

        for src, dests in self.puzzle_completion_pairs.items():
            sorted_dests = sorted(
                dests.items(),
                key=lambda item: len(item[1]),
                reverse=True
            )
            ret_val[src] = {item[0]: item[1] for item in sorted_dests[:5]}
        
        print(f"Return value: {ret_val}")
        return [ret_val]
    

    def Subfeatures(self) -> List[str]:
        return []

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
