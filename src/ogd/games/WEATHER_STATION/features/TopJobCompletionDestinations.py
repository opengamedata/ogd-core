from collections import Counter
from typing import Any, List, Optional

from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.Feature import Feature
from ogd.common.models.Event import Event
from ogd.common.models.enums.ExtractionMode import ExtractionMode
from ogd.common.models.FeatureData import FeatureData
from collections import defaultdict


class TopJobCompletionDestinations(Feature):
    def __init__(self, params: GeneratorParameters):
        super().__init__(params=params)

        self.cur_session = None
        self.last_completed_puzzle = {} 
        self.current_started_puzzle = {}  # Track the puzzle that was started
        self.puzzle_completion_pairs = defaultdict(lambda: defaultdict(list)) 

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode: ExtractionMode) -> List[str]:
        return ["start_puzzle", "complete_puzzle"]

    @classmethod
    def _featureFilter(cls, mode: ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event: Event) -> None:
        puzzle_name = self._getIndexNameFromEvent(event)
        session_id = event.session_id
        
        if event.EventName == "puzzle_started":
            if session_id != self.cur_session:
                self.cur_session = session_id
            self.current_started_puzzle[session_id] = puzzle_name

        if event.EventName == "puzzle_completed":
            current_puzzle = puzzle_name
            last_puzzle = self.last_completed_puzzle.get(session_id, None)
            print(f"Last completed puzzle: {last_puzzle}, Current completed puzzle: {current_puzzle}, Session: {session_id}")
            
            if last_puzzle and last_puzzle != current_puzzle:
                if session_id not in self.puzzle_completion_pairs[last_puzzle][current_puzzle]:
                    self.puzzle_completion_pairs[last_puzzle][current_puzzle].append(session_id)
                    print(f"Added transition: {last_puzzle} -> {current_puzzle} for session {session_id}")

            self.last_completed_puzzle[session_id] = current_puzzle


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

    def _getIndexNameFromEvent(self, event: Event) -> str:
        level = event.GameState.get("level", None)
        puzzle = event.EventData.get("puzzle", None)
        if puzzle is None:
            return None
        # Convert puzzle enum to lowercase for mapping
        puzzle_lower = puzzle.lower()
        return f"lv{level}-{puzzle_lower}"

    # *** Optionally override public functions. ***
    @staticmethod
    def MinVersion() -> Optional[str]:
        return "1"
