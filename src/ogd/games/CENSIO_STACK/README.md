# Game: CENSIO_STACK

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
| LevelType | ['DEFAULT', 'CLUTTER', 'BOMBS', 'FULL_SET', 'FULL_ORDERED_SET', 'SHIFTING'] |
| LevelDifficulty | ['NORMAL', 'HARD', 'BONUS'] |
| PieceShape | ['HEAD', 'ARM', 'BODY', 'LEG', 'BOMB'] |
| ReceiptItem | ['GOOD', 'DAMAGED', 'JUNK', 'MISSED', 'FULL_SET', 'DUPLICATE', 'LEG_POS', 'TORSO_POS', 'HEAD_POS'] |
| PunchType | ['CLICK', 'SPACEBAR'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched. | |
| level | int | The current level the player is in (1-6, or 0 when not in a level). | |
| level_info | Dict | A dict, containing elements to indicate the type of level the player is on, and whether they are playing in 'hard' mode or not. Note, currently, there's just one level of each type, but this may change in the future. |**type** : LevelType, **difficulty** : LevelDifficulty |
| level_time | int | The number of seconds elapsed since the start of the level. | |
| level_max_time | int | The number of seconds the player has to complete the level, i.e. the starting value of the level's countdown timer. | |
| score | int | The player's score on the current level. | |
| box_count | int | The number of boxes the player has filled on the current level, which count towards the current score. During the level, this is the number of filled boxes; when the level ends a partially-filled box will also count as it is automatically 'packaged' before the final score is given. | |
| piece_count | int | The total number of pieces the player has pushed into boxes on the current level. | |
| target_pieces | List[PieceType] | A list of the types of pieces accepted on the given level's target board. For 'ordered set' levels, the order in the list indicates the order pieces must be placed. | |
| box_contents | List[Dict] | A list whose elements are dictionaries describing individual pieces placed in the current box. Each dict indicates the type of the piece, whether the piece was damaged, and whether it matched the level target. |**type** : PieceType, **is_damaged** : bool, **is_target** : bool |  

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

### **game_complete**

When the player completes the last level of the game, thus completing the game itself.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **level_preview_displayed**

When the system displays a preview of the upcoming level to the player, including the target score and allowed time.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the previewed level. | |
| level_type | LevelType | The type of the previewed level. | |
| duration | int | The allotted time for the level. | |
| goal_score | int | The target score on the level. | |  

### **click_level_play**

When the player clicks the 'play' button from the preview to start the level.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the level. | |
| level_type | LevelType | The type of the level. | |
| duration | int | The allotted time for the level. | |
| goal_score | int | The target score on the level. | |  

### **level_begin**

When a level actually begins, whether due to the player clicking 'play' from a new level preview, or clicking 'replay' in a level summary.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the level. | |
| level_type | LevelType | The type of the level. | |
| duration | int | The allotted time for the level. | |
| goal_score | int | The target score on the level. | |  

### **piece_appeared**

When a new piece appears on the conveyer belt.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| type | PieceShape | The type of piece that appeared on the belt. | |  

### **piece_disappeared**

When a non-packed piece disappears off the conveyer belt.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| type | PieceShape | The type of piece that left the belt. | |  

### **punch_launched**

When the player clicks (or presses key) to punch a piece into the box.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| type | PunchType | Whether the player triggered the punch with a click or the spacebar. | |  

### **piece_hit**

When a piece is hit by a punch, packing it into the box.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| piece | Dict | A dict describing the piece that was hit. Indicates the type of the piece, whether the piece was damaged, and whether it matched the level target. |**type** : PieceShape, **is_damaged** : bool, **is_target** : bool |
| new_box_contents | List[Dict] | A list whose elements are dictionaries describing individual pieces placed in the current box, including the newly-packed piece. Each dict indicates the type of the piece, whether the piece was damaged, and whether it matched the level target. |**type** : PieceShape, **is_damaged** : bool, **is_target** : bool |
| accuracy | float | A value, from 0-1, indicating how close the player was to a 'perfectly accurate' punch. | |  

### **bomb_hit**

When a bomb is hit by a punch, destroying the current contents of the box.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| pieces_destroyed | List[Dict] | A list whose elements are dictionaries describing individual pieces that were in the current box, and destroyed by the bomb. Each dict indicates the type of the piece, whether the piece was damaged, and whether it matched the level target. |**type** : PieceShape, **is_damaged** : bool, **is_target** : bool |
| accuracy | float | A value, from 0-1, indicating how close the player was to a 'perfectly accurate' punch. | |  

### **box_completed**

When a third piece is packed in a box, completing the box

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| pieces | List[Dict] | A list whose elements are dictionaries describing individual pieces that were in the completed box. Each dict indicates the type of the piece, whether the piece was damaged, and whether it matched the level target. |**type** : PieceShape, **is_damaged** : bool, **is_target** : bool |
| score | int | The points earned for packing the box. | |
| is_perfect | bool | Indicator for whether the box score is the maximum possible for the current level. | |  

### **target_pieces_changed**

When a player packs a box in a 'SHIFTING' level, and the target for the next box is randomly changed.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| new_target_pieces | List[PieceShape] | A list of the types of pieces accepted for the new target. If the game ever has 'shifting ordered set' levels, the order in the list indicates the order pieces must be placed. | |  

### **level_end**

When the level's timer runs out, ending the level.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| receipts | List[Dict] | A list whose elements are dictionaries describing individual boxes that were completed in the level. Each dict contains a point value of the box, an indicator of whether the box was 'perfect', and a sub-list of receipt items; which each contain a ReceiptItem type and a point value. |**items** : List[Dict[ {'type':ReceiptItem, 'value':int} ]], **total_value** : int, **is_perfect** : bool |  

### **level_summary_displayed**

When the system displays a summary of the level results to the player.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the summarized level. | |
| level_type | LevelType | The type of the summarized level. | |
| duration | int | The allotted time for the level. | |
| goal_score | int | The target score on the level. | |
| final_score | int | The actual score the player earned on the level. | |  

### **click_replay_level**

When the player clicks the 'replay' button in the level summary screen

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| level_id | int | The level number for the replayed level. | |
| level_type | LevelType | The type of the replayed level. | |
| duration | int | The allotted time for the level. | |
| goal_score | int | The target score on the level. | |
| final_score | int | The actual score the player earned on the level. | |  

### **click_breakdown**

When the player clicks to view the 'breakdown' page for the level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **breakdown_page_displayed**

When the system displays a 'page' of the level breakdown.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| page_index | int | The index of the 'page' of the level breakdown, among the breakdown pages. | |
| receipts | List[Dict] | A list whose elements are dictionaries describing individual boxes in the breakdown page. Each dict contains a point value of the box, an indicator of whether the box was 'perfect', and a sub-list of receipt items; which each contain a ReceiptItem type and a point value. |**items** : List[Dict[ {'type':ReceiptItem, 'value':int} ]], **total_value** : int, **is_perfect** : bool |  

### **click_next_breakdown_page**

When the player clicks to advance to the next 'breakdown' page for the level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| old_page_index | int | The index of the 'page' of the player was on when they clicked the 'next' button. | |  

### **click_prev_breakdown_page**

When the player clicks to go to the previous 'breakdown' page for the level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| old_page_index | int | The index of the 'page' of the player was on when they clicked the 'previous' button. | |  

### **click_next_level**

When the player clicks to advance to the next level from the 'summary' page.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_play_harder**

Placeholder for an event when the player clicks to play a level on 'hard' mode.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_play_easier**

Placeholder for an event when the player clicks to play a level on 'normal' mode.

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

