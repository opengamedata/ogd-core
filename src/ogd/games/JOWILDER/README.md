# Game: JOWILDER

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

### **checkpoint**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **startgame**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| save_code | N/A |  |  | |
| fullscreen | N/A |  |  | |
| music | N/A |  |  | |
| hq | N/A |  |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **endgame**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **navigate_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **notebook_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| page | N/A |  |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **map_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **notification_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |
| text_fqid | N/A | c.fqid | Text fqid (v6+) | |
| text | N/A | c_text | Text  (v6+) | |

#### Other Elements

- None  

### **object_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **observation_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |
| text_fqid | N/A | obs_fqid | Text fqid (v6+) | |
| text | N/A | obs_text | Text  (v6+) | |

#### Other Elements

- None  

### **person_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |
| text_fqid | N/A | speak.fqid | Text fqid (v6+) | |
| text | N/A | speak_text | (v6+) | |

#### Other Elements

- None  

### **cutscene_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |
| text_fqid | N/A | cutscene.fqid | Text fqid (v6+) | |
| text | N/A | txt | Either cutscene text or 'undefined' (v6+) | |

#### Other Elements

- None  

### **wildcard_click**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| screen_coor | N/A | x,y integer array of where the mouse is in current room |  | |
| room_coor | N/A | x,y integer array of where the mouse is in the game screen |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |
| correct | N/A | correct answer to the problem (only exists for event name CHOICE) - sometimes doesn't exist?? | Only exists in versions 1-4. (v4-) | |
| answer | N/A | selected answer (only exists for event name CHOICE) | Only exists in versions 1-4. (v4-) | |
| cur_cmd_fqid | N/A | cmd_type == 1 ? cur_cmd.speak_fqid : wc.cur_command.entry_fqid | Only exists in versions 6+ (v6+) | |
| cur_cmd_type | N/A | cmd_type | Only exists in versions 6+ (v6+) | |
| text | N/A | cmd_txt | Only exists in versions 6+ (v6+) | |
| interacted_fqid | N/A | clicked_fqid | Only exists in versions 6+ (v6+) | |

#### Other Elements

- None  

### **navigate_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| start_time | N/A | client side timestamp for the time the hover started |  | |
| end_time | N/A | client side timestamp for the time the hover ended |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **notebook_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |

#### Other Elements

- None  

### **map_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| start_time | N/A | client side timestamp for the time the hover started |  | |
| end_time | N/A | client side timestamp for the time the hover ended |  | |
| name | N/A | event name |  | |
| level | N/A | enum for current checkpoint |  | |

#### Other Elements

- None  

### **notification_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |

#### Other Elements

- None  

### **object_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| start_time | N/A | client side timestamp for the time the hover started |  | |
| end_time | N/A | client side timestamp for the time the hover ended |  | |
| level | N/A | enum for current checkpoint |  | |
| name | N/A | event name - sometimes doesn't exist?? |  | |

#### Other Elements

- None  

### **observation_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |

#### Other Elements

- None  

### **person_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |

#### Other Elements

- None  

### **cutscene_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |

#### Other Elements

- None  

### **wildcard_hover**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| event Name | N/A | Description | Note | |
| room_fqid | N/A | fully qualified id of the room |  | |
| type | N/A | type name |  | |
| subtype | N/A | subtype name |  | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted |  | |
| event_custom | N/A | event enum |  | |
| start_time | N/A | client side timestamp for the time the hover started |  | |
| end_time | N/A | client side timestamp for the time the hover ended |  | |
| name | N/A | event name - sometimes doesn't exist?? |  | |
| level | N/A | enum for current checkpoint |  | |
| correct | N/A | correct answer to the problem (only exists for event name CHOICE) - sometimes doesn't exist?? | Only exists in versions 1-4. (v4-) | |
| answer | N/A | selected answer (only exists for event name CHOICE) | Only exists in versions 1-4. (v4-) | |
| cur_cmd_fqid | N/A | cmd_type == 1 ? cur_cmd.speak_fqid : wc.cur_command.entry_fqid | Only exists in versions 6+ (v6+) | |
| cur_cmd_type | N/A | cmd_type | Only exists in versions 6+ (v6+) | |
| text | N/A | cmd_txt | Only exists in versions 6+ (v6+) | |
| interacted_fqid | N/A | clicked_fqid | Only exists in versions 6+ (v6+) | |

#### Other Elements

- None  

### **quiz**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| room_fqid | N/A | fully qualified id of the room | |
| type | N/A | type enum | |
| subtype | N/A | subtype enum | |
| fqid | N/A | fqid of the interaction, with the room_fqid subtracted | |
| event_custom | N/A | event enum | |
| questions | N/A | array of question objects, each has question, response, and response_index | |
| name | N/A | event name enum | |
| level | N/A | enum for current checkpoint | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**Clicks** : *int*, *Aggregate feature*   
The number of clicks in a session  
*Sub-features*:  

- **AverageTimeBetween** : *float*, The average number of seconds between clicks  
  

**Hovers** : *int*, *Aggregate feature*   
The number of hovers in a session  
  

**SessionDuration** : *timedelta*, *Aggregate feature*   
The total time in a session  
  

**NotebookUses** : *int*, *Aggregate feature*   
The number of notebook uses in a session  
  

**EventCount** : *int*, *Aggregate feature*   
The number of events in a session  
  

**UserEnabled** : *int*, *Aggregate feature*   
A feature to show which options a user enabled; Base feature is 1 if user enabled fullscreen, otherwise 0.  
*Sub-features*:  

- **Music** : *int*, 1 if the user enabled music, otherwise 0  

- **HQGraphics** : *int*, 1 if the user enabled high-quality graphics, otherwise 0  
  

**GameVersion** : *str*, *Aggregate feature*   
A feature to show which version of the game the player played.  
*Sub-features*:  

- **Log** : *str*, The log version of the game the player played  
  

**UsedSaveCode** : *str*, *Aggregate feature*   
A feature to show which save code, if any, a player used as a starting point for their game.  
  

**GameScript** : *str*, *Aggregate feature*   
A feature to show which version of the script the player saw.  
*Sub-features*:  

- **Version** : *int*, Version of the game script the player saw.  
  

**SessionStart** : *date*, *Aggregate feature*   
A feature to record the date and time on which the gameplay session started.  
*Sub-features*:  

- **Time** : *time*, The time the player started their session  

- **Year** : *int*, The year the player started their session  

- **Month** : *int*, The month in which the player started their session  

- **Hour** : *int*, The hour during which the player started their session  
  

**IdleState15** : *timedelta*, *Aggregate feature*   
A feature to calculate total time spent idle in session; configured to define 'idle' as spending 15 seconds or more without making a 'meaningful' action  
*Sub-features*:  

- **Count** : *int*, The total number of times the player entered an idle state  
*Other elements*:  

IDLE_THRESH_SECONDS : 15  

**ActiveStateTime** : *timedelta*, *Aggregate feature*   
A feature to calculate the time spent actively playing the game.  
*Sub-features*:  

- **Clicking** : *timedelta*, No description  
*Other elements*:  

ACTIVE_THRESH_SECONDS : 15  

**MeaningfulActions** : *int*, *Aggregate feature*   
A feature to calculate the total number of 'meaningful' clicks in a session. That is, the number of navigation clicks on items/objects/people/portholes + number of clicks on map locations.  
  

**FirstInteraction** : *str*, *Aggregate feature*   
A feature to show which interaction a player had first within the game session.  
  

**LastInteraction** : *str*, *Aggregate feature*   
A feature to show which interaction a player had last within the game session.  
  

**UsedContinue** : *int*, *Aggregate feature*   
A feature to indicate whether the session began from the 'continue' button; i.e. whether this session continued from the ending savecode of another session.  
  

**QuestionAnswers** : *List[str]*, *Per-count feature*   
list the different answers that the player chose, by id#  
*Sub-features*:  

- **Count** : *int*, The total count of answers the player chose  
  

**SurveyItem** : *int*, *Per-count feature*   
Survey answer index for the given question  
*Sub-features*:  

- **Text** : *str*, The text associated with the given answer  

- **Time** : *timedelta*, No description  

- **ResponseChanges** : *int*, The number of times the player changed their answer before submitting  
  

**Interaction** : *timedelta*, *Per-count feature*   
The total time spent in this interaction, across all times having the interaction   
*Sub-features*:  

- **FirstEncounterTime** : *timedelta*, The time spent in this interaction the first time the player encountered it  

- **NumEncounter** : *int*, The number of times the player encountered the interaction  

- **TimeTo** : *timedelta*, The time it took the player to reach the interaction  
  

**SurveyTime** : *timedelta*, *Per-count feature*  (disabled)  
The total time spent on a survey screen.  
  

**InteractionName** : *str*, *Per-count feature*   
The fqid of the interaction  
*Sub-features*:  

- **BoxesCount** : *int*, The number of text boxes in the interaction  

- **WordsCount** : *int*, The number of words in the interaction  
  

**InteractionTextBoxesPerSecond** : *float*, *Per-count feature*   
A feature to calculate text-boxes-per-second in various interactions. It will include a subfeature for the first time the interaction was encountered.  
*Sub-features*:  

- **FirstEncounter** : *float*, The text-boxes-per-second the first time the player encountered the interaction.  

- **Variance** : *float*, No description  
  

**InteractionWordsPerSecond** : *float*, *Per-count feature*   
A feature to calculate words-per-second in various interactions. It will include a subfeature for the first time the interaction was encountered.  
*Sub-features*:  

- **FirstEncounter** : *float*, The words-per-second the first time the player encountered the interaction.  

- **Variance** : *float*, No description  


No changelog prepared

