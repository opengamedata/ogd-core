# Game: CENSIO_SLIDE

No game-specific readme content prepared

## Field Day Open Game Data

Retrieved from https://fielddaylab.wisc.edu/opengamedata
These anonymous data are provided in service of future educational data mining research.
They are made available under the Creative Commons CCO 1.0 Universal license.
See https://creativecommons.org/publicdomain/zero/1.0/

### Suggested citation

#### Field Day. (2019). Open Educational Game Play Logs - [dataset ID]. Retrieved [today's date] from https://opengamedata.fielddaylab.wisc.edu/

## Database Columns

The individual columns recorded in the database for this game.

**session_id** : *str* - session_id, Unique identifier for the gameplay session  
**user_id** : *str* - user_id, Unique identifier for the player  
**user_data** : *json* - user_data, Additional metadata about the player  
**client_time** : *datetime* - client_time, The client machine time when the event was generated  
**client_offset** : *timedelta* - client_offset, The time difference between local client time and GMT  
**server_time** : *datetime* - server_time, The server machine time when the event was logged  
**event_name** : *str* - event_name, The type of event logged  
**event_data** : *json* - event_data, Data specific to an event type, encoded as a JSON string  
**event_source** : *enum('GAME', 'DETECTOR')* - event_source, The generator of the event  
**game_state** : *json* - game_state, Additional metadata about the state of the game when the event was logged  
**app_version** : *str* - app_version, The version of the game from which the event came  
**app_branch** : *str* - app_branch, The branch of the game code from which the event came  
**log_version** : *int* - log_version, The version of the logging code from which the event came  
**event_sequence_index** : *int* - event_sequence_index, Counter of events in the session, from 0. A row with session_n = i is the (i+1)-th event of the session  
**remote_addr** : *str* - remote_addr, The IP address for the player's computer  
**http_user_agent** : *str* - http_user_agent, Data on the type of web browser, OS, etc. in use by the player  

## Event Object Elements

The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.

**session_id** = Column '*session_id*' (index 0)  
**app_id** = null  
**timestamp** = Column '*client_time*' (index 3)  
**event_name** = Columns '*6*'  
**event_data** = Column '*{'event_data': 7, 'server_time': 5, 'http_user_agent': 15}*' (DEBUG: Type <class 'dict'>)  
**event_source** = null  
**app_version** = Column '*app_version*' (index 10)  
**app_branch** = Column '*app_branch*' (index 11)  
**log_version** = Column '*log_version*' (index 12)  
**time_offset** = Column '*client_offset*' (index 4)  
**user_id** = Column '*user_id*' (index 1)  
**user_data** = Column '*user_data*' (index 2)  
**game_state** = Column '*game_state*' (index 9)  
**event_sequence_index** = Column '*event_sequence_index*' (index 13)  



## Logged Events  

The individual fields encoded in the *game_state* and *user_data* Event element for all event types, and the fields in the *event_data* Event element for each individual event type logged by the game.  

### Enums  

| **Name** | **Values** |
| ---      | ---        |
| BlockType | ['WIRE', 'POWER', 'TRANSISTOR'] |
| MovementConstraint | ['NO_ROTATE', 'NO_VERTICAL', 'NO_HORIZONTAL'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched. | |
| level | int | The current level the player is in. | |
| move_count | int | The number of moves the player has made on the current level. | |
| level_max_moves | int | The maximum number of moves allowed in the current level. | |
| board | N/A | TODO - Placeholder for some representation of the board state. |**N/A** : N/A |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **session_start**

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **game_start**

When the player starts a new game (at present, this happens automatically at launch, but in the future the player may launch a new game from a menu).

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **level_menu_displayed**

When the system displays a list of the game's levels.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| unlocked_levels | List[Dict] | A list of all currently-unlocked levels, each indicating the level number, max moves allowed, and the player's best score, or null if unplayed. |**level_id** : int, **level_max_moves** : int, **best_score** : int | null |
| locked_levels | List[Dict] | A list of all currently-locked levels, each indicating the level number and max moves allowed. |**level_id** : int, **level_max_moves** : int |

#### Other Elements

- None  

### **level_tier_unlocked**

When the player completes a tier of levels, and the system shows the next tier being unlocked.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| unlocked_levels | List[Dict] | A list of the newly-unlocked levels, each indicating the level number and max moves allowed. |**level_id** : int, **level_max_moves** : int |

#### Other Elements

- None  

### **click_select_level**

When the player selects a level from the menu.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the level. | |
| level_max_moves | int | The max number of moves allowed in the level. | |
| best_score | int | null | The player's best score on the level, or null if they have not previously played the level. | |

#### Other Elements

- None  

### **click_reset**

When the player clicks the button to reset the current puzzle.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_confirm_reset**

When the player clicks the button to confirm they want to reset the current puzzle.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_cancel_reset**

When the player clicks the button to cancel resetting the current puzzle.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **select_block**

When the player selects a level from the menu.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block | TBD | TODO - Placeholder for some representation of an individual block. | |
| position | List[int] | The board coordinates of the selected block's anchor point. | |
| is_connected | bool | Indicator for whether the selected block is currently connected to power (i.e. whether the wire is green or red). | |

#### Other Elements

- None  

### **place_block**

When the player moves the selected block to a new position.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block | TBD | TODO - Placeholder for some representation of an individual block. | |
| position | List[int] | The board coordinates at which the selected block's anchor point was placed. | |
| is_connected | bool | Indicator for whether the block is now connected to power (i.e. whether the wire is green or red). | |
| new_move_count | bool | The total moves the player has made on the current puzzle, after placing the block. | |

#### Other Elements

- None  

### **rotate_block**

When the player clicks to rotate a block to a new orientation.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block | TBD | TODO - Placeholder for some representation of an individual block. | |
| old_orientation | int | The orientation of the block before rotation, relative to its default, in degrees. | |
| new_orientation | int | The orientation of the block after being rotated, relative to its default, in degrees. | |
| is_connected | bool | Indicator for whether the block is now connected to power (i.e. whether the wire is green or red). | |
| new_move_count | bool | The total moves the player has made on the current puzzle, after placing the block. | |

#### Other Elements

- None  

### **block_destinations_highlighted**

When the system displays higlighting on the puzzle board for where the currently-selected block may be placed.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| highlighted_spaces | List[List] | A list of board coordinates, each indicating a highlighted space on the puzzle board. | |

#### Other Elements

- None  

### **puzzle_solved**

When the puzzle enters the 'solved' state after the player has moved all pieces to complete the circuit.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **puzzle_solution_lost**

When the player makes a move after previously solving the puzzle, taking the puzzle out of the 'solved' state.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_complete_level**

When the player clicks the button to complete the level, when the puzzle is in the 'solved' state.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_quit_level**

When the player clicks the button to quit the current level.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_request_hint**

TODO - Placeholder for when hinting is implemented in the game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **select_hint_block**

TODO - Placeholder for when hinting is implemented in the game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **block_hint_displayed**

TODO - Placeholder for when hinting is implemented in the game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **start_survey**

When the player enters into a survey after a level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |

#### Other Elements

- None  

### **survey_item_displayed**

When the system displays a multi-choice (i.e. select one) survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| prompt | str | The text content of the item prompt. | |
| choices | List[str] | The list of possible choices for the survey item. | |

#### Other Elements

- None  

### **select_survey_response**

When the player clicks on a choice in a multi-choice survey item, selecting the choice.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| choice_value | int | The index of the selected choice among the available choices, or the value (if the multi-choice item uses a Likert scale or similar). | |
| choice_string | str | The text content of the selected choice. | |

#### Other Elements

- None  

### **submit_survey_response**

When the player clicks to submit their choice on a multi-choice survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| choice_value | int | The index of the submitted choice among the available choices, or the value (if the multi-choice item uses a Likert scale or similar). | |
| choice_string | str | The text content of the submitted choice. | |

#### Other Elements

- None  

### **end_survey**

When the player finishes a survey

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

None  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.

No changelog prepared

