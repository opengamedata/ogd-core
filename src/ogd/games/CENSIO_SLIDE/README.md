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
| MovementConstraint | ['NO_ROTATE', 'NO_VERTICAL', 'NO_HORIZONTAL'] |
| ShapeFlag | ['Basic', 'Locked', 'ConstrainedHorizontal', 'ConstrainedVertical', 'Rotate', 'Goal'] |
| CardinalDirection | ['N', 'E', 'S', 'W'] |
| EdgeType | ['OPEN', 'CLOSED'] |
| RotationType | ['CW', 'CCW', 'NONE'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched. | |
| level | int | The current level the player is in. | |
| move_count | int | The number of moves the player has made on the current level. | |
| level_max_moves | int | The maximum number of moves allowed in the current level. | |
| board | List[Dict[str, Any]] | A list of all shapes currently on the game board. Each shape is a sub-dictionary that includes 'flags' indicating any special attributes of the shape, and an index in the overall list for cross-referencing. They also include a 2D 'map' of the shape, which uses 0 (empty) and 1 (filled) to indicate the shape within a bounding box of board tiles. Finally, they include the position of the upper-left corner of the block map, in global coordinates. |**shape_flags** : List[ShapeFlag], **shape_index** : int, **position** : Dict[str, int], **block_map** : List[List[int]] |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **session_start**

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **game_start**

When the player starts a new game (at present, this happens automatically at launch, but in the future the player may launch a new game from a menu).

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **level_menu_displayed**

When the system displays a list of the game's levels.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| unlocked_levels | List[Dict] | A list of all currently-unlocked levels, each indicating the level number, max moves allowed, and the player's best score, or null if unplayed. |**level_id** : int, **level_max_moves** : int, **best_score** : int | null |
| locked_levels | List[Dict] | A list of all currently-locked levels, each indicating the level number and max moves allowed. |**level_id** : int, **level_max_moves** : int |  

### **level_tier_unlocked**

When the player completes a tier of levels, and the system shows the next tier being unlocked.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| unlocked_levels | List[Dict] | A list of the newly-unlocked levels, each indicating the level number and max moves allowed. |**level_id** : int, **level_max_moves** : int |  

### **click_select_level**

When the player selects a level from the menu.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the level. | |
| level_max_moves | int | The max number of moves allowed in the level. | |
| best_score | int | null | The player's best score on the level, or null if they have not previously played the level. | |  

### **click_reset**

When the player clicks the button to reset the current puzzle.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_confirm_reset**

When the player clicks the button to confirm they want to reset the current puzzle.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_cancel_reset**

When the player clicks the button to cancel resetting the current puzzle.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **select_shape**

When the player selects a level from the menu.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| shape_flags | List[ShapeFlag] | The list of 'flags' indicating any special attributes of the shape. | |
| shape_index | int | The index of the shape within the overall list of shapes, used for cross-referencing | |
| position | Dict[str,int] | The board coordinates of the upper-left corner of the selected shape's bounding box, in global coordinates. | |
| block_map | List[List[int]] | A 2D 'map' of the shape, which uses 0 (empty) and 1 (filled) to indicate the shape within a bounding box of board tiles. The map is presented as the shape appears on the board, i.e. a rotated shape will have a rotated map | |
| block_details | List[Dict[str, Any]] | A list of details for each block in the shape. Includes the block offset (in global coordinates) from the shape's position, which can be used to check which point the given block occupies in the block_map. Other details include any flags specific to the given block (such as whether the given block is the pivot for a rotating shape), and indication of whether each edge of the block is 'open' (carries charge) or 'closed', and specific attributes for rotation and sequenced blocks. |**block_offset** : Dict[str, int], **block_type** : ShapeFlag, **edges** : Dict[CardinalDirection, EdgeType], **charged** : bool, **rotation_direction** : RotationType, **sequence_goal** : int, **sequence_goal_met** : bool |  

### **place_shape**

When the player moves the selected block to a new position.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| shape_flags | List[ShapeFlag] | The list of 'flags' indicating any special attributes of the shape. | |
| shape_index | int | The index of the shape within the overall list of shapes, used for cross-referencing | |
| position | Dict[str,int] | The board coordinates of the upper-left corner of the selected shape's bounding box, in global coordinates. | |
| block_map | List[List[int]] | A 2D 'map' of the shape, which uses 0 (empty) and 1 (filled) to indicate the shape within a bounding box of board tiles. The map is presented as the shape appears on the board, i.e. a rotated shape will have a rotated map | |
| block_details | List[Dict[str, Any]] | A list of details for each block in the shape. Includes the block offset (in global coordinates) from the shape's position, which can be used to check which point the given block occupies in the block_map. Other details include any flags specific to the given block (such as whether the given block is the pivot for a rotating shape), and indication of whether each edge of the block is 'open' (carries charge) or 'closed', and specific attributes for rotation and sequenced blocks. |**block_offset** : Dict[str, int], **block_type** : ShapeFlag, **edges** : Dict[CardinalDirection, EdgeType], **charged** : bool, **rotation_direction** : RotationType, **sequence_goal** : int, **sequence_goal_met** : int |
| new_move_count | bool | The total moves the player has made on the current puzzle, after placing the block. | |  

### **rotate_shape**

When the player clicks to rotate a block to a new orientation.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| shape_flags | List[ShapeFlag] | The list of 'flags' indicating any special attributes of the shape. | |
| shape_index | int | The index of the shape within the overall list of shapes, used for cross-referencing | |
| position | Dict[str,int] | The board coordinates of the upper-left corner of the selected shape's bounding box, in global coordinates. | |
| block_map | List[List[int]] | A 2D 'map' of the shape, which uses 0 (empty) and 1 (filled) to indicate the shape within a bounding box of board tiles. The map is presented as the shape appears on the board, i.e. a rotated shape will have a rotated map | |
| block_details | List[Dict[str, Any]] | A list of details for each block in the shape. Includes the block offset (in global coordinates) from the shape's position, which can be used to check which point the given block occupies in the block_map. Other details include any flags specific to the given block (such as whether the given block is the pivot for a rotating shape), and indication of whether each edge of the block is 'open' (carries charge) or 'closed', and specific attributes for rotation and sequenced blocks. |**block_offset** : Dict[str, int], **block_type** : ShapeFlag, **edges** : Dict[CardinalDirection, EdgeType], **charged** : bool, **rotation_direction** : RotationType, **sequence_goal** : int, **sequence_goal_met** : int |
| new_move_count | bool | The total moves the player has made on the current puzzle, after placing the block. | |  

### **shape_destinations_highlighted**

When the system displays higlighting on the puzzle board for where the currently-selected block may be placed.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| highlighted_spaces | List[List] | A list of board coordinates, each indicating a highlighted space on the puzzle board. | |  

### **puzzle_solved**

When the puzzle enters the 'solved' state after the player has moved all pieces to complete the circuit.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **puzzle_solution_lost**

When the player makes a move after previously solving the puzzle, taking the puzzle out of the 'solved' state.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_complete_level**

When the player clicks the button to complete the level, when the puzzle is in the 'solved' state.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_quit_level**

When the player clicks the button to quit the current level.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_request_hint**

When the player clicks on the 'hint' button to display the correct final position of a block.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **block_hint_appeared**

When the game displays the correct final position of a block, as a hint to the player.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **block_hint_disappeared**

When the hinted block position disappears.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_display_help**

When the player clicks the button to display instructions on how to move blocks

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_close_help**

When the player clicks the button to close the instructions on how to move blocks

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **start_survey**

When the player enters into a survey after a level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |  

### **survey_item_displayed**

When the system displays a multi-choice (i.e. select one) survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| prompt | str | The text content of the item prompt. | |
| choices | List[str] | The list of possible choices for the survey item. | |  

### **select_survey_response**

When the player clicks on a choice in a multi-choice survey item, selecting the choice.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| choice_value | int | The index of the selected choice among the available choices, or the value (if the multi-choice item uses a Likert scale or similar). | |
| choice_string | str | The text content of the selected choice. | |  

### **submit_survey_response**

When the player clicks to submit their choice on a multi-choice survey item.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| survey_id | str | An identifier for the specific survey. | |
| item_id | str | An identifier for the specific survey item. | |
| choice_value | int | The index of the submitted choice among the available choices, or the value (if the multi-choice item uses a Likert scale or similar). | |
| choice_string | str | The text content of the submitted choice. | |  

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

