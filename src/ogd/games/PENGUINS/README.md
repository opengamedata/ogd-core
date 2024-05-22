# Game: PENGUINS

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

When the app is started and the gameplay session is assigned a session ID. The player has not necessarily begun the game itself yet.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| random_seed | Unknown | The random seed used for all random number/position/rotation generation in the game. | |

#### Other Elements

- None  

### **game_start**

When a new game is started

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mode | enum(HOME_MODE, ...) | The game mode that the player launched | |

#### Other Elements

- None  

### **open_menu**

When the player opens the game menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **close_menu**

When the player closes the game menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **select_menu_item**

When the player clicks and item in the menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| item | str | The name of the menu item the player selected | |

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

### **player_waddle**

When a player performs a waddle movement to move their penguin avatar forward

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of... some object | |
| old_posX | float | The previous X-position, where the waddle started. | |
| old_posY | float | The previous Y-position, where the waddle started. | |
| old_posZ | float | The previous Z-position, where the waddle started. | |
| posX | float | The new X-position, where the waddle ended. | |
| posY | float | The new Y-position, where the waddle ended. | |
| posZ | float | The new Z-position, where the waddle ended. | |
| rotX | float | The X-component of the rotation when the waddle ended. | |
| rotY | float | The Y-component of the rotation when the waddle ended. | |
| rotZ | float | The Z-component of the rotation when the waddle ended. | |
| rotW | float | The W-component of the rotation when the waddle ended. | |
| source | enum(BUTTON, WADDLE) | Indicator for whether the player waddled by pressing a button, or by making the 'waddle' gesture with their head. | |

#### Other Elements

- None  

### **gaze_object_begin**

An event triggered when the player has gazed at an object for at least 0.25 seconds, where 'gazed at' means the object is the nearest on a raycast from the viewport center

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the object the player is gazing at | |

#### Other Elements

- None  

### **gaze_object_end**

An event triggered when the player turns away from an object they'd gazed at, so the object is no longer nearest on a raycast from the viewport center. Note there may be a small buffer around the object for the raycast.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the object the player had previously gazed at | |

#### Other Elements

- None  

### **bubble_pop**

An event triggered when the player pops a bubble in the bubble-popping mini-game. A bubble should be popped on a 'beat' of the music, but can be popped up to 0.5 seconds before or after the 'beat.'

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the bubble object the player popped | |
| timing_error | float | The timing difference between the pop event and the music 'beat.' This value is in the range [-0.5, 0.5], where a negative indicates the bubble was popped before the 'beat,' and positive indicates popping after the 'beat.' | |

#### Other Elements

- None  

### **eat_fish**

An event triggered when the player eats a fish.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the fish object the player ate | |

#### Other Elements

- None  

### **flipper_bash_skua**

An event triggered when the player makes a flipper-bashing move to shoo a skua away from their nest/egg.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the skua object the player bashed | |

#### Other Elements

- None  

### **pickup_rock**

An event triggered when the player picks up a rock lying on the ground, which contributes to the building of their nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| total_picked_up | int | The running total of rocks the player has picked up. | |
| px | float | The x-position of the player when the event happened | |
| py | float | The y-position of the player when the event happened | |
| pz | float | The z-position of the player when the event happened | |
| qx | float | The x-component of the quaternion for the player's orientation when the event happened | |
| qy | float | The y-component of the quaternion for the player's orientation when the event happened | |
| qz | float | The z-component of the quaternion for the player's orientation when the event happened | |
| qw | float | The w-component of the quaternion for the player's orientation when the event happened | |

#### Other Elements

- None  

### **push_snowball**

An event triggered when the player pushes a snowball down the hill.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the snowball object the player pushed | |
| px | float | The x-position of the player when the event happened | |
| py | float | The y-position of the player when the event happened | |
| pz | float | The z-position of the player when the event happened | |
| qx | float | The x-component of the quaternion for the player's orientation when the event happened | |
| qy | float | The y-component of the quaternion for the player's orientation when the event happened | |
| qz | float | The z-component of the quaternion for the player's orientation when the event happened | |
| qw | float | The w-component of the quaternion for the player's orientation when the event happened | |

#### Other Elements

- None  

### **ring_chime**

An event when the player rings one of the chimes in the chime mini-game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| note_played | str | The name of the chime the player rang | |

#### Other Elements

- None  

### **bubble_appeared**

Event when a new bubble appears in the mating dance minigame.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the bubble object that appeared | |
| posX | float | The x-position of the bubble that appeared | |
| posY | float | The y-position of the bubble that appeared | |
| posZ | float | The z-position of the bubble that appeared | |

#### Other Elements

- None  

### **bubble_expired**

Event when a bubble's pop-able time ends and the bubble disappears.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the bubble object that disappeared | |

#### Other Elements

- None  

### **egg_hatch_indicator_updated**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_remaining | int | The time left until the egg will hatch | |

#### Other Elements

- None  

### **egg_hatched**

Event when the egg hatches

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **egg_lost**

Event when the player's egg is stolen by a skua.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the skua that stole the egg | |

#### Other Elements

- None  

### **egg_recovered**

Event when the player recovers the egg from the skuas.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **mating_dance_indicator_updated**

Event when a bubble is popped and the indicator for progress to completion of the mating dance updates.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| percent_full | int | The new percent to which the dance completion indicator is filled | |

#### Other Elements

- None  

### **nest_complete**

Event when the player completes the building of their nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **penguin_pin_fell**

When one of the pins fell in the bowling area.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **skua_spawn**

Event when a new skua is added in the nest/egg defense mini-game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the skua object that appeared | |
| posX | float | The x-position of the skua that appeared | |
| posY | float | The y-position of the skua that appeared | |
| posZ | float | The z-position of the skua that appeared | |

#### Other Elements

- None  

### **skua_move**

Event when a skua moves to a new location in the nest/egg defense mini-game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the skua object that moved | |
| from_position_x | float | The initial x-position of the skua that moved | |
| from_position_y | float | The initial y-position of the skua that moved | |
| from_position_z | float | The initial z-position of the skua that moved | |
| to_position_x | float | The new x-position of the skua that moved | |
| to_position_y | float | The new y-position of the skua that moved | |
| to_position_z | float | The new z-position of the skua that moved | |

#### Other Elements

- None  

### **enter_region**

Event when the player moves into one of the regions containing a mini-game or other feature.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| region_name | str | The name of the region the player entered | |

#### Other Elements

- None  

### **exit_region**

Event when a moves out of one of the regions containing a mini-game or other feature.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| region_name | str | The name of the region the player left | |

#### Other Elements

- None  

### **activity_begin**

Event when the player begins to engage with a mini-game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| activity_name | enum(skuas, mating_dance, ...) | The name of the mini-game/activity with which the player began to engage | |

#### Other Elements

- None  

### **activity_end**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| activity_name | enum(skuas, mating_dance, ...) | NOT YET DOCUMENTED | |

#### Other Elements

- None  

### **global_timer_begin**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_remaining | int | The left on the global timer | |

#### Other Elements

- None  

### **global_timer_pause**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| data | Unknown | NOT YET DOCUMENTED | |

#### Other Elements

- None  

### **global_timer_expired**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| data | Unknown | NOT YET DOCUMENTED | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

**RegionEnter** : *Detector*   
Triggers an event when a player enter a region  
  

**RegionExit** : *Detector*   
Triggers an event when a player exit a region  
  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**GazeCount** : *int*, *Aggregate feature*   
The number of times a player waddled in a given region of the game.  
  

**PickupRockCount** : *int*, *Aggregate feature*   
The duration each session took.  
  

**PlayerWaddleCount** : *int*, *Aggregate feature*   
The number of times a player waddled.  
  

**SessionDuration** : *timedelta*, *Aggregate feature*   
The duration each session took.  
  

**GazeDuration** : *timedelta*, *Aggregate feature*   
How long gaze event last for.  
  

**RegionEnterCount** : *int*, *Aggregate feature*  (disabled)  
The number of times a player enterd for a given region of the game.  
  

**ActivityCompleted** : *int*, *Aggregate feature*   
The activities completed in a given session.  
  

**ActivityDuration** : *int*, *Aggregate feature*   
How long activity last for.  
  

**RegionsEncountered** : *int*, *Aggregate feature*   
The regions entered in a given session.  
  

**RegionDuration** : *timedelta*, *Per-count feature*   
The duration of time a player played in a given region of the game.  
  

**WaddlePerRegion** : *int*, *Per-count feature*   
The number of times a player waddled in a given region of the game.  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

game_state : {'seconds_from_launch': {'type': 'float', 'description': 'The number of seconds of game time elapsed since the game was launched, *not including time when the game was paused*.'}, 'pos': {'type': 'List[float]', 'description': 'The current position of the player headset at the moment the event occurred, formatted as [x, y, z]'}, 'rot': {'type': 'List[float]', 'description': 'The current orientation of the player headset at the moment the event occurred, formatted as [x, y, z, w]'}, 'has_rock': {'type': 'bool', 'description': 'Whether the player was holding a rock in their beak at the time the event occurred.'}}  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.  

level_range : range(1, 6)

No changelog prepared

