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

The individual fields encoded in the *game_state* and *user_data* Event element for all event types, and the fields in the *event_data* Event element for each individual event type logged by the game.  

### Enums  

| **Name** | **Values** |
| ---      | ---        |
| GameMode | ['HOME_MODE', '...'] |
| MoveType | ['BUTTON', 'WADDLE'] |
| Activity | ['skuas', 'mating_dance', 'nest', '...'] |
| Hand | ['LEFT', 'RIGHT'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| has_rock | bool | Whether the player was holding a rock in their beak at the time the event occurred. | |
| pos | List[float] | The current position of the player headset at the moment the event occurred, formatted as [x, y, z] | |
| rot | List[float] | The current orientation of the player headset at the moment the event occurred, formatted as [x, y, z, w] | |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched, *not including time when the game was paused*. | |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **session_start**

When the app is started and the gameplay session is assigned a session ID. The player has not necessarily begun the game itself yet.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| random_seed | int | The random seed used for all random number/position/rotation generation in the game. | |  

### **game_start**

When a new game is started

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mode | GameMode | The game mode that the player launched | |  

### **device_identifier**

Event to record a hardware ID, for cross-referencing against survey data at gameplay events.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hardware_uuid | str | The device UUID | |  

### **open_menu**

When the player opens the game menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **close_menu**

When the player closes the game menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **select_menu_item**

When the player clicks and item in the menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| item | str | The name of the menu item the player selected | |  

### **headset_on**

When the player puts the headset on, resuming the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **headset_off**

When the player removes the headset from their head, pausing the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **viewport_data**

An event sent approximately once per second, containing the in-game position and orientation of the player headset for each frame in the past second

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| gaze_data_package | List[Dict] | A list of dicts, where each dict is one frame of headset data, containing a position and rotation vector, e.g. {"pos":[1,2,3], "rot":[4,5,6,7]}. |**pos** : List[float], **rot** : List[float] |  

### **left_hand_data**

An event sent approximately once per second, containing the in-game position and orientation of the player's left hand for each frame in the past second

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| left_hand_data_package | List[Dict] | A list of dicts, where each dict is one frame of left-hand data, containing a position and rotation vector, e.g. {"pos":[1,2,3], "rot":[4,5,6,7]}. |**pos** : List[float], **rot** : List[float] |  

### **right_hand_data**

An event sent approximately once per second, containing the in-game position and orientation of the player's right hand for each frame in the past second

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| right_hand_data_package | List[Dict] | A list of dicts, where each dict is one frame of right-hand data, containing a position and rotation vector, e.g. {"pos":[1,2,3], "rot":[4,5,6,7]}. |**pos** : List[float], **rot** : List[float] |  

### **player_waddle**

When a player performs a waddle movement to move their penguin avatar forward

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of... some object | |
| pos_old | List[float] | The previous position of the player avatar's feet, in [x, y, z] form, i.e. where the waddle started. | |
| pos_new | List[float] | The resulting position of the player avatar's feet, in [x, y, z] form, i.e. where the waddle ended. | |
| source | MoveType | Indicator for whether the player waddled by pressing a button, or by making the 'waddle' gesture with their head. | |  

### **gaze_object_begin**

An event triggered when the player has gazed at an object for at least 0.25 seconds, where 'gazed at' means the object is the nearest on a raycast from the viewport center

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the object the player is gazing at | |  

### **gaze_object_end**

An event triggered when the player turns away from an object they'd gazed at, so the object is no longer nearest on a raycast from the viewport center. Note there may be a small buffer around the object for the raycast.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the object the player had previously gazed at | |  

### **bubble_pop**

An event triggered when the player pops a bubble in the bubble-popping mini-game. A bubble should be popped on a 'beat' of the music, but can be popped up to 0.5 seconds before or after the 'beat.'

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the bubble object the player popped | |
| timing_error | float | The timing difference between the pop event and the music 'beat.' This value is in the range [-0.5, 0.5], where a negative indicates the bubble was popped before the 'beat,' and positive indicates popping after the 'beat.' | |  

### **eat_fish**

An event triggered when the player eats a fish.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the fish object the player ate | |  

### **stand_on_nest**

An event triggered when the player stands atop a nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| nest_id | str | The name of the nest object the player stood on | |
| nest_pos | List[float] | The position of the nest the player stood on | |  

### **stand_on_rock**

An event triggered when the player stands atop a rock.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| rock_id | str | The name of the rock object the player stood on | |
| rock_pos | List[float] | The position of the rock when it got stood on | |  

### **flipper_bash_nest**

An event triggered when the player makes a flipper-bashing move and makes contact with a nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| nest_id | str | The name of the nest object the player bashed | |
| nest_pos | List[float] | The position of the nest the player bashed | |
| hand | List[float] | The position of the nest the player bashed | |  

### **flipper_bash_penguin**

An event triggered when the player makes a flipper-bashing move and makes contact with another penguin.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| penguin_id | str | The name of the penguin object the player bashed | |
| penguin_pos | List[float] | The position of the other penguin when it got bashed | |
| hand | Hand | Whether the player performed the bash with their right or left hand. | |  

### **flipper_bash_rock**

An event triggered when the player makes a flipper-bashing move and makes contact with a rock.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| rock_id | str | The name of the rock object the player bashed | |
| rock_pos | List[float] | The position of the rock when it got bashed | |
| hand | Hand | Whether the player performed the bash with their right or left hand. | |  

### **flipper_bash_skua**

An event triggered when the player makes a flipper-bashing move to shoo a skua away from their nest/egg.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| skua_id | str | The name of the skua object the player bashed | |
| skua_pos | List[float] | The position of the skua when it got bashed | |
| penguin_pos | str | The position of the player when they slapped the skua. NOTE : This was added due to a mistake in specification, and is redundant with the position element in game_state. | |
| hand | Hand | Whether the player performed the bash with their right or left hand. | |  

### **peck_nest**

An event triggered when the player's beak makes contact with a nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| nest_id | str | The name of the nest object the player pecked | |
| nest_pos | List[float] | The position of the nest the player pecked | |  

### **peck_penguin**

An event triggered when the player's beak makes contact with another penguin.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| penguin_id | str | The name of the penguin object the player pecked | |
| penguin_pos | List[float] | The position of the other penguin when it got pecked | |  

### **peck_rock**

An event triggered when the player's beak makes contact with a rock.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| rock_id | str | The name of the rock object the player pecked | |
| rock_pos | List[float] | The position of the rock when it got pecked | |  

### **peck_skua**

An event triggered when the player's beak makes contact with a skua.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| skua_id | str | The name of the skua object the player pecked | |
| skua_pos | List[float] | The position of the skua when it got pecked | |  

### **pickup_rock**

An event triggered when the player picks up a rock lying on the ground, which contributes to the building of their nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| total_picked_up | int | The running total of rocks the player has picked up. | |  

### **place_rock**

An event triggered when the player places the rock into their nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| percent_complete | float | The proportion indicating the player's progress towards completing the nest. So far, the game has always been set to require 4 rocks. | |
| rock_count | int | The total number of rocks the player has placed in their nest. | |  

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

### **ring_chime**

An event when the player rings one of the chimes in the chime mini-game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| note_played | str | The name of the chime the player rang | |  

### **bubble_appeared**

Event when a new bubble appears in the mating dance minigame.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the bubble object that appeared | |
| posX | float | The x-position of the bubble that appeared | |
| posY | float | The y-position of the bubble that appeared | |
| posZ | float | The z-position of the bubble that appeared | |  

### **bubble_expired**

Event when a bubble's pop-able time ends and the bubble disappears.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the bubble object that disappeared | |  

### **egg_hatch_indicator_updated**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_remaining | float | The time left until the egg will hatch | |  

### **egg_hatched**

Event when the egg hatches

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **egg_lost**

Event when the player's egg is stolen by a skua.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the skua that stole the egg | |  

### **egg_recovered**

Event when the player recovers the egg from the skuas.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **mating_dance_indicator_updated**

Event when a bubble is popped and the indicator for progress to completion of the mating dance updates.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| percent_full | int | The new percent to which the dance completion indicator is filled | |  

### **nest_complete**

Event when the player completes the building of their nest.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **penguin_pin_fell**

When one of the pins fell in the bowling area.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **skua_spawn**

Event when a new skua is added in the nest/egg defense mini-game.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object_id | str | The name of the skua object that appeared | |
| posX | float | The x-position of the skua that appeared | |
| posY | float | The y-position of the skua that appeared | |
| posZ | float | The z-position of the skua that appeared | |  

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

### **enter_region**

Event when the player moves into one of the regions containing a mini-game or other feature.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| region_name | str | The name of the region the player entered | |  

### **exit_region**

Event when a moves out of one of the regions containing a mini-game or other feature.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| region_name | str | The name of the region the player left | |  

### **activity_begin**

Event when the player begins to engage with a mini-game activity. Exact trigger varies by activity.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| activity_name | Activity | The name of the mini-game/activity with which the player began to engage | |  

### **activity_end**

Event when the player completes a mini-game activity. Exact trigger varies by activity.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| activity_name | Activity | The name of the mini-game/activity the player completed. | |  

### **global_timer_begin**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| time_remaining | int | The left on the global timer | |  

### **global_timer_pause**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| data | Unknown | NOT YET DOCUMENTED | |  

### **global_timer_expired**

NOT YET DOCUMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| data | Unknown | NOT YET DOCUMENTED | |  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

**RegionEnter** : *Detector*   
Triggers an event when a player enter a region  
  

**RegionExit** : *Detector*   
Triggers an event when a player exit a region  
  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**LogVersion** : *int*, *Aggregate feature*   
The version of game the player use.  
  

**SessionDuration** : *timedelta*, *Aggregate feature*   
The duration each session took.  
  

**BuiltNestCount** : *int*, *Aggregate feature*   
The number of times a player with a rock placed the rock on the correct nest.  
  

**BuiltWrongNestCount** : *int*, *Aggregate feature*   
The number of times a player with a rock that has a peck_nest event, where nest_id does not equal to player nest_id.  
  

**RockPickupCount** : *int*, *Aggregate feature*   
The duration each session took.  
  

**RockMultiplePickupCount** : *int*, *Aggregate feature*   
The number of times a player with a rock has peck_rock event.  
  

**RockBashCount** : *int*, *Aggregate feature*   
he number of times a player had a flipper_bash_rock event.  
  

**SkuaBashCount** : *int*, *Aggregate feature*   
The number of times a player bashed skuas  
  

**SkuaPeckCount** : *int*, *Aggregate feature*   
The number of times a player pecked skuas, which does not actually affect the skuas  
  

**EggLostCount** : *int*, *Aggregate feature*   
The number of times a player's egg was stolen by skuas  
  

**EggRecoverTime** : *int*, *Aggregate feature*   
The amount of time the egg spent stolen, with the player trying to recover it  
  

**PenguinInteractCount** : *int*, *Aggregate feature*   
The number of times a player interacted with another penguin via pecks and/or flipper bashes  
  

**GazeCount** : *int*, *Aggregate feature*   
The number of times a player waddled in a given region of the game.  
  

**GazeDuration** : *timedelta*, *Aggregate feature*   
How long gaze event last for.  
  

**WaddleCount** : *int*, *Aggregate feature*   
The number of times a player waddled.  
  

**ActivityCompleted** : *int*, *Aggregate feature*   
The activities completed in a given session.  
  

**ActivityDuration** : *int*, *Aggregate feature*   
How long activity last for.  
  

**RegionsEncountered** : *int*, *Aggregate feature*   
The regions entered in a given session.  
  

**RegionEnterCount** : *int*, *Per-count feature*  (disabled)  
The number of times a player enterd for a given region of the game.  
  

**RegionDuration** : *timedelta*, *Per-count feature*   
The duration of time a player played in a given region of the game.  
  

**WaddlePerRegion** : *int*, *Per-count feature*   
The number of times a player waddled in a given region of the game.  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.  

level_range : range(1, 6)

No changelog prepared

