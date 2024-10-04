# Game: MAGNET

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

### **COMPLETE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| guessScore | Dict | N/A |**northDist** : float, **southDist** : float |
| guessScoreIfSwitched | Dict | N/A |**northPoleToSouthGuess** : float, **southPoleToNorthGuess** : float |
| numCompasses | int | N/A | |
| ironFilingsUsed | boolean | N/A | |
| magneticFilmUsed | boolean | N/A | |
| levelTime | float | N/A | |
| numLevels | int | N/A | |
| numTimesPolesMoved | int | N/A | |
| magnetLocation | Dict | N/A |**xNorth** : float, **yNorth** : float, **xSouth** : float, **ySouth** : float |
| event_custom | COMPLETE | N/A | |  

### **DRAG_TOOL**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | DRAG_TOOL | N/A | |
| toolType | string | N/A | |
| dragTime | float | N/A | |
| location | Dict | N/A |**x** : int, **y** : int |
| toolNum | float | N/A | |  

### **DRAG_POLE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | DRAG_POLE | N/A | |
| poleType | string | N/A | |
| dragTime | float | N/A | |
| location | Dict | N/A |**x** : int, **y** : int |
| numTimesMoved | int | N/A | |
| distToPole | float | N/A | |
| numToolsUsed | int | N/A | |  

### **PLAYGROUND_EXIT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | PLAYGROUND_EXIT | N/A | |
| timeSpent | float | N/A | |
| numThingsDragged | int | N/A | |  

### **TUTORIAL_EXIT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | TUTORIAL_EXIT | N/A | |
| timeSpent | float | N/A | |  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**sessionID** : **, *Aggregate feature*  (disabled)  
The player's session ID number for this play session  
  

**persistentSessionID** : **, *Aggregate feature*  (disabled)  
The session ID for the player's device, persists across multiple players using the same device.  
  

**sessionEventCount** : **, *Aggregate feature*  (disabled)  
The total number of events across the entire session  
  

**sessionTime** : **, *Aggregate feature*  (disabled)  
The total number of seconds spent  
  

**numberOfCompletePlays** : **, *Aggregate feature*  (disabled)  
The number of times the player played the game  
  

**averageScore** : **, *Aggregate feature*  (disabled)  
The average score across all complete plays  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.  

level_range : range(0, 219)

No changelog prepared

