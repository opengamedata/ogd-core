# Game: WAVES

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

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **COMPLETE.0**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(COMPLETE) | N/A | |
| amplitude_left | float | N/A | |
| wavelength_left | float | N/A | |
| offset_left | float | N/A | |
| amplitude_right | float | N/A | |
| wavelength_right | float | N/A | |
| offset_right | float | N/A | |
| closeness | float | N/A | |  

### **SUCCEED.0**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(SUCCEED) | N/A | |
| amplitude_left | float | N/A | |
| wavelength_left | float | N/A | |
| offset_left | float | N/A | |
| amplitude_right | float | N/A | |
| wavelength_right | float | N/A | |
| offset_right | float | N/A | |
| closeness | float | N/A | |  

### **FAIL.0**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(FAIL) | N/A | |
| amplitude_left | float | N/A | |
| wavelength_left | float | N/A | |
| offset_left | float | N/A | |
| amplitude_right | float | N/A | |
| wavelength_right | float | N/A | |
| offset_right | float | N/A | |
| closeness | float | N/A | |  

### **CUSTOM.1**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(SLIDER_MOVE_RELEASE) | N/A | |
| slider | Unknown | Unknown | |
| wave | string | N/A | |
| begin_val | float | N/A | |
| end_val | float | N/A | |
| min_val | float | N/A | |
| max_val | float | N/A | |
| ave_val | float | N/A | |
| begin_closeness | float | N/A | |
| end_closeness | float | N/A | |
| drag_length_ticks | int | N/A | |
| direction_shifts | int | N/A | |
| stdev_val | float | N/A | |
| correct_val | float | N/A | |  

### **CUSTOM.2**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(ARROW_MOVE_RELEASE) | N/A | |
| slider | Unknown | Unknown | |
| wave | string | N/A | |
| begin_val | float | N/A | |
| end_val | float | N/A | |
| closeness | float | N/A | |
| correct_val | float | N/A | |  

### **CUSTOM.3**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(QUESTION_ANSWER) | N/A | |
| answer | int | N/A | |
| answered | int | N/A | |
| question | int | N/A | |  

### **CUSTOM.4**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(RESET_BTN_PRESS) | N/A | |
| amplitude_left | float | N/A | |
| wavelength_left | float | N/A | |
| offset_left | float | N/A | |
| amplitude_right | float | N/A | |
| wavelength_right | float | N/A | |
| offset_right | float | N/A | |
| closeness | float | N/A | |  

### **CUSTOM.5**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(MENU_BUTTON) | N/A | |  

### **CUSTOM.6**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(SKIP_BUTTON) | N/A | |  

### **CUSTOM.7**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(DISMISS_MENU_BUTTON) | N/A | |  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**SessionID** : *str*, *Aggregate feature*   
The player's session ID number for this play session  
  

**PersistentSessionID** : *str*, *Aggregate feature*   
The session ID for the player's device, persists across multiple players using the same device.  
  

**AverageFails** : *float*, *Aggregate feature*   
totalFails averaged over all levels  
  

**AverageLevelTime** : *float*, *Aggregate feature*   
totalLevelTime averaged over all levels  
  

**AverageMoveTypeChanges** : *float*, *Aggregate feature*   
totalMoveTypeChanges averaged over all levels  
  

**AverageSliderMoves** : *float*, *Aggregate feature*   
totalSliderMoves averaged over all levels  
  

**OverallPercentAmplitudeMoves** : *float*, *Aggregate feature*   
Percent of total moves that were amplitude adjustments over a whole session  
  

**OverallPercentOffsetMoves** : *float*, *Aggregate feature*   
Percent of total moves that were offset adjustments over a whole session  
  

**OverallPercentWavelengthMoves** : *float*, *Aggregate feature*   
Percent of total moves that were wavelength adjustments over a whole session  
  

**OverallSliderAverageRange** : *float*, *Aggregate feature*   
Average range of slider moves over a whole session  
  

**OverallSliderAverageStandardDeviations** : *float*, *Aggregate feature*   
Average standard deviation of slider moves over a whole sessioin  
  

**SessionSucceedCount** : *int*, *Aggregate feature*   
number of times a 'SUCCEED' event occurs, across the whole session. [count of 'SUCCEED' events]  
*Other elements*:  

target : SUCCEED.0  

**BeginCount** : *int*, *Per-count feature*   
number of times a player 'began' the level. [count of 'BEGIN' events]  
  

**Completed** : *bool*, *Per-count feature*   
whether the level was completed or not [bool whether 'COMPLETE' event was found]  
*Sub-features*:  

- **Count** : *int*, number of times a player 'completed' the level. [count of 'COMPLETE' events]  
  

**MenuButtonCount** : *int*, *Per-count feature*  (disabled)  
number of times the player returned to the main menu. [count of 'MENU_BUTTON' events]  
  

**SucceedCount** : *int*, *Per-count feature*   
number of times a 'SUCCEED' event occurs. [count of 'SUCCEED' events]  
  

**TotalFails** : *int*, *Per-count feature*   
number of 'Fail' events across a level  
  

**TotalLevelTime** : *timedelta*, *Per-count feature*   
time spent on a level [sum of differences in time between 'BEGIN' and 'COMPLETE' event(s)]  
  

**TotalResets** : *int*, *Per-count feature*   
number of times the user pressed the 'reset' button across a level  
  

**TotalSkips** : *int*, *Per-count feature*   
number of times the player chose to skip the level (only allowed if they already completed the level once)  
  

**FirstMoveType** : *char*, *Per-count feature*   
A character indicating what type of slider move a player made first. A = Amplitude, W = Wavelength, O = Offset, null = No moves  
  

**AmplitudeGoodMoveCount** : *int*, *Per-count feature*   
number of amplitude moves that brought amplitude closer to the correct value  
  

**OffsetGoodMoveCount** : *int*, *Per-count feature*   
number of offset moves that brought offset closer to the correct value  
  

**WavelengthGoodMoveCount** : *int*, *Per-count feature*   
number of wavelength moves that brought wavelength closer to the correct value  
  

**PercentAmplitudeMoves** : *float*, *Per-count feature*   
percent of total moves that were amplitude adjustments in a level  
  

**PercentOffsetMoves** : *float*, *Per-count feature*   
percent of total moves that were offset adjustments in a level  
  

**PercentWavelengthMoves** : *float*, *Per-count feature*   
percent of total moves that were wavelength adjustments in a level  
  

**PercentAmplitudeGoodMoves** : *float*, *Per-count feature*   
percent of amplitude moves that brought amplitude closer to the correct value  
  

**PercentOffsetGoodMoves** : *float*, *Per-count feature*   
percent of wavelength moves that brought wavelength closer to the correct value  
  

**PercentWavelengthGoodMoves** : *float*, *Per-count feature*   
percent of wavelength moves that brought wavelength closer to the correct value  
  

**SliderAverageRange** : *float*, *Per-count feature*   
difference between max and min values of a slider move, averaged together across a level  
  

**SliderAverageStandardDeviations** : *float*, *Per-count feature*   
Average of stdev_val for all slider moves in a level  
  

**TotalArrowMoves** : *int*, *Per-count feature*   
arrow moves across a given level [count of 'ARROW_MOVE_RELEASE' events]  
  

**TotalMoveTypeChanges** : *int*, *Per-count feature*   
number of times the player changes between 'Arrow' and 'Slider' move types across a level  
  

**TotalSliderMoves** : *int*, *Per-count feature*   
slider moves across a given level [count of 'SLIDER_MOVE_RELEASE' events]  
  

**QuestionAnswered** : *int*, *Per-count feature*   
The answer the user gave to a given question (or -1 if unanswered)  
  

**QuestionCorrect** : *int*, *Per-count feature*   
0 if user answered the question incorrectly, 1 if answered correctly, -1 if unanswered  
  

**TimeToAnswerMS** : *int*, *Per-count feature*  (disabled)  
The time, in milliseconds, taken by the player before answering the question  
  

**SequenceLevel** : *str*, *Per-count feature*   
Sequence of slider interactions (e.g. 'wow' for Wavelength, Offset, Wavelength)  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.  

level_range : range(0, 34)

No changelog prepared

