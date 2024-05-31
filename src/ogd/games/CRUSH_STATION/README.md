# Game: CRUSH_STATION

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

### **region**

(code=1500), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| city | str | TODO | |
| region | str | TODO | |
| country | str | TODO | |
| zipCode | int | TODO | |

#### Other Elements

- None  

### **welcome**

(code=4500), It only happens the first time the game runs

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| agreed | ?bool? | TODO | |
| age | int | TODO | |
| deviceType | ?str? | TODO | |

#### Other Elements

- None  

### **general_level_stats**

(code=5500), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| right | ?int? | TODO | |
| wrong | ?int? | TODO | |
| missed | ?int? | TODO | |

#### Other Elements

- None  

### **general_game_stats**

(code=5501), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| right | ?int? | TODO | |
| wrong | ?int? | TODO | |
| missed | ?int? | TODO | |

#### Other Elements

- None  

### **general_level_times**

(code=5502), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| playTime | ?timedelta? | TODO | |
| gameTime | ?timedelta? | TODO | |
| averageTimeRight | ?timedelta? | TODO | |
| averageTimeWrong | ?timedelta? | TODO | |

#### Other Elements

- None  

### **general_game_times**

(code=5503), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| playTime | ?timedelta? | TODO | |
| gameTime | ?timedelta? | TODO | |
| averageTimeRight | ?timedelta? | TODO | |
| averageTimeWrong | ?timedelta? | TODO | |

#### Other Elements

- None  

### **general_game_levels**

(code=5504), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| startLevel | ?str? | TODO | |
| endLevel | ?str? | TODO | |
| highestLevel | ?str? | TODO | |

#### Other Elements

- None  

### **start_game**

(code=1001) Generally not exported by Al

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| gameName | str | TODO | |

#### Other Elements

- None  

### **gamescribe_created**

(code=1002) Generally not exported by Al

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| gamescribeMode | enum(trace, strict) | trace or strict (trace is for debug, strict for production) | |

#### Other Elements

- None  

### **settings**

(code=2001) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| playTime | int | Amount of active play time research intended for players, as set in DREAM. Not counting instruction screens. | |

#### Other Elements

- None  

### **main_menu_shown**

(code=3001) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **level_menu_shown**

(code=3002) This will never be jotted for Fall 2018, because we're not using the level menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| passedLevel | bool | Binary - did they complete the level or not? | |
| highestPanelUnlocked | ?int? | This refers to the highest panel unlocked. The game organizes progess in levels and panels (i.e., dots at the bottom), with up to 20 (?) levels per panel.  | |
| highestLevelUnlocked | ?int? | This shows the highest level unlocked. The game organizes progess in levels and panels, with up to 20 (?) levels per panel.  | |

#### Other Elements

- None  

### **level_start**

(code=3003) Called once the level starts, tutorial not included

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **bubble_shown**

(code=3004) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| id | int | TODO | |

#### Other Elements

- None  

### **bubble_hidden**

(code=3005) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| id | int | TODO | |

#### Other Elements

- None  

### **bubble_active**

(code=3006) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| id | int | TODO | |

#### Other Elements

- None  

### **bubble_chosen**

(code=4001) Called every time a bubble UI is unfolded

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| id | int | id of the bubble whose UI has been unfolded | |
| bubblesArray | List[Dict] | A list of bubbles |**color** : enum(ALREADY_SUBMITTED, GREEN, YELLOW, RED, PINK, PURPLE), **shape** : enum(ALREADY_SUBMITTED, CRAB, JELLYFISH, STARFISH, STINGRAY, LOBSTER), **id** : int |

#### Other Elements

- None  

### **color_animal_selection**

(code=4002) (All the choices a player makes, even before bubble has been submitted)

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| id | int | TODO | |
| color | enum(ALREADY_SUBMITTED, GREEN, YELLOW, RED, PINK, PURPLE) | TODO | |
| shape | enum(ALREADY_SUBMITTED, CRAB, JELLYFISH, STARFISH, STINGRAY, LOBSTER) | TODO | |

#### Other Elements

- None  

### **bubble_done**

(code=4003) Called every time a bubble UI is unfolded

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| id | int | TODO | |
| color | enum(ALREADY_SUBMITTED, GREEN, YELLOW, RED, PINK, PURPLE) | TODO | |
| shape | enum(ALREADY_SUBMITTED, CRAB, JELLYFISH, STARFISH, STINGRAY, LOBSTER) | TODO | |
| bubblesArray | List[Dict] | TODO |**color** : enum(ALREADY_SUBMITTED, GREEN, YELLOW, RED, PINK, PURPLE), **shape** : enum(ALREADY_SUBMITTED, CRAB, JELLYFISH, STARFISH, STINGRAY, LOBSTER), **id** : int |

#### Other Elements

- None  

### **summary_screen**

(code=3050) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| levelPoints | int | Summarizes points the participant earned during the level; never negative to protect feelings. Since this can never go below 0, may be different from LevelRealPoints | |
| levelRealPoints | int | Summarizes points the participant earned during the level; can be negative | |
| maxLevelPoints | int | Maximum points it would have been possible to earn | |
| numStars | int | Number of stars displayed after completing the level; depends on percentage | |

#### Other Elements

- None  

### **leaderboard_shown**

(code=3051) TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| totalPoints | ?int? | Total points displayed to participant (?) | |
| totalRealPoints | ?int? | Total points actually earned by participant (?) | |
| classPoints | ?int? | Total points earned by the class (i.e., same access code) | |
| highestClassPoints | ?int? | Highest point value earned by any class (in a Dream table, EF Leaderboard) | |

#### Other Elements

- None  

### **leaderboard_closed**

TODO

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

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.  

level_range : range(0, 3)

No changelog prepared

