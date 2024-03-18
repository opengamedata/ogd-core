# Game: CRYSTAL

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

### **COMPLETE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| 0 | int | N/A | |
| 1 | int | N/A | |
| 2 | int | N/A | |
| 3 | int | N/A | |
| 4 | int | N/A | |
| 5 | int | N/A | |
| 6 | int | N/A | |
| 7 | int | N/A | |
| 8 | int | N/A | |
| stability | Dict | N/A |**pack** : int, **charge** : int |

#### Other Elements

- None  

### **BEGIN**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| stars_0 | int | N/A | |
| stars_1 | int | N/A | |
| stars_2 | int | N/A | |
| stars_3 | int | N/A | |
| stars_4 | int | N/A | |
| stars_5 | int | N/A | |
| stars_6 | int | N/A | |
| stars_7 | int | N/A | |
| stars_8 | int | N/A | |

#### Other Elements

- None  

### **MOLECULE_RELEASE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | MOLECULE_RELEASE | N/A | |
| startPosition | Dict | may be more coords, not sure if upper limit exists |**coord_0** : {'x': 'int', 'y': 'int'}, **coord_1** : {'x': 'int', 'y': 'int'}, **coord_2** : {'x': 'int', 'y': 'int'} |
| endPosition | Dict | may be more coords, not sure if upper limit exists |**coord_0** : {'x': 'int', 'y': 'int'}, **coord_1** : {'x': 'int', 'y': 'int'}, **coord_2** : {'x': 'int', 'y': 'int'} |
| time | float | N/A | |
| startStability | Dict | Starting stability when the molecule was 'grabbed'. |**pack** : int, **charge** : int |
| endStability | Dict | Ending stability when the molecule was 'released'. |**pack** : int, **charge** : int |

#### Other Elements

- None  

### **MOLECULE_ROTATE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | string | N/A | |
| isStamp | bool | N/A | |
| startRotation | int | N/A | |
| endRotation | int | N/A | |
| numRotations | int | N/A | |
| startStability | Dict | Starting stability when the molecule was 'grabbed'. |**pack** : int, **charge** : int |
| endStability | Dict | Ending stability after the molecule was rotated. |**pack** : int, **charge** : int |

#### Other Elements

- None  

### **CLEAR_BTN_PRESS**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | string | N/A | |
| numTimesPressed | int | N/A | |
| numMolecules | int | N/A | |
| stability | Unknown | Unknown | |

#### Other Elements

- None  

### **QUESTION_ANSWER**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | string | N/A | |
| answer | int | N/A | |
| answered | int | N/A | |
| question | int | N/A | |

#### Other Elements

- None  

### **MUSEUM_CLOSE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | string | N/A | |
| timeOpen | float | N/A | |

#### Other Elements

- None  

### **BACK_TO_MENU**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_custom | enum(BACK_TO_MENU) | N/A | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**sessionID** : **, *Aggregate feature*  (disabled)  
The player's session ID number for this play session  
  

**persistentSessionID** : **, *Aggregate feature*  (disabled)  
The session ID for the player's device, persists across multiple players using the same device.  
  

**sessionEventCount** : *int*, *Aggregate feature*  (disabled)  
The total number of events across the entire session  
  

**sessionDurationInSecs** : **, *Aggregate feature*  (disabled)  
The total time (in seconds) spent over the entire session  
  

**sessionStampRotateCount** : *int*, *Aggregate feature*  (disabled)  
Total number of stamp rotation events over the session  
  

**sessionSingleRotateCount** : *int*, *Aggregate feature*  (disabled)  
Total number of single rotation events over the session  
  

**sessionMoleculeMoveCount** : *int*, *Aggregate feature*  (disabled)  
Total number of molecule move events over the session  
  

**sessionClearBtnPresses** : *int*, *Aggregate feature*  (disabled)  
Total number of times the clear button was pressed during the session  
  

**sessionMuseumDurationInSecs** : **, *Aggregate feature*  (disabled)  
Total amount of time spent in a museum during the session?  
  

**questionAnswered** : *int*, *Per-count feature*  (disabled)  
The answer the user gave to a given question (or -1 if unanswered)  
  

**questionCorrect** : *bool*, *Per-count feature*  (disabled)  
0 if user answered the question incorrectly, 1 if answered correctly, -1 if unanswered  


No changelog prepared

