from typing import Optional
from ogd.common.models.Event import Event

def _getIndexNameFromEvent(event: Event) -> Optional[str]:
    """
    Extract puzzle index name from an event. 
    Intended for Job Graph related features (e.g. TopJobCompletionDestinations).
    
    Args:
        event: The event to extract the puzzle name from
        
    Returns:
        A string in the format "lv{level}-{puzzle_lower}" or None if puzzle is not found
    """
    level = event.GameState.get("level", None)
    puzzle = event.EventData.get("puzzle", None)
    if puzzle is None:
        return None
    # Convert puzzle enum to lowercase for mapping
    puzzle_lower = puzzle.lower()
    return f"lv{level}-{puzzle_lower}"
