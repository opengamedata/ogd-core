# Game: LAKELAND

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

### **GAMESTATE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tiles | N/A | pako.gzip(uint8_tile_array()).join() | Gzipped tile [data matrix](#DataMatrices). | |
| farmbits | N/A | pako.gzip(uint8_farmbit_array()).join() | Gzipped farmbit [data matrix](#DataMatrices). | |
| items | N/A | pako.gzip(uint8_item_array()).join() | Gzipped item [data matrix](#DataMatrices). | |
| money | N/A | gg.money | current money | |
| speed | N/A | gg.speed | current game speed (see [Speed](#SpeedConst)) | |
| achievements | N/A | achievements | A boolean array of whether the player has gotten the [achievement](#Achievements) at that index. | |
| num_checkpoints_completed | N/A | get_num_checkpoints_completed() | Number of tutorials began + number of tutorial ended. Includes tutorials skipped. | |
| raining | N/A | gg.b.raining | Boolean - currently raining or not. | |
| curr_selection_type | N/A | gg.inspector.detailed_type | Current selection [inspector content](#InspectorContent) index. (Note that because the game currently (as of 7/25) logs gamestate only after buys, this will always be the type of tile.) | |
| curr_selection_data | N/A | detailed_data() | SelectFarmbit/SelectItem/SelectTile data, depending on the curr_selection_type. | |
| camera_center | N/A | prev_center_txty | Tile that the game is currently centered on. | |
| gametime | N/A | time | Metric to count speed-adjusted time. Based on number of ticks. | |
| timestamp | N/A | now | current client time | |
| num_food_produced | N/A | num_food_produced | total number of food produced (not bought) since the start of the game | | |
| num_milk_produced | N/A | num_milk_produced | total number of milk produced (not bought) since the start of the game | | |
| num_poop_produced | N/A | num_poop_produced | total number of poop produced (not bought) since the start of the game | | |

#### Other Elements

- None  

### **STARTGAME**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_states | N/A | tile_states | 2500 element array of tile state indices. | |
| tile_nutritions | N/A | tile_nutritions | 2500 element array of tile nutritions on a scale 0-255. | |

#### Other Elements

- None  

### **CHECKPOINT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event_category | N/A | arguments[2] | Usually (always?) begin or end | |
| event_label | N/A | arguments[2] | Tutorial name. For example, the name of the tutorial that teaches the player how to build a house is called 'build_a_house' | |
| event_type | N/A | arguments[1] | Usually (always?) tutorial | |
| blurb_history | N/A | flush_blurb_history(now) | List of client time relative to now for each blurb popup. (Blurbs are now logged here instead of the [blurb](#blurb) event.) | |
| client_time | N/A | now | current client time | |
| continue | N/A | gg.continue_ls ? 1: 0 | 1/0 boolean to indicate whether the player continued or not | |
| language | N/A | g.scenes[1].language_toggle.on ? 'espanol':'english' | language of the game | |
| audio | N/A | AUDIO ? 1: 0 | 1/0 boolean to indicate whether audio was toggled on or not | |
| fullscreen | N/A | g.scenes[1].fullscreen_toggle.on ? 1:  | 1/0 boolean to indicate whether the game was toggled into fullscreen whether or not | |

#### Other Elements

- None  

### **SELECTTILE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Tile [mark indices](#Mark). | |

#### Other Elements

- None  

### **SELECTFARMBIT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| farmbit | N/A | farmbit_data_short(f) | See [Data Short](#DataShort). | |

#### Other Elements

- None  

### **SELECTITEM**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| item | N/A | item_data_short(it) | See [Data Short](#DataShort). | |
| mark | N/A | it.mark | Item [mark index](#Mark). | |

#### Other Elements

- None  

### **SELECTBUY**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| buy | N/A | buy | [Buy index](#Buys). | |
| cost | N/A | gg.shop.buy_cost(buy) | Cost of buy | |
| curr_money | N/A | gg.money | Current money | |
| success | N/A | gg.money>=gg.shop.buy_cost(buy) | Boolean. Whether the buy can be selected or not. (Cannot select a buy that cannot be paid for.) | |

#### Other Elements

- None  

### **BUY**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| buy | N/A | gg.shop.selected_buy | [Buy index](#Buys). | |
| tile | N/A | tile_data_short(gg.b.hover_t) | [Data Short](#DataShort) for the tile the buy will be placed on. | |
| success | N/A | gg.b.placement_valid(gg.b.hover_tgg.shop.selected_buy) | Boolean. Whether the buy can be put on the tile. If not, buy fails. | |
| buy_hovers | N/A | flush_buy_hovers(now) | List of tile [Data Short](#DataShort) appended with client time before now for each hovered tile since either selectbuy log or the previous buy log. | |
| client_time | N/A | now | current client time | |

#### Other Elements

- None  

### **CANCELBUY**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| selected_buy | N/A | buy | [Buy index](#Buys). | |
| cost | N/A | gg.shop.buy_cost(buy) | Cost of buy. | |
| curr_money | N/A | gg.money | Current money. | |
| buy_hovers | N/A | flush_buy_hovers(now) | List of tile [Data Short](#DataShort) appended with client time before now for each hovered tile since either selectbuy log or the previous buy log. | |
| client_time | N/A | now | current client time | |

#### Other Elements

- None  

### **ROADBUILDS**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| road_builds | N/A | flush_road_hovers(now) | List of tile [Data Short](#DataShort) appended with client time before now for each tile a road was built on. | |
| client_time | N/A | now | current client time | |

#### Other Elements

- None  

### **TILEUSESELECT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Tile [mark indices](#Mark). | |

#### Other Elements

- None  

### **ITEMUSESELECT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| item | N/A | item_data_short(it) | See [Data Short](#DataShort). | |
| prev_mark | N/A | it.mark | Item [mark index](#Mark). | |

#### Other Elements

- None  

### **TOGGLENUTRITION**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| to_state | N/A | gg.b.nutrition_view | 1 if nutrition view is being turned on, 0 if turned off. | |
| tile_nutritions | N/A | nutrition_array() | 2500 element array of tile nutritions on a scale 0-255. | |

#### Other Elements

- None  

### **TOGGLESHOP**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| shop_open | N/A | gg.shop.open | 1 if the shop view is being opened, 0 if closed. | |

#### Other Elements

- None  

### **TOGGLEACHIEVEMENTS**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| achievements_open | N/A | gg.achievements.open | 1 if the achievement view is being opened, 0 if closed. | |

#### Other Elements

- None  

### **SKIPTUTORIAL**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| (none) | N/A |  | Event itself indicates that the player skipped a tutorial (the tutorial skipped is the last tutorial event logged). | |

#### Other Elements

- None  

### **SPEED**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| cur_speed | N/A | gg.speed | To [speed](#SpeedConst) index. | |
| prev_speed | N/A | speed | From [speed](#SpeedConst) index. | |
| manual | N/A | manual_speed_bool | bool: 1 if speed was manually changed, 0 if not  | |

#### Other Elements

- None  

### **ACHIEVEMENT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| achievement | N/A | i | [Achievement](#Achievements) index. | |

#### Other Elements

- None  

### **FARMBITDEATH**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| farmbit | N/A | farmbit_data_short(f) | See [Data Short](#DataShort). | |
| grave | N/A | tile_data_short(f.home) | Tile data short of dead farmbit's home. | |

#### Other Elements

- None  

### **BLURB**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| (none) | N/A |  | Event itself indicates that the player clicked to the next blurb in a tutorial etc. (the tutorial itself is the last tutorial event logged). | |

#### Other Elements

- None  

### **CLICK**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| (not currently implemented) | N/A |  |  | |

#### Other Elements

- None  

### **RAINSTOPPED**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| (none) | N/A |  | Log itself indicates that it was raining and the raining has now stopped. | |

#### Other Elements

- None  

### **HISTORY**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| client_time | N/A | now | current client time | |
| camera_history | N/A | flush_camera_history(now) | List of [camera moves](#CameraMove) since last history log. | |
| emote_history | N/A | flush_emote_history(now) | List of 11 element sublists [[farmbit](#DataShort), [emote index](#Emotes), time before client_time (negative number)] emotes since last history log. | |

#### Other Elements

- None  

### **ENDGAME**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| (none) | N/A |  | Log itself indicates the player has left the game page. Seperate history and gamestate logs are sent. | |

#### Other Elements

- None  

### **EMOTE**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| farmbit | N/A | farmbit_data_short(t) | See [Data Short](#DataShort). | |
| emote_enum | N/A | emote_id | See [emotes](#Emotes). | |

#### Other Elements

- None  

### **FARMFAIL**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | Farm that failed. See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Farm [mark indices](#Mark). | |

#### Other Elements

- None  

### **BLOOM**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Not relevant to lake tiles. Included for uniformity. | |

#### Other Elements

- None  

### **FARMHARVESTED**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | Farm that produced corn. See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Tile [mark indices](#Mark). | |

#### Other Elements

- None  

### **MILKPRODUCED**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | Dairy that produced milk. See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Tile [mark indices](#Mark). | |

#### Other Elements

- None  

### **POOPPRODUCED**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile | N/A | tile_data_short(t) | Dairy that produced poop. See [Data Short](#DataShort). | |
| marks | N/A | t.marks | Tile [mark indices](#Mark). | |

#### Other Elements

- None  

### **DEBUG**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| (none) | N/A |  | Event itself means that someone has used 'spyparty' to enter debug mode. | |

#### Other Elements

- None  

### **NEWFARMBIT**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| farmbit | N/A | farmbit_data_short(t) | See [Data Short](#DataShort). | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**sess_count_achievements** : *int*, *Aggregate feature*  (disabled)  
Player feature - Progress: count of achievements  
  

**sess_count_encounter_tutorial** : *int*, *Aggregate feature*  (disabled)  
Player feature - Progress: count of tutorials  
  

**sess_count_skips** : *int*, *Aggregate feature*  (disabled)  
Player feature - Progress: count of skips  
  

**sess_count_gamestate_logs** : *int*, *Aggregate feature*  (disabled)  
count of gamestate logs  
  

**sess_count_rains** : *int*, *Aggregate feature*  (disabled)  
Count of how many times it rained  
  

**sess_count_explore_events** : *int*, *Aggregate feature*  (disabled)  
number of events that explore the gamestate: SELECTTILE, SELECTFARMBIT, SELECTITEM, TOGGLEACHIEVEMENTS, TOGGLESHOP  
  

**sess_count_impact_events** : *int*, *Aggregate feature*  (disabled)  
number of active events that change the gamestate: BUY,TILEUSESELECT,ITEMUSESELECT  
  

**sess_count_idle** : *int*, *Aggregate feature*  (disabled)  
number of times the player went from active to idle  
  

**sess_count_buy_home** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a home  
  

**sess_count_buy_food** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a food  
  

**sess_count_buy_farm** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a farm  
  

**sess_count_buy_fertilizer** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a fertilizer  
  

**sess_count_buy_livestock** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a livestock  
  

**sess_count_buy_skimmer** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a skimmer  
  

**sess_count_buy_sign** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a sign  
  

**sess_count_buy_road** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: buy a road  
  

**sess_money_spent_home** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on home  
  

**sess_money_spent_food** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on food  
  

**sess_money_spent_farm** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on farm  
  

**sess_money_spent_fertilizer** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on fertilizer  
  

**sess_money_spent_livestock** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on livestock  
  

**sess_money_spent_skimmer** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on skimmer  
  

**sess_money_spent_sign** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on sign  
  

**sess_money_spent_road** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: money spent on road  
  

**sess_count_change_item_mark** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: change a sale/eat/feed state in an item panel  
  

**sess_count_change_tile_mark** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: change a sale/eat/feed state in a farm panel  
  

**sess_time_to_exist_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the exist achievement (or 0 if not achieved)  
  

**sess_time_active_to_exist_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the exist achievement (or 0 if not achieved)  
  

**sess_time_to_group_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the group achievement (or 0 if not achieved)  
  

**sess_time_active_to_group_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the group achievement (or 0 if not achieved)  
  

**sess_time_to_town_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the town achievement (or 0 if not achieved)  
  

**sess_time_active_to_town_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the town achievement (or 0 if not achieved)  
  

**sess_time_to_city_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the city achievement (or 0 if not achieved)  
  

**sess_time_active_to_city_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the city achievement (or 0 if not achieved)  
  

**sess_time_to_farmer_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the farmer achievement (or 0 if not achieved)  
  

**sess_time_active_to_farmer_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the farmer achievement (or 0 if not achieved)  
  

**sess_time_to_farmers_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the farmers achievement (or 0 if not achieved)  
  

**sess_time_active_to_farmers_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the farmers achievement (or 0 if not achieved)  
  

**sess_time_to_farmtown_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the farmtown achievement (or 0 if not achieved)  
  

**sess_time_active_to_farmtown_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the farmtown achievement (or 0 if not achieved)  
  

**sess_time_to_megafarm_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the megafarm achievement (or 0 if not achieved)  
  

**sess_time_active_to_megafarm_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the megafarm achievement (or 0 if not achieved)  
  

**sess_time_to_paycheck_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the paycheck achievement (or 0 if not achieved)  
  

**sess_time_active_to_paycheck_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the paycheck achievement (or 0 if not achieved)  
  

**sess_time_to_thousandair_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the thousandair achievement (or 0 if not achieved)  
  

**sess_time_active_to_thousandair_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the thousandair achievement (or 0 if not achieved)  
  

**sess_time_to_stability_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the stability achievement (or 0 if not achieved)  
  

**sess_time_active_to_stability_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the stability achievement (or 0 if not achieved)  
  

**sess_time_to_riches_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the riches achievement (or 0 if not achieved)  
  

**sess_time_active_to_riches_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the riches achievement (or 0 if not achieved)  
  

**sess_time_to_bloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the bloom achievement (or 0 if not achieved)  
  

**sess_time_active_to_bloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the bloom achievement (or 0 if not achieved)  
  

**sess_time_to_bigbloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the bigbloom achievement (or 0 if not achieved)  
  

**sess_time_active_to_bigbloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the bigbloom achievement (or 0 if not achieved)  
  

**sess_time_to_hugebloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the hugebloom achievement (or 0 if not achieved)  
  

**sess_time_active_to_hugebloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the hugebloom achievement (or 0 if not achieved)  
  

**sess_time_to_massivebloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the massivebloom achievement (or 0 if not achieved)  
  

**sess_time_active_to_massivebloom_achievement** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to the massivebloom achievement (or 0 if not achieved)  
  

**sess_time_to_another_death_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to another_death tutorial (or 0 if unencountered)  
  

**sess_time_active_to_another_death_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to another_death tutorial (or 0 if unencountered)  
  

**sess_time_to_another_member_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to another_member tutorial (or 0 if unencountered)  
  

**sess_time_active_to_another_member_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to another_member tutorial (or 0 if unencountered)  
  

**sess_time_to_bloom_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to bloom tutorial (or 0 if unencountered)  
  

**sess_time_active_to_bloom_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to bloom tutorial (or 0 if unencountered)  
  

**sess_time_to_build_a_farm_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to build_a_farm tutorial (or 0 if unencountered)  
  

**sess_time_active_to_build_a_farm_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to build_a_farm tutorial (or 0 if unencountered)  
  

**sess_time_to_build_a_house_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to build_a_house tutorial (or 0 if unencountered)  
  

**sess_time_active_to_build_a_house_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to build_a_house tutorial (or 0 if unencountered)  
  

**sess_time_to_buy_fertilizer_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to buy_fertilizer tutorial (or 0 if unencountered)  
  

**sess_time_active_to_buy_fertilizer_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to buy_fertilizer tutorial (or 0 if unencountered)  
  

**sess_time_to_buy_food_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to buy_food tutorial (or 0 if unencountered)  
  

**sess_time_active_to_buy_food_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to buy_food tutorial (or 0 if unencountered)  
  

**sess_time_to_buy_livestock_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to buy_livestock tutorial (or 0 if unencountered)  
  

**sess_time_active_to_buy_livestock_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to buy_livestock tutorial (or 0 if unencountered)  
  

**sess_time_to_death_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to death tutorial (or 0 if unencountered)  
  

**sess_time_active_to_death_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to death tutorial (or 0 if unencountered)  
  

**sess_time_to_end_life_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to end_life tutorial (or 0 if unencountered)  
  

**sess_time_active_to_end_life_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to end_life tutorial (or 0 if unencountered)  
  

**sess_time_to_extra_life_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to extra_life tutorial (or 0 if unencountered)  
  

**sess_time_active_to_extra_life_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to extra_life tutorial (or 0 if unencountered)  
  

**sess_time_to_final_death_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to final_death tutorial (or 0 if unencountered)  
  

**sess_time_active_to_final_death_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to final_death tutorial (or 0 if unencountered)  
  

**sess_time_to_flooded_fertilizer_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to flooded_fertilizer tutorial (or 0 if unencountered)  
  

**sess_time_active_to_flooded_fertilizer_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to flooded_fertilizer tutorial (or 0 if unencountered)  
  

**sess_time_to_gross_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to gross tutorial (or 0 if unencountered)  
  

**sess_time_active_to_gross_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to gross tutorial (or 0 if unencountered)  
  

**sess_time_to_gross_again_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to gross_again tutorial (or 0 if unencountered)  
  

**sess_time_active_to_gross_again_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to gross_again tutorial (or 0 if unencountered)  
  

**sess_time_to_livestock_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to livestock tutorial (or 0 if unencountered)  
  

**sess_time_active_to_livestock_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to livestock tutorial (or 0 if unencountered)  
  

**sess_time_to_long_travel_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to long_travel tutorial (or 0 if unencountered)  
  

**sess_time_active_to_long_travel_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to long_travel tutorial (or 0 if unencountered)  
  

**sess_time_to_low_nutrients_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to low_nutrients tutorial (or 0 if unencountered)  
  

**sess_time_active_to_low_nutrients_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to low_nutrients tutorial (or 0 if unencountered)  
  

**sess_time_to_mass_sadness_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to mass_sadness tutorial (or 0 if unencountered)  
  

**sess_time_active_to_mass_sadness_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to mass_sadness tutorial (or 0 if unencountered)  
  

**sess_time_to_poop_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to poop tutorial (or 0 if unencountered)  
  

**sess_time_active_to_poop_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to poop tutorial (or 0 if unencountered)  
  

**sess_time_to_rain_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to rain tutorial (or 0 if unencountered)  
  

**sess_time_active_to_rain_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to rain tutorial (or 0 if unencountered)  
  

**sess_time_to_sell_food_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to sell_food tutorial (or 0 if unencountered)  
  

**sess_time_active_to_sell_food_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to sell_food tutorial (or 0 if unencountered)  
  

**sess_time_to_successful_harvest_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to successful_harvest tutorial (or 0 if unencountered)  
  

**sess_time_active_to_successful_harvest_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to successful_harvest tutorial (or 0 if unencountered)  
  

**sess_time_to_timewarp_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to timewarp tutorial (or 0 if unencountered)  
  

**sess_time_active_to_timewarp_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to timewarp tutorial (or 0 if unencountered)  
  

**sess_time_to_unattended_farm_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to unattended_farm tutorial (or 0 if unencountered)  
  

**sess_time_active_to_unattended_farm_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to unattended_farm tutorial (or 0 if unencountered)  
  

**sess_time_to_unused_fertilizer_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to unused_fertilizer tutorial (or 0 if unencountered)  
  

**sess_time_active_to_unused_fertilizer_tutorial** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to unused_fertilizer tutorial (or 0 if unencountered)  
  

**sess_time_to_first_home_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first home  
  

**sess_time_active_to_first_home_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first home  
  

**sess_time_to_first_food_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first food  
  

**sess_time_active_to_first_food_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first food  
  

**sess_time_to_first_farm_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first farm  
  

**sess_time_active_to_first_farm_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first farm  
  

**sess_time_to_first_fertilizer_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first fertilizer  
  

**sess_time_active_to_first_fertilizer_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first fertilizer  
  

**sess_time_to_first_livestock_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first livestock  
  

**sess_time_active_to_first_livestock_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first livestock  
  

**sess_time_to_first_skimmer_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first skimmer  
  

**sess_time_active_to_first_skimmer_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first skimmer  
  

**sess_time_to_first_sign_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first sign  
  

**sess_time_active_to_first_sign_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first sign  
  

**sess_time_to_first_road_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first road  
  

**sess_time_active_to_first_road_buy** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first road  
  

**sess_time_to_first_death** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first death  
  

**sess_time_active_to_first_death** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first death  
  

**sess_time_to_first_rain** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first rain  
  

**sess_time_active_to_first_rain** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first rain  
  

**sess_time_to_first_bloom** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first bloom  
  

**sess_time_active_to_first_bloom** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first bloom  
  

**sess_time_to_first_milkproduced** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first milk produced  
  

**sess_time_active_to_first_milkproduced** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first milk produced  
  

**sess_time_to_first_poopproduced** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first poop produced (from dairy)  
  

**sess_time_active_to_first_poopproduced** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first poop produced (from dairy)  
  

**sess_time_to_first_sale** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first sale  
  

**sess_time_active_to_first_sale** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first sale  
  

**sess_time_to_first_farmfail** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first farmfail (farm growth slows near 0)  
  

**sess_time_active_to_first_farmfail** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first farmfail (farm growth slows near 0)  
  

**sess_time_to_first_tilemarkchange** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first tile mark change  
  

**sess_time_active_to_first_tilemarkchange** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first tile mark change  
  

**sess_time_to_first_itemmarkchange** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first item mark change  
  

**sess_time_active_to_first_itemmarkchange** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first item mark change  
  

**sess_time_to_first_togglenutrition** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first toggle nutrition  
  

**sess_time_active_to_first_togglenutrition** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first toggle nutrition  
  

**sess_time_to_first_toggleachievements** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first toggle achievements  
  

**sess_time_active_to_first_toggleachievements** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first toggle achievements  
  

**sess_time_to_first_skip** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first tutorial skip  
  

**sess_time_active_to_first_skip** : **, *Aggregate feature*  (disabled)  
Player feature - Progress: Time to first tutorial skip  
  

**sess_time_to_first_null_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_null_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_fullness_motivated_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_fullness_motivated_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_fullness_desperate_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_fullness_desperate_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_energy_desperate_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_energy_desperate_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_joy_motivated_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_joy_motivated_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_joy_desperate_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_joy_desperate_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_puke_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_puke_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_yum_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_yum_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_tired_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_tired_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_happy_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_happy_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_swim_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_active_to_first_swim_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type  
  

**sess_time_to_first_sale_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type (same as sess_time_to_first_sale)  
  

**sess_time_active_to_first_sale_emote** : **, *Aggregate feature*  (disabled)  
Session time to first emote type (same as sess_time_to_first_sale)  
  

**sess_time_to_first_food_sale** : **, *Aggregate feature*  (disabled)  
Session time to first food sale  
  

**sess_time_active_to_first_food_sale** : **, *Aggregate feature*  (disabled)  
Session time to first food sale  
  

**sess_time_to_first_milk_sale** : **, *Aggregate feature*  (disabled)  
Session time to first milk sale  
  

**sess_time_active_to_first_milk_sale** : **, *Aggregate feature*  (disabled)  
Session time to first milk sale  
  

**sess_time_to_first_poop_sale** : **, *Aggregate feature*  (disabled)  
Session time to first poop sale  
  

**sess_time_active_to_first_poop_sale** : **, *Aggregate feature*  (disabled)  
Session time to first poop sale  
  

**sess_time_to_first_water_sale** : **, *Aggregate feature*  (disabled)  
Session time to first water sale  
  

**sess_time_active_to_first_water_sale** : **, *Aggregate feature*  (disabled)  
Session time to first water sale  
  

**sess_time_to_reset** : **, *Aggregate feature*  (disabled)  
Session time to first emote type (same as sess_time_to_first_sale)  
  

**sess_time_active_to_reset** : **, *Aggregate feature*  (disabled)  
Session time to first emote type (same as sess_time_to_first_sale)  
  

**sess_avg_num_tiles_hovered_before_placing_home** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing home  
  

**sess_avg_num_tiles_hovered_before_placing_food** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing food  
  

**sess_avg_num_tiles_hovered_before_placing_farm** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing farm  
  

**sess_avg_num_tiles_hovered_before_placing_fertilizer** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing fertilizer  
  

**sess_avg_num_tiles_hovered_before_placing_livestock** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing livestock  
  

**sess_avg_num_tiles_hovered_before_placing_skimmer** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing skimmer  
  

**sess_avg_num_tiles_hovered_before_placing_sign** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing sign  
  

**sess_avg_num_tiles_hovered_before_placing_road** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: ave num tiles hovered before placing (the first) road  
  

**sess_avg_time_per_blurb_in_another_death_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_another_member_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_bloom_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_build_a_farm_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_build_a_house_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_buy_fertilizer_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_buy_food_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_buy_livestock_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_death_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_end_life_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_extra_life_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_final_death_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_flooded_fertilizer_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_gross_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_gross_again_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_livestock_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_long_travel_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_low_nutrients_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_mass_sadness_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_poop_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_rain_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_sell_food_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_successful_harvest_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_timewarp_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_unattended_farm_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb_in_unused_fertilizer_tutorial** : *float*, *Aggregate feature*  (disabled)  
time per textbox in the specified tutorial  
  

**sess_avg_time_per_blurb** : *float*, *Aggregate feature*  (disabled)  
? include skips ? Player feature - General: ave time per tutorial screen (blurb) before continue  
  

**sess_count_food_produced** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: num of food produced  
  

**sess_count_milk_produced** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: num of milk produced  
  

**sess_count_poop_produced** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: num of poop produced  
  

**sess_money_earned** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: money earned  
  

**sess_money_spent** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: money earned  
  

**sess_time_in_nutrition_view** : **, *Aggregate feature*  (disabled)  
Player feature - Total amount of time the player: spend in nutrition view  
  

**sess_time_in_game_speed_pause** : **, *Aggregate feature*  (disabled)  
Player feature - Total amount of time the player: in game speed pause (with client identified to correct for fps)   
  

**sess_time_in_game_speed_play** : **, *Aggregate feature*  (disabled)  
Player feature - Total amount of time the player: in game speed play (with client identified to correct for fps)   
  

**sess_time_in_game_speed_fast** : **, *Aggregate feature*  (disabled)  
Player feature - Total amount of time the player: in game speed fast (with client identified to correct for fps)   
  

**sess_time_in_game_speed_vfast** : **, *Aggregate feature*  (disabled)  
Player feature - Total amount of time the player: in game speed vfast (with client identified to correct for fps)   
  

**sess_max_num_per_capita_food_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of food marked for sale  
  

**sess_max_num_per_capita_food_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of food marked for eat  
  

**sess_max_num_per_capita_food_marked_feed** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of food marked for feed  
  

**sess_max_num_per_capita_milk_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of milk marked for sale  
  

**sess_max_num_per_capita_milk_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of milk marked for eat  
  

**sess_max_num_per_capita_poop_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of poop marked for sale  
  

**sess_max_num_per_capita_poop_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: maximum per capita number of poop marked for fertilize  
  

**sess_min_num_per_capita_food_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of food marked for sale  
  

**sess_min_num_per_capita_food_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of food marked for eat  
  

**sess_min_num_per_capita_food_marked_feed** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of food marked for feed  
  

**sess_min_num_per_capita_milk_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of milk marked for sale  
  

**sess_min_num_per_capita_milk_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of milk marked for eat  
  

**sess_min_num_per_capita_poop_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of poop marked for sale  
  

**sess_min_num_per_capita_poop_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: minimum per capita number of poop marked for fertilize  
  

**sess_max_num_food_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for sale  
  

**sess_max_num_food_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for eat  
  

**sess_max_num_food_marked_feed** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for feed  
  

**sess_max_num_milk_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for sale  
  

**sess_max_num_milk_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for eat  
  

**sess_max_num_poop_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for sale  
  

**sess_max_num_poop_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for fertilize  
  

**sess_max_percent_food_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for sale  
  

**sess_max_percent_food_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for eat  
  

**sess_max_percent_food_marked_feed** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for feed  
  

**sess_max_percent_milk_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for sale  
  

**sess_max_percent_milk_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for eat  
  

**sess_max_percent_poop_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for sale  
  

**sess_max_percent_poop_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for fertilize  
  

**sess_min_num_food_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for sale  
  

**sess_min_num_food_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for eat  
  

**sess_min_num_food_marked_feed** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for feed  
  

**sess_min_num_milk_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for sale  
  

**sess_min_num_milk_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for eat  
  

**sess_min_num_poop_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for sale  
  

**sess_min_num_poop_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for fertilize  
  

**sess_min_percent_food_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for sale  
  

**sess_min_percent_food_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for eat  
  

**sess_min_percent_food_marked_feed** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of food marked for feed  
  

**sess_min_percent_milk_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for sale  
  

**sess_min_percent_milk_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of milk marked for eat  
  

**sess_min_percent_poop_marked_sell** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for sale  
  

**sess_min_percent_poop_marked_use** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent of poop marked for fertilize  
  

**sess_min_num_home_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of home in play  
  

**sess_max_num_home_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of home in play  
  

**sess_min_num_grave_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of home in play  
  

**sess_max_num_grave_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of home in play  
  

**sess_min_num_farm_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of farm in play  
  

**sess_max_num_farm_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of farm in play  
  

**sess_min_num_fertilizer_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of fertilizer in play  
  

**sess_max_num_fertilizer_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of fertilizer in play  
  

**sess_min_num_livestock_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of livestock in play  
  

**sess_max_num_livestock_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of livestock in play  
  

**sess_min_num_skimmer_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of skimmer in play  
  

**sess_max_num_skimmer_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of skimmer in play  
  

**sess_min_num_sign_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of sign in play  
  

**sess_max_num_sign_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of sign in play  
  

**sess_min_num_road_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of road in play  
  

**sess_max_num_road_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of road in play  
  

**sess_min_num_food_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of food in play  
  

**sess_max_num_food_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of food in play  
  

**sess_min_num_poop_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of poop in play  
  

**sess_max_num_poop_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of poop in play  
  

**sess_min_num_milk_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: min number of milk in play  
  

**sess_max_num_milk_in_play** : *int*, *Aggregate feature*  (disabled)  
Player feature - General: max number of milk in play  
  

**sess_count_fullness_motivated_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the fullness_motivated emotes per capita  
  

**sess_count_fullness_desperate_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the fullness_desperate emotes per capita  
  

**sess_count_energy_desperate_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the energy_desperate emotes per capita  
  

**sess_count_joy_motivated_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the joy_motivated emotes per capita  
  

**sess_count_joy_desperate_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the joy_desperate emotes per capita  
  

**sess_count_puke_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the puke emotes per capita  
  

**sess_count_yum_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the yum emotes per capita  
  

**sess_count_tired_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the tired emotes per capita  
  

**sess_count_happy_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the happy emotes per capita  
  

**sess_count_swim_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the swim emotes per capita  
  

**sess_count_sale_txt_emotes_per_capita** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: max num of the sale emotes per capita  
  

**sess_percent_positive_emotes** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: percent positive emotes  
  

**sess_percent_negative_emotes** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: percent negative emotes  
  

**sess_percent_neutral_emotes** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: percent neutral emotes  
  

**sess_total_positive_emotes** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: total positive emotes  
  

**sess_total_negative_emotes** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: total negative emotes  
  

**sess_total_neutral_emotes** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: total neutral emotes  
  

**sess_avg_distance_between_poop_placement_and_lake** : *float*, *Aggregate feature*  (disabled)  
 Player feature - Assessment: average distance between poop placement and lake  
  

**sess_avg_avg_distance_between_buildings** : *float*, *Aggregate feature*  (disabled)  
Player feature - Assessment: Average distance between buildings (when they build, how far is it from the closest thing)  
  

**sess_count_farmfails** : *int*, *Aggregate feature*  (disabled)  
Count of farms going into low productivity (nutrition roughly < 1%)  
  

**sess_max_avg_lake_nutrition** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: ave lake nutrition  
  

**sess_min_avg_lake_nutrition** : *float*, *Aggregate feature*  (disabled)  
Game feature - General: ave lake nutrition  
  

**sess_count_blooms** : *int*, *Aggregate feature*  (disabled)  
Count of algae blooms  
  

**sess_count_inspect_tile** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: inspect a tile  
  

**sess_count_inspect_farmbit** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: inspect a farmbit  
  

**sess_count_inspect_item** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: inspect a item  
  

**sess_count_open_achievements** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: look at achievements  
  

**sess_count_open_shop** : *int*, *Aggregate feature*  (disabled)  
Player feature - Number of times the player: open the shop  
  

**sess_count_deaths** : *int*, *Aggregate feature*  (disabled)  
Game feature - General: num deaths per sess  
  

**event_sequence** : **, *Aggregate feature*  (disabled)  
Sequence of buys, deaths, blooms, and others in the game  
  

**sess_percent_building_a_farm_on_highest_nutrition_tile** : *float*, *Aggregate feature*  (disabled)  
Player feature - General: percent building a farm on the best tile with the highest nutrition that was hovered over during the buy process  
  

**sess_percent_placing_fertilizer_on_lowest_nutrient_farm** : *float*, *Aggregate feature*  (disabled)  
 TODO:::figure out how to calculate this:::TODO Player feature - General: percent placing fertilizer on lowest nutrient farm  
  

**sess_EventCount** : *int*, *Aggregate feature*  (disabled)  
The total number of events across the entire sess  
  

**sess_ActiveEventCount** : *int*, *Aggregate feature*  (disabled)  
Number of player events that require the player's active input  
  

**sess_InactiveEventCount** : *int*, *Aggregate feature*  (disabled)  
Number of game events that don't require the player's active input  
  

**sess_time_idle** : **, *Aggregate feature*  (disabled)  
Amount of time in gameplay spent idle (time past IDLE_THRESH_SECONDS without active log)  
  

**sess_time_active** : **, *Aggregate feature*  (disabled)  
Amount of time in gameplay spent actively playing (not going more than IDLE_THRESH_SECONDS without an active event)  
  

**sess_time_in_secs** : *int*, *Aggregate feature*  (disabled)  
Time (in seconds) spent on the game (copy of sessDuration)  
  

**play_year** : *int*, *Aggregate feature*  (disabled)  
year started the game (UTC)  
  

**play_month** : *int*, *Aggregate feature*  (disabled)  
month started the game (UTC)  
  

**play_day** : *int*, *Aggregate feature*  (disabled)  
day started the game (UTC)  
  

**play_hour** : *int*, *Aggregate feature*  (disabled)  
hour started the game (UTC)  
  

**play_minute** : *int*, *Aggregate feature*  (disabled)  
minute started the game (UTC)  
  

**play_second** : *int*, *Aggregate feature*  (disabled)  
second started the game (UTC)  
  

**rt_currently_active** : *bool*, *Aggregate feature*  (disabled)  
(boolean - 1/0) whether or not the player is currently active  
  

**continue** : *bool*, *Aggregate feature*  (disabled)  
1 if player continued, 0 if new game  
  

**language** : *str*, *Aggregate feature*  (disabled)  
language name  
  

**audio** : *bool*, *Aggregate feature*  (disabled)  
1 if audio on, 0 if off  
  

**fullscreen** : *bool*, *Aggregate feature*  (disabled)  
1 if fullscreen, 0 if not  
  

**version** : *int*, *Aggregate feature*  (disabled)  
version number  
  

**debug** : *bool*, *Aggregate feature*  (disabled)  
1 if player used a debug feature, 0 if not  
  

**num_play** : *int*, *Aggregate feature*  (disabled)  
Playthrough number (i.e., if a player has died and restarts, this number will be 1 in the first playthrough and 2 in the second)  
  

**sessID** : **, *Aggregate feature*  (disabled)  
The player's sess ID number for this play sess  
  

**persistentSessionID** : **, *Aggregate feature*  (disabled)  
The sess ID for the player's device, persists across multiple players using the same device.  
  

**sessDuration** : *int*, *Aggregate feature*  (disabled)  
The total time (in seconds) spent over the entire sess  
  

**player_id** : **, *Aggregate feature*  (disabled)  
Player ID  


No changelog prepared

