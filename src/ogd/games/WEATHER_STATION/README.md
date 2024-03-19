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

### **level_complete**

When the player finishes a level and is transitioned to the next.

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

### **object_highlighted**

When an object is highlighted, indicating the player should move the object, or place another object on it.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| highlight_object | enum(HighlightObject) | enum(HighlightDestination) | The object that was highlighted. | |
| highlight_type | enum(HighlightType) | Indicator of whether the object was a normal object, or an object destination. | |

#### Other Elements

- None  

### **object_unhighlighted**

When the highlighting on an object is cleared

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| highlight_object | enum(HighlightObject) | enum(HighlightDestination) | The object that was highlighted. | |
| highlight_type | enum(HighlightType) | Indicator of whether the object was a normal object, or an object destination. | |

#### Other Elements

- None  

### **click_argo_help**

When the player presses the help button on Argo

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **click_argo_funfact**

When the player presses the 'fun fact' button on Argo

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **grab_station_handle**

When the player grabs the weather station adjustment handle

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_height | float | The height of the weather station handle when the player grabbed it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the handle with their right or left hand. | |

#### Other Elements

- None  

### **release_station_handle**

When the player releases the weather station handle at a new height

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_height | float | The height of the weather station handle when the player released it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the handle with their right or left hand. | |

#### Other Elements

- None  

### **grab_workbench_handle**

When the player grabs the workbench adjustment handle

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_height | float | The height of the workbench handle when the player grabbed it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the handle with their right or left hand. | |

#### Other Elements

- None  

### **release_workbench_handle**

When the player releases the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_height | float | The height of the workbench handle when the player released it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the handle with their right or left hand. | |

#### Other Elements

- None  

### **grab_puzzle_object**

When the player grabs a puzzle object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object | enum(PuzzleObject) | The object the player grabbed; either the solar panel, wind turbine, data logger, temperature sensor, battery, or Argo. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the object with their right or left hand. | |

#### Other Elements

- None  

### **release_puzzle_object**

When the player releases a puzzle object, without placing it onto a destination

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object | enum(PuzzleObject) | The object the player released; either the solar panel, wind turbine, data logger, temperature sensor, battery, or Argo. | |
| pos | Dict[str, float] | The position of the object when the player released it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| rot | Dict[str, float] | The orientation of the object when the player released it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(Hand) | Indicator of whether the player grabbed the object with their right or left hand. | |

#### Other Elements

- None  

### **place_puzzle_object**

When the player places a puzzle object on a destination

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object | enum(PuzzleObject) | The object the player placed; either the solar panel, wind turbine, data logger, temperature sensor, battery, or Argo. | |
| destination | enum(Destination) | The type of destination in which  the player placed the object, either the sled, workbench, or tower. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the object with their right or left hand. | |

#### Other Elements

- None  

### **discard_object**

When the player drops any object into the trash chute

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object | enum(PropellerShape) | enum(BatteryShape) | enum(ThermometerComponentShape) | The object the player dropped into the trash chute. | |

#### Other Elements

- None  

### **place_argo_to_sled**

When the player places Argo, specifically, on the sled, triggering a transition to a new location. This event occurs in addition to the standard `place_puzzle_object` event

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(Hand) | Indicator of whether the player placed Argo with their right or left hand. | |

#### Other Elements

- None  

### **location_transition**

When the player is transitioned to a new location

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| to | enum(Location) | The location to which the player is moved (the starting location is given in GameState). | |

#### Other Elements

- None  

### **start_puzzle**

When the player makes an initial move to start a puzzle, usually by placing the puzzle object on the workbench or interacting with the object at the weather station

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| puzzle | enum(PuzzleObject) | The puzzle the player started. | |

#### Other Elements

- None  

### **complete_puzzle**

When the player completes a puzzle

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| puzzle | enum(PuzzleObject) | The puzzle the player completed. | |

#### Other Elements

- None  

### **grab_solar_handle**

When the player grabs the handle of the solar panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_angle | float | The rotation of the solar panel when the player grabbed it. | |
| start_alignment | int | The number of green 'bars' shown on the solar panel when the player grabbed it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the solar panel with their right or left hand. | |

#### Other Elements

- None  

### **release_solar_handle**

When the player releases the handle of the solar panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_angle | float | The rotation of the solar panel when the player released it. | |
| start_alignment | int | The number of green 'bars' shown on the solar panel when the player released it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the solar panel with their right or left hand. | |

#### Other Elements

- None  

### **grab_logger_handle**

When the player grabs the handle of the data logger door

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_angle | float | The hinge angle of the door when the player grabbed it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the door with their right or left hand. | |

#### Other Elements

- None  

### **release_logger_handle**

When the player releases the handle of the data logger door

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_angle | float | The hinge angle of the door when the player released it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the door with their right or left hand. | |

#### Other Elements

- None  

### **grab_data_puck**

When the player grabs a puzzle object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| puck_shape | enum(PuckShape) | The data puck shape the player grabbed; the pucks come in a variety of shapes. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the puck with their right or left hand. | |

#### Other Elements

- None  

### **release_data_puck**

When the player releases a propeller sahpe, without placing it onto the logger board

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(PuckShape) | The data puck shape the player released; the pucks come in a variety of shapes. | |
| pos | Dict[str, float] | The position of the puck when the player released it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| rot | Dict[str, float] | The orientation of the puck when the player released it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(Hand) | Indicator of whether the player grabbed the puck with their right or left hand. | |

#### Other Elements

- None  

### **place_data_puck**

When the player places a propeller onto the turbine

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(PuckShape) | The data puck shape the player placed; the pucks come in a variety of shapes. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the puck with their right or left hand. | |

#### Other Elements

- None  

### **click_test_uplink**

When the player presses the button to test the data uplink and complete the indoor portion of the level.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| station_name | str | The name of the station on the map whose uplink the player is testing. | |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **grab_trash**

When the player grabs the door of the trash chute to open it and toss away a component

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_angle | float | The hinge angle of the trash chute door when the player grabbed it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the door with their right or left hand. | |

#### Other Elements

- None  

### **release_trash**

When the player releases the trash chute door

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_angle | float | The hinge angle of the trash chute door when the player released it. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the door with their right or left hand. | |

#### Other Elements

- None  

### **click_rotate_drawer**

When the player presses the button to shift to a different drawer of components at the workbench.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| drawer_contents | List[PropellerShape, BatteryShape] | A list of all the shapes in the new drawer we rotated to. | |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **grab_propeller**

When the player grabs a puzzle object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(PropellerShape) | The propeller shape the player grabbed; the propeller comes in a few sizes. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the object with their right or left hand. | |

#### Other Elements

- None  

### **release_propeller**

When the player releases a propeller sahpe, without placing it onto the turbine

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(PropellerShape) | The propeller the player released; the propeller comes in a few sizes. | |
| pos | Dict[str, float] | The position of the propeller when the player released it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| rot | Dict[str, float] | The orientation of the propeller when the player released it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(Hand) | Indicator of whether the player grabbed the propeller with their right or left hand. | |

#### Other Elements

- None  

### **place_propeller**

When the player places a propeller onto the turbine

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(PropellerShape) | The propeller the player placed; the propeller comes in a few sizes. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the propeller with their right or left hand. | |

#### Other Elements

- None  

### **click_test_propeller**

When the player presses the button to test the propeller they placed on the wind turbine

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| is_correct | bool | Indicator for whether the propeller the player is testing is the correct one. | |
| propeller_shape | enum(PropellerShape) | The propeller the player is testing; the propeller comes in a few sizes. | |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **battery_box_open**

TODO.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **battery_box_close**

TODO.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **grab_battery_component**

When the player grabs a component for repairing the battery

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(BatteryShape) | The battery component the player grabbed. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the battery component with their right or left hand. | |

#### Other Elements

- None  

### **release_battery_component**

When the player releases a battery component, without placing it in the battery box

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(BatteryShape) | The battery component the player released. | |
| pos | Dict[str, float] | The position of the battery component when the player released it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| rot | Dict[str, float] | The orientation of the battery component when the player released it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(Hand) | Indicator of whether the player grabbed the battery component with their right or left hand. | |

#### Other Elements

- None  

### **place_battery_component**

When the player places a battery component onto a spot in the battery box

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| propeller_shape | enum(BatteryShape) | The battery component the player placed. | |
| hand | enum(Hand) | Indicator of whether the player grabbed the battery component with their right or left hand. | |

#### Other Elements

- None  

### **click_cycle_temperature_component**

When the player presses the button to rotate one of the component shapes on the temperature sensor

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| button_position | int | The index of the component button the player clicked to rotate. | |
| old_shape | enum(ThermometerComponentShape) | The shape of the component that was selected before the rotation happened. | |
| new_shape | enum(ThermometerComponentShape) | The shape of the component that after rotating. | |
| hand | enum(Hand) | Indicator of whether the player pressed the button with their right or left hand. | |

#### Other Elements

- None  

### **lock_temperature_components**

When the player presses the button to lock the temperature sensor components

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| component_settings | List[ThermometerComponentShape] | The list of current component shapes when the player locked them. | |

#### Other Elements

- None  

### **epilogue_start**

When the epilogue level starts. This level does not have any tasks for the player, just dialog to listen to.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **epilogue_end**

When the epilogue level ends.

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

