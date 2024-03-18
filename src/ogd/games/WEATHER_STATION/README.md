# Game: WEATHER_STATION

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

### **session_start**

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **game_start**

When the player starts a new game (at present, this happens automatically at launch, but in the future the player will launch a new game from a menu).

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **viewport_data**

An event sent approximately once per second, containing the in-game position and orientation of the player headset for each frame in the past second

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| gaze_data_package | List[Dict] | A list of dicts, where each dict is one frame of headset data, containing a position and rotation vector, e.g. {"pos":[1,2,3], "rot":[4,5,6,7]}. |**pos** : List[float], **rot** : List[float] |

#### Other Elements

- None  

### **left_hand_data**

An event sent approximately once per second, containing the in-game position and orientation of the player's left hand for each frame in the past second

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| left_hand_data_package | List[Dict] | A list of dicts, where each dict is one frame of left-hand data, containing a position and rotation vector, e.g. {"pos":[1,2,3], "rot":[4,5,6,7]}. |**pos** : List[float], **rot** : List[float] |

#### Other Elements

- None  

### **right_hand_data**

An event sent approximately once per second, containing the in-game position and orientation of the player's right hand for each frame in the past second

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| right_hand_data_package | List[Dict] | A list of dicts, where each dict is one frame of right-hand data, containing a position and rotation vector, e.g. {"pos":[1,2,3], "rot":[4,5,6,7]}. |**pos** : List[float], **rot** : List[float] |

#### Other Elements

- None  

### **headset_on**

When the player puts the headset on, resuming the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **headset_off**

When the player removes the headset from their head, pausing the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **grab_gesture**

When the player presses the trigger to perform a grab, whether the 'grab' did anything or not.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| pos | Dict[str, float] | The position of the hand when the 'grab' was triggered |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| rot | Dict[str, float] | The orientation of the hand when the 'grab' was triggered |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(Hand) | Indicator of whether the player grabbed with their right or left hand. | |

#### Other Elements

- None  

### **release_gesture**

When the player releases the trigger button to end a 'grab'

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| pos | Dict[str, float] | The position of the hand when the 'grab' was released |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| rot | Dict[str, float] | The orientation of the hand when the 'grab' was released |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(Hand) | Indicator of whether the player grabbed with their right or left hand. | |

#### Other Elements

- None  

### **dialog_audio_start**

When a voiceover audio clip begins

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| dialog_id | str | The identifier of the dialog audio, which can be cross-referenced against DBExport. | |
| dialog_type | enum(DialogType) | Indicator for whether the dialog was exposition, a hint, or a fun fact. | |
| speaker | enum(Speaker) | Which character speaks the dialog | |

#### Other Elements

- None  

### **dialog_audio_end**

When a voiceover audio clip ends

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| dialog_id | str | The identifier of the dialog audio, which can be cross-referenced against DBExport. | |
| dialog_type | enum(DialogType) | Indicator for whether the dialog was exposition, a hint, or a fun fact. | |
| speaker | enum(Speaker) | Which character spoke the dialog | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

None

No changelog prepared

