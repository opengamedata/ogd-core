# Game: AQUALAB

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

### **accept_job**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **switch_job**

Event that occurs whenever the job switches, whether manually or through an `accept_job` or `complete_job`

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| prev_job_name | str | String name of the previous job, may be incorrect when coinciding with any `complete_job`, or with an `accept_job` at a time the user was actively in a job. | |

#### Other Elements

- None  

### **receive_fact**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| fact_entity | str | The entity (e.g. species) with which the fact is associated | |
| fact_id | str | Unique ID for the given fact | |
| fact_rate | bool | Whether the fact is a... rate fact? I don't really get this one... | |
| fact_stressed | bool |  | |
| fact_type | str | The type of fact | |
| has_rate | bool | Whether the fact... has a rate? We need better naming of things I guess... | |

#### Other Elements

- None  

### **receive_entity**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| entity_id | str | Unique ID for the given entity | |

#### Other Elements

- None  

### **complete_job**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| job_name | str | String name of the completed job | |

#### Other Elements

- None  

### **complete_task**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| task_id | str | ID of the completed task | |

#### Other Elements

- None  

### **scene_changed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| scene_name | str | Name of the loaded scene | |

#### Other Elements

- None  

### **room_changed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| room_name | str | Name of the room being entered | |

#### Other Elements

- None  

### **begin_dive**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| site_id | str | ID of the dive site | |

#### Other Elements

- None  

### **ask_for_help**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| node_id | str | Scripting ID for the hint response | |

#### Other Elements

- None  

### **guide_script_triggered**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| node_id | str | Scripting ID for the guide's response | |

#### Other Elements

- None  

### **script_fired**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| node_id | str | ID of a given script node | |

#### Other Elements

- None  

### **open_bestiary**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **bestiary_open_species_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **bestiary_open_environments_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **bestiary_open_models_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **bestiary_select_species**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| species_id | str | ID of the selected species | |

#### Other Elements

- None  

### **bestiary_select_environment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| environment_id | str | ID of the selected environment | |

#### Other Elements

- None  

### **bestiary_select_model**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| model_id | str | ID of the selected model | |

#### Other Elements

- None  

### **close_bestiary**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **open_status**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **status_open_job_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **status_open_item_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **status_open_tech_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **close_status**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **begin_model**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **model_phase_changed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| phase | str | The selected modeling phase | |

#### Other Elements

- None  

### **model_ecosystem_selected**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **model_concept_started**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **model_concept_updated**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |
| status | str | Updated status of the concept model | |

#### Other Elements

- None  

### **model_concept_exported**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **begin_simulation**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **model_sync_error**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |
| sync | int | Sync % achieved with the current model | |

#### Other Elements

- None  

### **simulation_sync_achieved**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **model_predict_completed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **model_intervene_update**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |
| organism | str | The organism having its population modified by the player | |
| difference_value | None | The population change for the selected organism | |

#### Other Elements

- None  

### **model_intervene_error**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **model_intervene_completed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |

#### Other Elements

- None  

### **end_model**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| phase | str | The selected modeling phase upon leaving | |
| ecosystem | str | The selected ecosystem upon leaving | |

#### Other Elements

- None  

### **purchase_upgrade**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| item_id | str | ID of the purchased item | |
| item_name | str | String name of the purchased item | |
| cost | None | Cost of the purchased item | |

#### Other Elements

- None  

### **insufficient_funds**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| item_id | str | ID of the item | |
| item_name | str | String name of the item | |
| cost | None | Cost of the item | |

#### Other Elements

- None  

### **talk_to_shopkeep**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **add_environment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Name of the added environment | |

#### Other Elements

- None  

### **remove_environment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Name of the removed environment | |

#### Other Elements

- None  

### **add_critter**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critter | str | Name of the critter added to the tank | |

#### Other Elements

- None  

### **remove_critter**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critter | str | Name of the critter removed from the tank | |

#### Other Elements

- None  

### **begin_experiment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critters | str | Comma separated list of all critters added to the tank | |

#### Other Elements

- None  

### **end_experiment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critters | str | Comma separated list of all critters added to the tank | |

#### Other Elements

- None  

### **begin_argument**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **fact_submitted**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| fact_id | str | ID of the submitted fact | |

#### Other Elements

- None  

### **fact_rejected**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |
| fact_id | str | ID of the rejected fact | |

#### Other Elements

- None  

### **leave_argument**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **complete_argument**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Details** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

**CollectFactNoJob** : *Detector*   
Triggers an event when a player collects a fact while not actively working on a job  
  

**DiveSiteNoEvidence** : *Detector*   
Triggers an event when a player has gone sufficiently long at a dive site without uncovering new evidence  
*Other elements*:  

threshold - 30  

**EchoRoomChange** : *Detector*  (disabled)  
Triggers an event when a player changes rooms.  
  

**HintAndLeave** : *Detector*   
  
*Other elements*:  

threshold - 30  

**Idle** : *Detector*   
  
*Other elements*:  

idle_level - 30  

**SceneChangeFrequently** : *Detector*   
  
*Other elements*:  

threshold - 30  

**TwoHints** : *Detector*   
  
*Other elements*:  

threshold - 30  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**ActiveJobs** : *dict*, *Aggregate feature*  (disabled)  
Count of players who left off on each job.  
  

**ActiveTime** : *timedelta*, *Aggregate feature*   
No Description  
  

**EventList** : *list*, *Aggregate feature*  (disabled)  
List of key events that happened in a player's session(s)  
  

**JobsCompleted** : *list[str]*, *Aggregate feature*   
List of completed jobs for a player  
  

**PlayerSummary** : *dict*, *Aggregate feature*  (disabled)  
Summary of player statistics (active session time, jobs completed, number of sessions)  
  

**PopulationSummary** : *dict*, *Aggregate feature*  (disabled)  
Summary of population statistics (active session time, average jobs completed count, average session count)  
  

**SessionDiveSitesCount** : *int*, *Aggregate feature*   
Time spent playing in a given session  
  

**SessionDuration** : *timedelta*, *Aggregate feature*   
Time spent playing in a given session  
  

**SessionGuideCount** : *int*, *Aggregate feature*   
Number of times player talked with the guide throughout the session  
  

**SessionHelpCount** : *int*, *Aggregate feature*   
Number of times player clicked the help button throughout the session  
  

**SessionID** : *str*, *Aggregate feature*   
The player's session ID number for this play session  
  

**SessionJobsCompleted** : *int*, *Aggregate feature*   
Number of jobs completed in a given session  
  

**SwitchJobsCount** : *int*, *Aggregate feature*   
Number of times player switched jobs before completion  
  

**TopJobCompletionDestinations** : *str*, *Aggregate feature*   
Top five most accepted jobs after previously completing a given job  
  

**TopJobSwitchDestinations** : *str*, *Aggregate feature*   
Top five most accepted jobs after switching away from a given job  
  

**TotalArgumentationTime** : *timedelta*, *Aggregate feature*   
Total time spent in argumentation  
  

**EchoSessionID** : *str*, *Aggregate feature*  (disabled)  
Test of second-order features.  
  

**TotalDiveTime** : *timedelta*, *Aggregate feature*   
Total time spent in dive sites  
  

**TotalExperimentationTime** : *timedelta*, *Aggregate feature*   
Total time spent in experimentation  
  

**UserAvgSessionDuration** : *float*, *Aggregate feature*   
Average session duration for a user.  
  

**UserTotalSessionDuration** : *timedelta*, *Aggregate feature*   
Total duration of all sessions for a user.  
  

**JobActiveTime** : *timedelta*, *Per-count feature*   
Time spent with job as the active job  
  

**JobArgumentationTime** : *timedelta*, *Per-count feature*   
Time spent in argumentation during a job  
  

**JobCompletionTime** : *timedelta*, *Per-count feature*   
Time taken to complete a given job  
  

**JobDiveSitesCount** : *int*, *Per-count feature*   
Number of dive sites visited during a job  
  

**JobDiveTime** : *timedelta*, *Per-count feature*   
Time spent diving during a job  
  

**JobExperimentationTime** : *timedelta*, *Per-count feature*   
Time spent in experimentation during a job  
  

**JobModelingTime** : *timedelta*, *Per-count feature*   
Time spent in modeling during a job  
  

**JobGuideCount** : *int*, *Per-count feature*   
Number of times player talked with guide during a job  
  

**JobHelpCount** : *int*, *Per-count feature*   
Number of times player asked for help during a job  
*Sub-features*:  

- **ByTask** : *int*, Help counts leading up to each completed task  
  

**JobLocationChanges** : *int*, *Per-count feature*   
Number of times player changed scenes or rooms  
*Sub-features*:  

- **ByTask** : *int*, Change counts leading up to each completed task  
  

**JobTasksCompleted** : *int*, *Per-count feature*   
Number of tasks completed for a given job  
  

**JobsAttempted** : **, *Per-count feature*   
Subfeatures for number of job starts and completes, percent complete, and avg/std time to complete  
*Sub-features*:  

- **job-name** : *string*, String name for a job  

- **num-starts** : *int*, Number of accept_job events for a given job id  

- **num-completes** : *int*, Number of complete_job events for a given job id  

- **percent-complete** : *float*, Percent of jobs which were accepted and completed  

- **avg-time-per-attempt** : *float*, Average time taken from accepting to completing/leaving a job  

- **std-dev-per-attempt** : *float*, Standard deviation of time taken on a job  

- **job-difficulties** : *dict*, Difficulty of experimentation, modeling, and argumentation phases in the job  
  

**SyncCompletionTime** : *timedelta*, *Per-count feature*   
Time taken to achieve 100% sync in a simulation  


No changelog prepared

