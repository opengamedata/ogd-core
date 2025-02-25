# Game: TRANSFORMATION_QUEST

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

The individual fields encoded in the *event_data* Event element for each type of event logged by the game.  

### **begin_game**

When a new game is started

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **continue_game**

When the player chooses to resume an existing game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **enter_code**

When the player submits a player ID code, to bring up the 'continue' option

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| code | str | The player ID code the player entered | |

#### Other Elements

- None  

### **click_tutorial_next**

When the player clicks the 'next' button in the game intro tutorial

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| from_index | int | The page number of the tutorial the player was at, *before* clicking the 'next' button. | |

#### Other Elements

- None  

### **click_tutorial_back**

When the player clicks the 'back' button in the game intro tutorial

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| from_index | int | The page number of the tutorial the player was at, *before* clicking the 'back' button. | |

#### Other Elements

- None  

### **select_level**

When the player clicks a level from the main map, which they may then click to play

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level | int | The number of the level selected.  NOTE: the `game_state` will have a `level` of null, indicating the `select_level` event occurred in the map; the `event_data` instance of `level` is the number of the level selected. | |
| level_shields | List[enum(BRONZE, SILVER, GOLD)] | A list of which shields the player had previously earned on the level. | |

#### Other Elements

- None  

### **click_level_play**

When the player clicks the 'play' button to enter a level from the level's 'mission' pop-up.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_display_level_rules**

When the player clicks the button to display the selected level's rules.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_level_rules_next**

When the player clicks the 'next' button in the level rules

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| from_index | int | The page number of the rules the player was at, *before* clicking the 'next' button. | |

#### Other Elements

- None  

### **click_level_rules_back**

When the player clicks the 'back' button in the level rules

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| from_index | int | The page number of the rules the player was at, *before* clicking the 'back' button. | |

#### Other Elements

- None  

### **click_level_rules_exit**

When the player clicks the 'x' button to leave the level rules, returning them to the level 'mission' pop-up.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| from_index | int | The page number of the rules the player was at, *before* clicking the 'exit' button. | |

#### Other Elements

- None  

### **click_level_rules_finish**

When the player clicks the button to 'finish' reading the level rules, returning them to the level 'mission' pop-up.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_level_mission**

When the player clicks the 'mission' button from inside a level, to display the level 'mission' pop-up.  NOTE: when the 'mission' pop-up is currently displayed, the player can click the 'mission' button to dismiss the pop-up; however this triggers a `click_dismiss_mission` event, **not** a `click_level_mission`.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_dismiss_mission**

When the player is in the level 'mission' pop-up, and clicks the 'mission' button to dismiss the pop-up.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_open | float | The number of seconds the objectives pop-up was open. | |

#### Other Elements

- None  

### **click_return_to_map**

When the player is in a level, and clicks the button to return to the map.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_replay_level**

When the player has just successfully completed a level, and clicks the 'replay' button in the level feedback pop-up.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_next_level**

When the player is in a level, and clicks the 'next level' button, which technically just returns them to the map.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **select_new_block**

When the player selects a new block type in the sidebar, which they can then add to the sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block_type | enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS) | The type of block selected in the sidebar | |
| block_params | Dict[str, int] | A mapping of the block parameters to the param values. Varies by block type. | |

#### Other Elements

- None  

### **add_new_block**

When the player clicks to add the selected block to the sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block_id | Unknown | TODO: determine if there is an ID associated with each block | |
| block_index | int | The index of the newly-added block within the sequence/loop | |
| in_loop | bool | A boolean indicator of whether the block was placed into a loop or not. | |
| loop_id | Unknown | TODO: determine if there is an ID associated with each loop block | |
| block_type | enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS) | The type of block added to the sequence | |
| block_params | Dict[str, int] | A mapping of the block parameters to the param values. Varies by block type. | |

#### Other Elements

- None  

### **delete_block**

When the player clicks to remove the selected block from the sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block_id | Unknown | TODO: determine if there is an ID associated with each block | |
| block_index | int | The index of the block within the sequence/loop, before it was removed. | |
| in_loop | bool | A boolean indicator of whether the block was in a loop or not. | |
| loop_id | Unknown | TODO: determine if there is an ID associated with each loop block | |
| block_type | enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS) | The type of block that was removed from the sequence | |
| block_params | Dict[str, int] | A mapping of the block parameters to the param values. Varies by block type. | |

#### Other Elements

- None  

### **drag_block**

When the player clicks and drags a block to a new spot in the sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block_id | Unknown | TODO: determine if there is an ID associated with each block | |
| from_index | int | The index of the block within the sequence/loop, before it was dragged. | |
| new_index | int | The index of the block within the sequence/loop, after it was dragged and dropped. | |
| in_loop | bool | A boolean indicator of whether the block is in a loop or not. | |
| loop_id | Unknown | TODO: determine if there is an ID associated with each loop block | |
| block_type | enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS) | The type of block that was moved within the sequence | |
| block_params | Dict[str, int] | A mapping of the block parameters to the param values. Varies by block type. | |

#### Other Elements

- None  

### **set_block_parameter**

When the player clicks and drags a block to a new spot in the sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| block_id | Unknown | TODO: determine if there is an ID associated with each block | |
| block_type | enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS) | The type of block that was moved within the sequence | |
| changed_param | str | The name of the parameter that was changed. | |
| old_value | int | The value of the parameter, before it was changed. | |
| new_value | int | The value of the parameter, after it was changed. | |

#### Other Elements

- None  

### **run_sequence**

When the player clicks the button to run a code block sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| sequence_elements | List[Dict] | A list of all elements in the sequence of blocks the player is about to run. |**block_id** : TODO: determine if there is an ID associated with each block, **block_index** : int, **block_type** : enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS), **loop_subelements** : List[Dict], **block_params** : Dict[str, int] |

#### Other Elements

- None  

### **dismiss_sequence_feedback**

When the player clicks to leave the pop-up feedback after running a sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_open | float | The number of seconds the objectives pop-up was open. | |

#### Other Elements

- None  

### **dismiss_legend**

When the player clicks to leave the pop-up indicating what each symbol means.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_open | float | The number of seconds the objectives pop-up was open. | |

#### Other Elements

- None  

### **dismiss_objectives**



#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_open | float | The number of seconds the objectives pop-up was open. | |

#### Other Elements

- None  

### **tutorial_displayed**

When the game shows a page of the initial game tutorial to the player, including when the player clicks 'next' or 'back' within the tutorial pop-up.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tutorial_index | int | The index of the displayed tutorial page, among all pages in the tutorial. | |
| tutorial_text | str | The actual text content being displayed. | |

#### Other Elements

- None  

### **navigation_displayed**

When the game shows the 'map' of levels to the player.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| levels | List[Dict] | A list of levels displayed in the navigation area. |**level_name** : str, **status** : enum(UNAVAILABLE, AVAILABLE, BRONZE, SILVER, GOLD) |

#### Other Elements

- None  

### **level_mission_displayed**

When the 'mission' pop-up for a level is displayed, allowing the player to review the 'rules' or click 'play'. This occurs when a player starts a level they have not yet completed, or when the player clicks the 'mission' button

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_text | str | The actual 'mission' text content displayed in the pop-up menu. | |

#### Other Elements

- None  

### **level_rules_displayed**

When the player clicks to view the 'rules' of a level, or clicks for the 'next' page of rules, and a new 'rules' page is displayed.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| rules_index | int | The page number of the rules page being displayed. | |
| rules_text | str | The actual text content displayed in the current rule pane. | |

#### Other Elements

- None  

### **objectives_displayed**



#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| bronze_objective_text | str | The text content indicating what the objectives are to obtain a bronze shield on the current level. | |
| silver_objective_text | str | The text content indicating what the objectives are to obtain a silver shield on the current level. | |
| gold_objective_text | str | The text content indicating what the objectives are to obtain a gold shield on the current level. | |

#### Other Elements

- None  

### **legend_displayed**



#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **sequence_updated**

Anytime the sequence changes, whether from a drag-and-drop, adding a block, removing a block, or modifying a block, this event shows the updated state of the sequence.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| sequence_elements | List[Dict] | A list of all elements in the sequence of blocks after the sequence was updated by a player action. |**block_id** : TODO: determine if there is an ID associated with each block, **block_index** : int, **block_type** : enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS), **loop_subelements** : List[Dict], **block_params** : Dict[str, int] |

#### Other Elements

- None  

### **sequence_execution_step**

When the sequence is being executed, and the next step runs.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| type | enum(TRANSLATE_HORIZONTAL, TRANSLATE_VERTICAL, ROTATE_CW_90, ROTATE_CCW_90, ROTATE_ABOUT_CW_90, ROTATE_ABOUT_CCW_90, REFLECT_ACROSS_X_VAL, REFLECT_ACROSS_Y_VAL, REFLECT_ACROSS_X_AXIS, REFLECT_ACROSS_Y_AXIS) | The type of block that ran in this step. | |
| moves_count | int | The number of moves made so far in the sequence, including this move. | |
| blue_gems | int | The total number of blue gems collected so far in the sequence, including any collected on this move. | |
| yellow_gems | int | The total number of yellow gems collected so far in the sequence, including any collected on this move. | |
| stamp_points | int | The total number of points gained from stamps so far in the sequence, including any collected on this move. | |
| outcome | enum(NONE, OUT_OF_BOUNDS, MONSTER, STAMP_1_POINT, STAMP_2_POINT, GEM_YELLOW, GEM_BLUE, GOAL) | The result of the step executing, which could be none, or could represent progress or a level failure. | |
| rules_text | str | The text content the rules page the player was at, before clicking the 'exit' button. | |

#### Other Elements

- None  

### **sequence_fail_displayed**

When the player's sequence ends in a failure, and the feedback is displayed

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| outcome | enum(OUT_OF_BOUNDS, COLLISION, FAILED_OBJECTIVE) | The failure outcome at the end of the execution. | |
| outcome_title | str | The literal text at at the top of the pop-up, indicating the type of outcome. | |
| outcome_text | str | The main text block of the pop-up, indicating what the player did wrong, or what they should do next | |
| moves_count | int | The final number of moves indicated in the 'moves' counter. | |
| level_shields | List[enum(BRONZE, SILVER, GOLD)] | A list of which shields the player has earned on this level. | |
| collected_items | Dict[str, int] | A summary of how many of each type of item the player collected during execution. |**blue_gems** : int, **yellow_gems** : int, **stamp_points** : int |

#### Other Elements

- None  

### **sequence_success_displayed**

When the player's sequence ends in a success, and the feedback is displayed

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| outcome | enum(EARNED_BRONZE, EARNED_SILVER, EARNED_GOLD) | The success outcome at the end of the execution. | |
| outcome_title | str | The literal text at at the top of the pop-up, indicating the type of outcome. | |
| outcome_text | str | The main text block of the pop-up, indicating what the player can do next | |
| moves_count | int | The final number of moves indicated in the 'moves' counter. | |
| level_shields | List[enum(BRONZE, SILVER, GOLD)] | A list of which shields the player has earned on this level, including the shield earned on this successful execution. | |
| collected_items | Dict[str, int] | A summary of how many of each type of item the player collected during execution. |**blue_gems** : int, **yellow_gems** : int, **stamp_points** : int |

#### Other Elements

- None  

### **level_begin**

A progression event indicating when a player actually began a new level, whether by entering from the map or replaying a level. NOTE: this occurs after they entered the level, so the level number is recorded in `game_state`, not `event_data`.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **level_complete**

A progression event indicating when a player completed a level, and is about to return to the main navigation menu. NOTE: this occurs just before they leave the level, so the level name is recorded in `game_state`, not `event_data`.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **level_quit**

A progression event indicating when a player has chosen to quit a level, and is about to return to the main navigation menu. NOTE: this occurs just before they leave the level, so the level name is recorded in `game_state`, not `event_data`.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

None

No changelog prepared

