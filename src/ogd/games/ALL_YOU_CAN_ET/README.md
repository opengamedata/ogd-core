# Game: ALL_YOU_CAN_ET

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

(code=1001), Generally not exported by Al

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| gameName | str | TODO | |

#### Other Elements

- None  

### **gamescribe_created**

(code=1002), Generally not exported by Al

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| gamescribeMode | enum(trace, strict) | trace or strict (trace is for debug, strict for production) | |

#### Other Elements

- None  

### **settings**

(code=2001), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| itemID | int | TODO | |
| playTime | ?int? | Amount of active play time research intended for players, as set in DREAM. Not counting instruction screens. | |

#### Other Elements

- None  

### **survey_graphics_version**

(code=2050), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| difficulty | str | i.e. 1.0 | |
| nextLevelAdaptable | str | i.e. 2.2 | |

#### Other Elements

- None  

### **main_menu_shown**

(code=3001), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **level_menu_shown**

(code=3002), This will never be jotted for Fall 2018, because we're not using the level menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| passedLevel | bool | Binary - did they complete the level or not? | |
| highestPanelUnlocked | ?int? | This refers to the highest panel unlocked. The game organizes progess in levels and panels (i.e., dots at the bottom), with up to 20 (?) levels per panel.  | |
| highestLevelUnlocked | ?int? | This shows the highest level unlocked. The game organizes progess in levels and panels, with up to 20 (?) levels per panel.  | |

#### Other Elements

- None  

### **level_start**

(code=3003), Called once the level starts, tutorial not included

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **tutorial_start**

(code=3004), gameTime for when the instructions began

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **change_of_rule**

(code=3005), Jots when exactly the new instruction screen comes up

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| waveType | str | Rule that will apply in the following wave | |
| ruleOnScreen | str | Specific rule being shown on the screen (could be the basic rule, radiation, or black hole) | |

#### Other Elements

- None  

### **wave_start**

(code=3006), Called every time a new wave of aliens starts (could be at the beginning of the level or after a rule change)

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| waveType | str | Rule for the aliens during that jot. Color scheme is off, Red = orange, Blue = green aliens.  | |

#### Other Elements

- None  

### **starting_food**

(code=3007), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| activeFood | enum(FOOD, DRINK) | The food item active at the start of that level. Randomly assigned. | |

#### Other Elements

- None  

### **alien_spawn**

(code=3008), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | int | Number representing the order in which the alien appeared, ranges from (1 - a number determined by level designer). | |
| posX | int | X position where alien was spawned, 0,0 is lower left corner | |
| posY | int | Y position where alien was spawned, 0,0 is lower left corner. This will be (almost) the same for all aliens. Aliens are spawned above the visible window, but the timing of the jot means the exact y position varies a little. | |
| difficulty | int | Speed difficulty at that moment (Number from 0 to 14) | |

#### Other Elements

- None  

### **alien_info**

(code=3009), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | int | Count of alien, represents order of appearance  | |
| alienType | int | Eye count of alien as identified by alienID | |
| alienColor | enum(red, blue) | Eye (red/blue) of alien as identified by alienID | |
| desiredFood | enum(FOOD, DRINK, BOTH) | Whether the alien requires the food or drink during that level | |
| waveType | str | Rule that applies when alien is on screen. Color scheme is off, Red = orange, Blue = green aliens.  | |

#### Other Elements

- None  

### **summary_screen**

(code=3050), TODO

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

(code=3051), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| totalPoints | int | Total points displayed to participant (?) | |
| totalRealPoints | int | Total points actually earned by participant (?) | |
| classPoints | int | Total points earned by the class (i.e., same access code) | |
| highestClassPoints | int | Highest point value earned by any class (in a Dream table, EF Leaderboard) | |

#### Other Elements

- None  

### **survey_shown**

(code=3052), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| surveyType | str | Name of the survey (i.e. Difficulty, NextLevelAdaptable) | |

#### Other Elements

- None  

### **food_switch**

(code=4001), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| previousFood | enum(FOOD, DRINK) | TODO | |
| currentFood | enum(FOOD, DRINK) | TODO | |

#### Other Elements

- None  

### **alien_shot**

(code=4002), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | int | Count of alien, represents order of appearance. | |
| foodShot | enum(FOOD, DRINK) | Item player shot | |
| foodNeeded | enum(FOOD, DRINK, BOTH) | Item the rules identified as correct for that alien | |

#### Other Elements

- None  

### **alien_hit_type_speed**

(code=4003), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | int | Count of alien, represents order of appearance  | |
| alienType | str | Eye count of alien as identified by alienID | |
| alienColor | enum(red, blue) | Eye color (red/blue) of alien as identified by alienID | |
| hitType | enum(HIT, SHOT, WRONG, MISSED) | Label for HIT, WRONG, MISSED if food is correct, wrong, or missed | |
| speed | int | Fall speed in pixels per second | |

#### Other Elements

- None  

### **alien_hit_reaction_times**

(code=4004), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | int | Count of alien, represents order of appearance  | |
| reactionTime | float | Time between when the first pixel of the alien appears onscreen, vs when the player shoots | |
| eyeReactionTime | float | Time between when the first pixel of the alien's eyes appear onscreen, vs when the player shoots | |
| afterHighlightedReactionTime | float | Time between when the alien was highlighted by the player, vs when the player shoots | |

#### Other Elements

- None  

### **alien_hit_pos_time**

(code=4005), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | int | Count of alien, represents order of appearance  | |
| posX | int | X position where alien was hit, 0,0 is lower left corner | |
| posY | int | Y position where alien was hit, 0,0 is lower left corner. This will be the same for all aliens. | |
| oldReactionTime | float | Time between when top of alien was an alien's length onscreen, and when it was hit by a food object | |

#### Other Elements

- None  

### **alien_hit_score**

(code=4006), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alienID | str | Count of alien, represents order of appearance  | |
| score | int | Points received for that alien | |
| difficulty | int | Speed difficulty at that moment (Number from 0 to 14) | |
| changeInDifficulty | enum(Initial, Decrease, Same, Increase, Final) | (INITIAL, DECREASE, SAME, INCREASE, FINAL) | |

#### Other Elements

- None  

### **leaderboard_closed**

(code=4050), As soon as they closed the leaderboard

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **survey_option_selection**

(code=4051), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| surveyType | str | Name of the survey (i.e. Difficulty, NextLevelAdaptable) | |
| optionSelected | int | ID defining the selected option (1, 2, 3, 4, 5) | |
| optionText | str | The actual text content of the survey item selected | |

#### Other Elements

- None  

### **survey_submission**

(code=4052), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| surveyType | str | Name of the survey (i.e. Difficulty, NextLevelAdaptable) | |
| optionSubmitted | int | ID defining the submitted option (1, 2, 3, 4, 5) | |
| optionText | str | The actual text content of the survey item selected | |

#### Other Elements

- None  

### **micro_adaptation**

(code=5001), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| difficulty | int | Speed difficulty after the micro adaptation happens (Number from 0 to 14) | |
| changeInDifficulty | enum(Initial, Decrease, Same, Increase, Final) | (Initial, Decrease, Same, Increase, Final) | |

#### Other Elements

- None  

### **macro_adaptation**

(code=5050), TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| difficulty | enum(Easy, Normal, Hard) | TODO | |
| changeInDifficulty | enum(Decrease, Same, Increase, Replay) | TODO | |
| averageScore | int | Score in a scale from 0 to 100 | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

None

No changelog prepared

