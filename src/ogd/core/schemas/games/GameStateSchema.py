# import standard libraries
import logging
from typing import Dict
# import local files
from ogd.core.schemas.games.DataElementSchema import DataElementSchema
from ogd.core.schemas.Schema import Schema
from ogd.core.utils.Logger import Logger

class GameStateSchema(Schema):
    """
    Dumb struct to contain a specification of a game's GameState in a GameSchema file.

    These essentially are just a set of elements in the GameState attribute of the game's Events.
    """
    def __init__(self, name:str, all_elements:Dict[str, Dict]):
        self._game_state  : Dict[str, DataElementSchema]

        if not isinstance(all_elements, dict):
            all_elements   = {}
            Logger.Log(f"For {name} Event config, all_elements was not a dict, defaulting to empty dict", logging.WARN)
        self._game_state = GameStateSchema._parseGameStateElements(event_data=all_elements)
        super().__init__(name=name, other_elements=None)

    @property
    def GameStateElements(self) -> Dict[str, DataElementSchema]:
        return self._game_state

    @property
    def AsMarkdown(self) -> str:
        return "\n\n".join([
            f"### **{self.Name}**",
            "\n".join(
                  [elem.AsMarkdown for elem in self.GameStateElements.values()]
                + (["- Other Elements:"] +
                   [f"  - **{elem_name}**: {elem_desc}" for elem_name,elem_desc in self.NonStandardElements]
                  ) if len(self.NonStandardElements) > 0 else []
            )
        ])

    @property
    def AsMarkdownTable(self) -> str:
        ret_val = [
            f"### **{self.Name}**",
            "#### Event Data",
            "\n".join(
                ["| **Name** | **Type** | **Description** | **Sub-Elements** |",
                 "| ---      | ---      | ---             | ---              |"]
              + [elem.AsMarkdownRow for elem in self.GameStateElements.values()]
            ),
        ]
        if len(self.NonStandardElements) > 0:
            ret_val.append("#### Other Elements")
            ret_val.append(
                "\n".join( [f"- **{elem_name}**: {elem_desc}  " for elem_name,elem_desc in self.NonStandardElements] )
            )
        return "\n\n".join(ret_val)

    @staticmethod
    def _parseGameStateElements(event_data):
        ret_val : Dict[str, DataElementSchema]
        if isinstance(event_data, dict):
            ret_val = {name:DataElementSchema(name=name, all_elements=elems) for name,elems in event_data.items()}
        else:
            ret_val = {}
            Logger.Log(f"event_data was unexpected type {type(event_data)}, defaulting to empty dict.", logging.WARN)
        return ret_val
