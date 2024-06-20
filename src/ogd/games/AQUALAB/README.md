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

The individual fields encoded in the *game_state* and *user_data* Event element for all event types, and the fields in the *event_data* Event element for each individual event type logged by the game.  

### Enums  

| **Name** | **Values** |
| ---      | ---        |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| job_name | str | The name of the current job | |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **accept_job**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **switch_job**

Event that occurs whenever the job switches, whether manually or through an `accept_job` or `complete_job`

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| prev_job_name | str | String name of the previous job, may be incorrect when coinciding with any `complete_job`, or with an `accept_job` at a time the user was actively in a job. | |  

### **receive_fact**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| fact_entity | str | The entity (e.g. species) with which the fact is associated | |
| fact_id | str | Unique ID for the given fact | |
| fact_rate | bool | Whether the fact is a... rate fact? I don't really get this one... | |
| fact_stressed | bool |  | |
| fact_type | str | The type of fact | |
| has_rate | bool | Whether the fact... has a rate? We need better naming of things I guess... | |  

### **receive_entity**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| entity_id | str | Unique ID for the given entity | |  

### **complete_job**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| job_name | str | String name of the completed job | |  

### **complete_task**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| task_id | str | ID of the completed task | |  

### **scene_changed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| scene_name | str | Name of the loaded scene | |  

### **room_changed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| room_name | str | Name of the room being entered | |  

### **begin_dive**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| site_id | str | ID of the dive site | |  

### **ask_for_help**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| node_id | str | Scripting ID for the hint response | |  

### **guide_script_triggered**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| node_id | str | Scripting ID for the guide's response | |  

### **script_fired**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| node_id | str | ID of a given script node | |  

### **open_bestiary**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **bestiary_open_species_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **bestiary_open_environments_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **bestiary_open_models_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **bestiary_select_species**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| species_id | str | ID of the selected species | |  

### **bestiary_select_environment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| environment_id | str | ID of the selected environment | |  

### **bestiary_select_model**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| model_id | str | ID of the selected model | |  

### **close_bestiary**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **open_status**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **status_open_job_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **status_open_item_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **status_open_tech_tab**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **close_status**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **begin_model**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **model_phase_changed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| phase | str | The selected modeling phase | |  

### **model_ecosystem_selected**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **model_concept_started**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **model_concept_updated**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |
| status | str | Updated status of the concept model | |  

### **model_concept_exported**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **begin_simulation**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **model_sync_error**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |
| sync | int | Sync % achieved with the current model | |  

### **simulation_sync_achieved**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **model_predict_completed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **model_intervene_update**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |
| organism | str | The organism having its population modified by the player | |
| difference_value | None | The population change for the selected organism | |  

### **model_intervene_error**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **model_intervene_completed**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| ecosystem | str | Ecosystem selected for modeling | |  

### **end_model**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| phase | str | The selected modeling phase upon leaving | |
| ecosystem | str | The selected ecosystem upon leaving | |  

### **purchase_upgrade**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| item_id | str | ID of the purchased item | |
| item_name | str | String name of the purchased item | |
| cost | None | Cost of the purchased item | |  

### **insufficient_funds**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| item_id | str | ID of the item | |
| item_name | str | String name of the item | |
| cost | None | Cost of the item | |  

### **talk_to_shopkeep**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **add_environment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Name of the added environment | |  

### **remove_environment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Name of the removed environment | |  

### **add_critter**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critter | str | Name of the critter added to the tank | |  

### **remove_critter**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critter | str | Name of the critter removed from the tank | |  

### **begin_experiment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critters | str | Comma separated list of all critters added to the tank | |  

### **end_experiment**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tank_type | str | Selected tank type for the experiment | |
| environment | str | Selected environment for the experiment | |
| critters | str | Comma separated list of all critters added to the tank | |  

### **begin_argument**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **fact_submitted**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| fact_id | str | ID of the submitted fact | |  

### **fact_rejected**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| fact_id | str | ID of the rejected fact | |  

### **leave_argument**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **complete_argument**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

**CollectFactNoJob** : *Detector*  (disabled)  
Triggers an event when a player collects a fact while not actively working on a job  
  

**DiveSiteNoEvidence** : *Detector*  (disabled)  
Triggers an event when a player has gone sufficiently long at a dive site without uncovering new evidence  
*Other elements*:  

threshold : 30  

**EchoRoomChange** : *Detector*  (disabled)  
Triggers an event when a player changes rooms.  
  

**HintAndLeave** : *Detector*  (disabled)  
  
*Other elements*:  

threshold : 30  

**Idle** : *Detector*  (disabled)  
  
*Other elements*:  

idle_level : 30  

**SceneChangeFrequently** : *Detector*  (disabled)  
  
*Other elements*:  

threshold : 30  

**TwoHints** : *Detector*  (disabled)  
  
*Other elements*:  

threshold : 30  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**ActiveJobs** : *dict*, *Aggregate feature*   
Count of players who left off on each job.  
  

**AppVersions** : *list*, *Aggregate feature*   
List of all app versions encountered.  
  

**ActiveTime** : *timedelta*, *Aggregate feature*  (disabled)  
Total time spent actively playing  
  

**EventList** : *list*, *Aggregate feature*  (disabled)  
List of key events that happened in a player's session(s)  
  

**JobsCompleted** : *list[str]*, *Aggregate feature*   
List of completed jobs for a player  
  

**PlayerSummary** : *dict*, *Aggregate feature*  (disabled)  
Summary of player statistics (active session time, jobs completed, number of sessions)  
  

**PlayLocations** : *List[bool]*, *Aggregate feature*  (disabled)  
An indicator of whether play happened during normal school hours or not  
*Sub-features*:  

- **LocalTime** : *datetime*, The actual local time when each session started  
  

**PopulationSummary** : *dict*, *Aggregate feature*  (disabled)  
Summary of population statistics (active session time, average jobs completed count, average session count)  
  

**SessionDiveSitesCount** : *int*, *Aggregate feature*   
Time spent playing in a given session  
  

**SessionDuration** : *timedelta*, *Aggregate feature*   
Time spent playing in a given session  
*Other elements*:  

threshold : 60  

**SessionID** : *str*, *Aggregate feature*  (disabled)  
The player's session ID number for this play session  
  

**SwitchJobsCount** : *int*, *Aggregate feature*   
Number of times player switched jobs before completion  
  

**TopJobCompletionDestinations** : *str*, *Aggregate feature*  (disabled)  
Top five most accepted jobs after previously completing a given job  
  

**TopJobSwitchDestinations** : *str*, *Aggregate feature*  (disabled)  
Top five most accepted jobs after switching away from a given job  
  

**TotalArgumentationTime** : *timedelta*, *Aggregate feature*   
Total time spent in argumentation  
  

**TotalDiveTime** : *timedelta*, *Aggregate feature*   
Total time spent in dive sites  
  

**TotalExperimentationTime** : *timedelta*, *Aggregate feature*   
Total time spent in experimentation  
  

**TotalModelingTime** : *timedelta*, *Aggregate feature*   
Total time spent in modeling  
  

**TotalGuideCount** : *int*, *Aggregate feature*   
Number of times player talked with the guide throughout the session  
  

**TotalHelpCount** : *int*, *Aggregate feature*   
Number of times player clicked the help button throughout the session  
  

**TotalPlayTime** : *timedelta*, *Aggregate feature*   
Total time the player had the game open, based on sum total of SessionDurations.  
  

**UserAvgSessionDuration** : *float*, *Aggregate feature*   
Average session duration for a user.  
  

**UserTotalSessionDuration** : *timedelta*, *Aggregate feature*   
Total duration of all sessions for a user.  
  

**JobActiveTime** : *timedelta*, *Per-count feature*   
Time spent with job as the active job  
  

**JobArgumentation** : *timedelta*, *Per-count feature*   
Number of times the player entered the argumentation mechanic during a job  
*Sub-features*:  

- **Time** : *timedelta*, Time spent in argumentation during a job  
  

**JobCompletionTime** : *timedelta*, *Per-count feature*   
Time taken to complete a given job  
  

**JobDiveSitesCount** : *int*, *Per-count feature*   
Number of dive sites visited during a job  
  

**JobDiveTime** : *timedelta*, *Per-count feature*   
Time spent diving during a job  
  

**JobExperimentation** : *timedelta*, *Per-count feature*   
Number of times the player entered the experimentation mechanic during a job  
*Sub-features*:  

- **Time** : *timedelta*, Time spent in experimentation during a job  
  

**JobGuideCount** : *int*, *Per-count feature*  (disabled)  
Number of times player talked with guide during a job  
  

**JobHelpCount** : *int*, *Per-count feature*  (disabled)  
Number of times player asked for help during a job  
*Sub-features*:  

- **ByTask** : *int*, Help counts leading up to each completed task  
  

**JobLocationChanges** : *int*, *Per-count feature*  (disabled)  
Number of times player changed scenes or rooms  
*Sub-features*:  

- **ByTask** : *int*, Change counts leading up to each completed task  
  

**JobModeling** : *timedelta*, *Per-count feature*   
Number of times the player entered the modeling mechanic during a job  
*Sub-features*:  

- **Time** : *timedelta*, Time spent in modeling during a job  
  

**JobPriorComplete** : *list*, *Per-count feature*   
  
  

**JobPriorAttempt** : *list*, *Per-count feature*   
  
  

**JobTasksCompleted** : *int*, *Per-count feature*   
Number of tasks completed for a given job  
  

**JobsAttempted** : **, *Per-count feature*  (disabled)  
Subfeatures for number of job starts and completes, percent complete, and avg/std time to complete  
*Sub-features*:  

- **job-name** : *string*, String name for a job  

- **num-starts** : *int*, Number of accept_job events for a given job id  

- **num-completes** : *int*, Number of complete_job events for a given job id  

- **percent-complete** : *float*, Percent of jobs which were accepted and completed  

- **avg-time-per-attempt** : *float*, Average time taken from accepting to completing/leaving a job  

- **std-dev-per-attempt** : *float*, Standard deviation of time taken on a job  

- **job-difficulties** : *dict*, Difficulty of experimentation, modeling, and argumentation phases in the job  
  

**RegionJobCount** : *int*, *Per-count feature*   
The number of jobs completed in a given region  
  

**RegionName** : *str*, *Per-count feature*   
The human-readable version of the name for a given region  
  

**SyncCompletionTime** : *timedelta*, *Per-count feature*   
Time taken to achieve 100% sync in a simulation  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.  

level_range : range(0, 56)  

task_range : range(0, 235)

No changelog prepared

