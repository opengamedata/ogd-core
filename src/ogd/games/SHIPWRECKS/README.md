# Game: SHIPWRECKS

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

**event_name** : *str* - event_name, The name of the event  
**event_params** : *json* - event_params, A repeated record of the parameters associated with this event  
**device** : *json* - device, A record of device information  
**geo** : *json* - geo, A record of the user's geographic information  
**platform** : *str* - platform, The platform on which the app was built  
**timestamp** : *datetime* - timestamp, Datetime when event was logged  
**app_version** : *str* - app_version, The version of the application (game) that generated the data  
**log_version** : *int* - log_version, The version of the logging code that generated the data  
**session_id** : *int* - session_id, ID for the play session  
**fd_user_id** : *str* - fd_user_id, The player's generated user code  

## Event Object Elements

The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.

**session_id** = Column '*session_id*' (index 8)  
**app_id** = null  
**timestamp** = Column '*timestamp*' (index 5)  
**event_name** = Column '*event_name*' (index 0)  
**event_data** = Column '*event_params*' (index 1)  
**event_source** = null  
**app_version** = Column '*app_version*' (index 6)  
**app_branch** = null  
**log_version** = Column '*log_version*' (index 7)  
**time_offset** = null  
**user_id** = Column '*fd_user_id*' (index 9)  
**user_data** = null  
**game_state** = null  
**event_sequence_index** = null  



## Logged Events  

The individual fields encoded in the *event_data* Event element for each type of event logged by the game.  

### **start_mission**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **checkpoint**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |
| status | N/A | Checkpoint status | |

#### Other Elements

- None  

### **open_map**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **scanning**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **scan_complete**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **dive_begin**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **new_evidence**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |
| type | N/A | Type of evidence found | |
| source | N/A | Source where the evidence was gathered from | |
| key | N/A | Name/ID for the evidence found | |

#### Other Elements

- None  

### **mission_complete**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **update_ship_overview**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |
| field | N/A | Field in ship overview that was updated | |
| evidence | N/A | Evidence placed in ship overview | |

#### Other Elements

- None  

### **view_desk**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |

#### Other Elements

- None  

### **view_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |
| tab_name | N/A | Name of tab opened | |

#### Other Elements

- None  

### **view_chat**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mission_id | N/A | ID for the current mission | |
| name | N/A | Name of NPC in the chat | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**ActiveJobs** : **, *Aggregate feature*   
Count of players who left off on each mission.  
  

**EventList** : **, *Aggregate feature*   
List of all events in a session  
  

**JobsCompleted** : **, *Aggregate feature*   
List of missions completed in a session  
  

**PlayerSummary** : **, *Aggregate feature*   
Summary of player statistics (active session time, jobs completed, number of sessions)  
  

**PopulationSummary** : **, *Aggregate feature*   
Summary of population statistics (active session time, average jobs completed count, average session count)  
  

**EvidenceBoardCompleteCount** : **, *Aggregate feature*  (disabled)  
Evidence board completes in a session  
  

**SessionDuration** : **, *Aggregate feature*   
Time spent playing in a given session  
  

**SessionID** : **, *Aggregate feature*   
The player's session ID number for this play session  
  

**TopJobCompletionDestinations** : **, *Aggregate feature*   
Top accepted missions after previously completing a given mission  
  

**TopJobSwitchDestinations** : **, *Aggregate feature*   
Top accepted missions after leaving a given mission  
  

**TotalDiveTime** : **, *Aggregate feature*  (disabled)  
Total time spent diving in a session  
  

**MissionDiveTime** : **, *Per-count feature*  (disabled)  
Time spent diving for a given mission  
  

**MissionSonarTimeToComplete** : **, *Per-count feature*  (disabled)  
Time taken to complete sonar scan for a given mission  
  

**JobsAttempted** : **, *Per-count feature*   
Subfeatures for number of mission starts and completes, percent complete, and avg/std time to complete  
*Sub-features*:  

- **job-name** : *string*, String name for a mission  

- **num-starts** : *int*, Number of mission_start events for a given mission  

- **num-completes** : *int*, Number of mission_complete events for a given mission  

- **percent-complete** : *float*, Percent of mission which were accepted and completed  

- **avg-time-complete** : *float*, Average time taken from accepting to completing a mission  

- **std-dev-complete** : *float*, Standard deviation of time taken to complete  


No changelog prepared

