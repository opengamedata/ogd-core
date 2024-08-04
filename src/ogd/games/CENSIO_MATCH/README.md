# Game: CENSIO_MATCH

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
| OrderType | ['LEGS', 'HEAD1', 'HEAD2', 'BODY'] |
| OrderStatus | ['COMPLETED', 'FAILED', 'NOT_TRIED'] |
| ToggleType | ['ON', 'OFF'] |
| DropPoint | ['LEFT', 'MIDDLE', 'RIGHT'] |
| PowerType | ['SPIN', 'FLIP', 'SWAP', 'MOVE'] |
| TargetType | ['SPIN', 'FLIP', 'SWAP_ORIGIN', 'SWAP_DESTINATION', 'MOVE_ORIGIN', 'MOVE_DESTINATION'] |
| TileType | ['GEAR', 'NUT', 'SCREW', 'SPRING', 'NONE'] |
| SlideType | ['LEFT', 'DOWN', 'RIGHT'] |
| GoalType | ['Self', 'Other'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched. | |
| order | OrderType | The current order the player is trying to fulfill. | |
| goal_value | int | The goal score the player selected for the current order. Always 0 if the player is in the menu, or in the first order (when a goal has not been set). | |
| goal_type | GoalType | Whether the player selected 'Self' or 'Other' for the current order. `null` if the player is in the menu, or in the first order (when a goal has not been set). | |
| tile_counts | Dict[str, int] | A dict, containing elements to indicate the number of each tile type the player has collected on the current order. |**gear** : int, **nut** : int, **screw** : int, **spring** : int |
| tile_targets | Dict[str, int] | A dict, containing elements to indicate the number of each tile type the player needs to collect to complete the current order. |**gear** : int, **nut** : int, **screw** : int, **spring** : int |
| drop_count | int | The number drops the player has used on the current order. | |
| drop_limit | int | The maximum number of drops the player can use on the current order. | |
| tile_overflow | int | The number of excess tiles the player has collected. | |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **session_start**

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **game_start**

When the player presses the new game button, or resumes.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **game_complete**

When the player completes the last order of the game, thus completing the game itself.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **order_menu_displayed**

When the system displays the order selection menu.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| completed_orders | List[OrderType] | The orders that have been completed so far. | |
| failed_orders | List[OrderType] | The orders that have been attempted, but only failed, so far. | |
| initial_grid | List[List[TileType]] | A list of all rows containing tiles (starting from the bottom of the grid). Each row indicates the types of all tiles in the grid spaces of the row (or NONE for a grid space without a tile). | |  

### **adjust_part_clutter**

When the player selects a new setting for the part clutter on their next order.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| old_clutter | float | The prior level of clutter, on a 0-1 scale. | |
| old_score_adjustment | float | The adjustment contributed to the overall score multiplier, by the prior setting. | |
| new_clutter | float | The newly-selected level of clutter, on a 0-1 scale. | |
| new_score_adjustment | float | The adjustment contributed to the overall score multiplier, by the new setting. | |  

### **adjust_drop_limit**

When the player selects a new setting for the drop limit on their next order.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| old_limit | int | The prior drop limit. | |
| old_score_adjustment | float | The adjustment contributed to the overall score multiplier, by the prior setting. | |
| new_limit | int | The newly-selected drop limit. | |
| new_score_adjustment | float | The adjustment contributed to the overall score multiplier, by the new setting. | |  

### **adjust_drop_speed**

When the player selects a new setting for the drop speed on their next order.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| old_speed | float | The prior drop speed, on a 0-1 scale. | |
| old_score_adjustment | float | The adjustment contributed to the overall score multiplier, by the prior setting. | |
| new_speed | float | The newly-selected drop speed, on a 0-1 scale. | |
| new_score_adjustment | float | The adjustment contributed to the overall score multiplier, by the new setting. | |  

### **grid_updated**

When the system updates the starting grid based on a change to one of the part clutter.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| new_grid | List[List[TileType]] | A list of all rows containing tiles (starting from the bottom of the grid). Each row indicates the types of all tiles in the grid spaces of the row (or NONE for a grid space without a tile). | |  

### **click_select_order**

When the player selects a new order from the menu list.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| new_order | OrderType | The new order the player selected. | |
| status | OrderStatus | The completion status of the selected order (completed, failed only, or not attempted). | |
| order_is_optimal | bool | true if the selected order matches level generation bias/settings | |  

### **click_toggle_order_target**

When the player toggles the 'target' view for the current order on or off.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| toggle | ToggleType | Whether the view was toggled on or off. | |  

### **click_reveal_drop_count**

When the player clicks to reveal the number of drops they have used so far.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_play_order**

When the player clicks to start an order from the menu.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_play_order_invalid**

When the player clicks to start an order from the menu, but has not yet selected a valid order.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **order_begin**

When playing an order actually begins, whether due to the player clicking 'play' from a new level preview, or clicking 'replay' in a level summary.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| order_type | OrderType | The type of the order being attempted. | |
| order_status | OrderStatus | The previous completion status of the order (completed, failed only, or not attempted). | |
| order_is_optimal | bool | True if the selected order matches the level’s most prevalent part. | |
| high_score | int | The previous high score on the order. | |
| part_clutter | float | The level of clutter, on a 0-1 scale. | |
| drop_limit | int | The number of drops allowed on the order. | |
| drop_speed | float | The speed of drops, on a 0-1 scale. | |
| score_multipliers | float | The overall score multiplier on the order, based on the settings. | |
| sandbox_enabled | bool | Whether the order began with the sandbox practice mode enabled or not. | |
| initial_grid | List[List[TileType]] | A list of all rows containing tiles (starting from the bottom of the grid). Each row indicates the types of all tiles in the grid spaces of the row (or NONE for a grid space without a tile). | |  

### **toggle_sandbox**

When the player turns the sandbox practice mode on or off.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| toggle | ToggleType | Whether the sandbox mode was toggled on or off. | |  

### **toggle_power_info**

When the player toggles the 'help' view (i.e. clicks the '?' button) of the 'powers' box on or off.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| toggle | ToggleType | Whether the view was toggled on or off. | |  

### **click_show_help_panel**

When the player clicks the button to display the 'help' overlay at the beginning of a round.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **select_power**

When the player selects a power to use.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| power | PowerType | Which power the player selected. | |  

### **cancel_power**

When the player cancels the use of a selected power.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| power | PowerType | Which power the player canceled. | |  

### **hover_power_target**

When the player hovers over a new target tile for the selected power.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| power | TargetType | Which kind of power target is currently being set. | |
| target_point | List[int] | The x, y coordinates of the targeted point. | |
| target_tile | TileType | The type of tile on the hovered point. | |  

### **execute_power**

When the player clicks to confirm and execute the selected power.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| power | PowerType | Which power the player canceled. | |
| cost | Dict[str, Any] | A dict, indicating which type of tile was spent on the power, and how many tiles were spent. |**type** : TileType, **count** : int |
| tile_updates | List[Dict[str, Any]] | A list of all changes to tile positions, each list element indicating the old and new points for a tile of given type. |**type** : TileType, **old_point** : List[int], **new_point** : List[int] |
| had_tile_overflow | bool | Whether the power spent excess parts which otherwise would have incurred a penalty. TODO: rename to spent_tile_overflow | |  

### **click_reveal_drops**

When the player clicks the 'reveal' button on one of the drop points.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| drop_point | DropPoint | Which drop point the player clicked to reveal. | |
| tile_pairs | List[List[TileType]] | A list of tile pairs revealed in the drop. Empty if the click was not a valid reveal (e.g. if the drop point already had revealed pairs). | |  

### **click_drop_pair**

When the player clicks to drop a new tile pair onto the grid.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| drop_point | DropPoint | Which drop point the player clicked to reveal. | |
| tile_pair | List[TileType] | The types of the two tiles in the pair. | |  

### **drop_pair_landed**

When the a dropping pair of tiles lands on the other tiles below.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_pair | List[Dict[str, Any]] | The types and landed positions of the two tiles in the pair. |**type** : TileType, **point** : List[int] |  

### **rotate_drop_pair**

When the player rotates a dropping pair.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_updates | List[Dict[str, Any]] | A list of changes to tile positions of the two tiles, resulting from the rotation. |**type** : TileType, **old_point** : List[int], **new_point** : List[int] |  

### **slide_drop_pair**

When the player slides a dropping pair left or right, or accelerates the pair down.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_updates | List[Dict[str, Any]] | A list of changes to tile positions of the two tiles, resulting from the slide. |**type** : TileType, **old_point** : List[int], **new_point** : List[int] |  

### **tile_fell**

When the space below a tile is empty, and 'gravity' causes the tile to fall and 'land' on another tile (or ground).

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_update | Dict[str, Any] | A dict indicating what type of tile fell, and which points it started and ended at. |**type** : TileType, **old_point** : List[int], **new_point** : List[int] |  

### **match_completed**

When three or more tiles are in a row, and a match is completed.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| matches | List[Dict[str, Any]] | A dict indicating what type of tile was matched, and the list of points where the matching tiles were located. |**type** : TileType, **tile_points** : List[List[int]] |
| combo_round | int | number of times matches have been made without player intervention (i.e. pieces falling into a match position). | |  

### **order_completed**

When the player has used all drops, completing the order.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| successful | bool | Whether the order was completed successfully or not. | |
| score | int | The score the player earned on the order. | |
| high_score | int | The highest score the player has earned on the given job. | |
| moves_left | int | The number of remaining moves (TODO : determine whether players who complete the order targets with leftover drops are forced to use the remaining drops or not). | |
| sandbox_enabled | bool | Whether the order had the sandbox practice mode enabled or not. | |  

### **order_summary_displayed**

When the system displays a summary of the order results to the player.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| base_score | int | The player score prior to applying the score mulitplier. | |
| score_multiplier | float | The score multiplier on the order. | |
| total_score | int | The final score the player earned on the order. | |
| goal_score | int | The goal score on the order. | |
| player_average | int | The average score the player has scored, across all attempts of the order. | |  

### **toggle_summary_help**

When the player toggles the 'help' view (i.e. clicks the '?' button) of the 'order summary' on or off.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| toggle | ToggleType | Whether the view was toggled on or off. | |  

### **click_try_again**

When the player clicks the button to replay the order

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_new_order**

When the player clicks the button to return to the main menu and choose a new order

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **start_survey**

When the player enters into a survey after a level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |  

### **multichoice_item_displayed**

When the system displays a multi-choice (i.e. select one) survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| prompt | str | The text content of the item prompt. | |
| choices | List[str] | The list of possible choices for the survey item. | |  

### **select_multichoice_response**

When the player clicks on a choice in a multi-choice survey item, selecting the choice.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| choice_value | int | The index of the selected choice among the available choices, or the value (if the multi-choice item uses a Likert scale or similar). | |
| choice_string | str | The text content of the selected choice. | |  

### **submit_multichoice_response**

When the player clicks to submit their choice on a multi-choice survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| choice_value | int | The index of the submitted choice among the available choices, or the value (if the multi-choice item uses a Likert scale or similar). | |
| choice_string | str | The text content of the submitted choice. | |  

### **slider_item_displayed**

When the system displays a slider survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| prompt | str | The text content of the item prompt. | |
| min_value | float | int | The minimum value the player can select on the survey item. | |
| max_value | float | int | The maximum value the player can select on the survey item. | |
| reference_values | List[Dict] | A list of other labeled 'reference' values on the slider scale. Each item in the list gives the reference label as well as its value. |**label** : str, **value** : float | int |
| current_value | float | int | The starting value of the slider. | |  

### **set_slider_position**

When the player drags the slider to a new position.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| prompt | str | The text content of the item prompt. | |
| start_value | float | int | The value of the slider before it was moved. | |
| end_value | float | int | The value to which the player set the slider. | |
| reference | str | null | The label of the reference value, if the new slider value matches one of the slider reference value, otherwise null. | |  

### **submit_slider_response**

When the player clicks to submit their choice on a slider survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| prompt | str | The text content of the item prompt. | |
| value | float | int | The value of the slider when the item was submitted. | |
| reference | str | null | The label of the reference value, if the slider was set to one of the slider reference values, otherwise null. | |  

### **end_survey**

When the player finishes a survey

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |  

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

