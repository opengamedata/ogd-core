# Game: JOURNALISM

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

**session_id** : _str_ - session_id, Unique identifier for the gameplay session  
**user_id** : _str_ - user_id, Unique identifier for the player  
**user_data** : _json_ - user_data, Additional metadata about the player  
**client_time** : _datetime_ - client_time, The client machine time when the event was generated  
**client_offset** : _timedelta_ - client_offset, The time difference between local client time and GMT  
**server_time** : _datetime_ - server_time, The server machine time when the event was logged  
**event_name** : _str_ - event_name, The type of event logged  
**event_data** : _json_ - event_data, Data specific to an event type, encoded as a JSON string  
**event_source** : _enum('GAME', 'DETECTOR')_ - event_source, The generator of the event  
**game_state** : _json_ - game_state, Additional metadata about the state of the game when the event was logged  
**app_version** : _str_ - app_version, The version of the game from which the event came  
**app_branch** : _str_ - app_branch, The branch of the game code from which the event came  
**log_version** : _int_ - log_version, The version of the logging code from which the event came  
**event_sequence_index** : _int_ - event_sequence_index, Counter of events in the session, from 0. A row with session_n = i is the (i+1)-th event of the session  
**remote_addr** : _str_ - remote_addr, The IP address for the player's computer  
**http_user_agent** : _str_ - http_user_agent, Data on the type of web browser, OS, etc. in use by the player

## Event Object Elements

The elements (member variables) of each Event object, available to programmers when writing feature extractors. The right-hand side shows which database column(s) are mapped to a given element.

**session_id** = Column '_session_id_' (index 0)  
**app_id** = null  
**timestamp** = Column '_client_time_' (index 3)  
**event_name** = Columns '_6_'  
**event_data** = Column '_{'event_data': 7, 'server_time': 5, 'http_user_agent': 15}_' (DEBUG: Type <class 'dict'>)  
**event_source** = null  
**app_version** = Column '_app_version_' (index 10)  
**app_branch** = Column '_app_branch_' (index 11)  
**log_version** = Column '_log_version_' (index 12)  
**time_offset** = Column '_client_offset_' (index 4)  
**user_id** = Column '_user_id_' (index 1)  
**user_data** = Column '_user_data_' (index 2)  
**game_state** = Column '_game_state_' (index 9)  
**event_sequence_index** = Column '_event_sequence_index_' (index 13)

## Logged Events

The individual fields encoded in the _event_data_ Event element for each type of event logged by the game.

### **new_game**

Player clicked to start a new game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **continue_game**

Player clicked to continue a game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **text_click**

clicked to advance to the next text bubble

#### Event Data

| **Name**     | **Type** | **Description**                                             | **Sub-Elements** |
| ------------ | -------- | ----------------------------------------------------------- | ---------------- |
| node_id      | str      | the node id containing the text                             |                  |
| text_content | str      | the actual text content of the bubble                       |                  |
| speaker      | str      | the speaker_id of the character/entity who 'spoke' the text |                  |

#### Other Elements

- None

### **display_text_dialog**

a new dialog text bubble is displayed on the screen

#### Event Data

| **Name**     | **Type** | **Description**                                             | **Sub-Elements** |
| ------------ | -------- | ----------------------------------------------------------- | ---------------- |
| node_id      | str      | the node id containing the text                             |                  |
| text_content | str      | the actual text content of the bubble                       |                  |
| speaker      | str      | the speaker_id of the character/entity who 'spoke' the text |                  |

#### Other Elements

- None

### **display_breakdown_dialog**

during the editor review of a submitted story, the story composition/breakdown is displayed like a text bubble.

#### Event Data

| **Name**         | **Type** | **Description**                                              | **Sub-Elements**                                                        |
| ---------------- | -------- | ------------------------------------------------------------ | ----------------------------------------------------------------------- |
| final_breakdown  | Dict     | The color/fact/useful breakdown of the submitted story       | **color_weight** : int, **facts_weight** : int, **useful_weight** : int |
| target_breakdown | Dict     | The target color/fact/useful breakdown assigned to the story | **color_weight** : int, **facts_weight** : int, **useful_weight** : int |

#### Other Elements

- None

### **display_snippet_quality_dialog**

during the editor review of a submitted story, the story snippet qualities are displayed like a text bubble.

#### Event Data

| **Name**        | **Type**                     | **Description**                                                                                                            | **Sub-Elements** |
| --------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| current_quality | List[enum(BAD, GOOD, GREAT)] | The quality for each snippet used in the story, sorted by quality. Note that 'GOOD' quality is not displayed to the player |                  |

#### Other Elements

- None

### **display_feedback_dialog**

a new dialog text bubble is displayed on the screen during the editor's feedback on a submitted story

#### Event Data

| **Name**        | **Type** | **Description**                                                    | **Sub-Elements** |
| --------------- | -------- | ------------------------------------------------------------------ | ---------------- |
| node_id         | str      | the node id containing the text                                    |                  |
| text_content    | str      | the actual text content of the bubble                              |                  |
| story_score     | float    | calculated score based on overall quality                          |                  |
| story_alignment | float    | score based on how well the player followed the target composition |                  |

#### Other Elements

- None

### **display_choices**

Event for when a set of choices are displayed to the user.

#### Event Data

| **Name** | **Type**                         | **Description**                                                                              | **Sub-Elements** |
| -------- | -------------------------------- | -------------------------------------------------------------------------------------------- | ---------------- |
| context  | enum(CONVERSATION, LOCATION_MAP) | Whether the choices are being displayed in a normal conversation, or in front of a map image |                  |
| choices  | List                             | Unknown                                                                                      |                  |

#### Other Elements

- None

### **hub_choice_click**

clicked to choose a text option

#### Event Data

| **Name**             | **Type**      | **Description**                        | **Sub-Elements** |
| -------------------- | ------------- | -------------------------------------- | ---------------- |
| text_content         | str           | The text contents of the choice button |                  |
| node_id              | str           |                                        |                  |
| next_node_id         | str           |                                        |                  |
| next_location        | Optional[str] |                                        |                  |
| time_cost            | int           |                                        |                  |
| time_cost_is_mystery | bool          |                                        |                  |

#### Other Elements

- None

### **time_choice_click**

clicked to choose a text option

#### Event Data

| **Name**             | **Type** | **Description** | **Sub-Elements** |
| -------------------- | -------- | --------------- | ---------------- |
| text_content         | str      |                 |                  |
| current_node_id      | str      |                 |                  |
| next_node_id         | str      |                 |                  |
| time_cost            | int      |                 |                  |
| time_cost_is_mystery | bool     |                 |                  |

#### Other Elements

- None

### **location_choice_click**

clicked to choose a text option

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| text_content    | str      |                 |                  |
| current_node_id | str      |                 |                  |
| next_node_id    | str      |                 |                  |
| next_location   | str      |                 |                  |

#### Other Elements

- None

### **once_choice_click**

clicked to choose a text option

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| text_content    | str      |                 |                  |
| current_node_id | str      |                 |                  |
| next_node_id    | str      |                 |                  |

#### Other Elements

- None

### **continue_choice_click**

clicked to choose a text option

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| text_content    | str      |                 |                  |
| current_node_id | str      |                 |                  |

#### Other Elements

- None

### **action_choice_click**

clicked to choose a text option

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| text_content    | str      |                 |                  |
| current_node_id | str      |                 |                  |

#### Other Elements

- None

### **fallback_choice_click**

clicked to choose a text option

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| text_content    | str      |                 |                  |
| current_node_id | str      |                 |                  |
| next_node_id    | str      |                 |                  |

#### Other Elements

- None

### **open_stats_tab**

The event when player clicks to open the player stats tab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **close_stats_tab**

The event when player clicks to clsoe the player stats tab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **open_map_tab**

Event when the player opens their non-interactive map tab

#### Event Data

| **Name**         | **Type**  | **Description**                                                                  | **Sub-Elements** |
| ---------------- | --------- | -------------------------------------------------------------------------------- | ---------------- |
| current_location | str       | The player's currently-displayed location on the map                             |                  |
| locations_list   | List[str] | each string is a location ID for one of the locations currently shown on the map |                  |

#### Other Elements

- None

### **open_choice_map**

Event when the game displays a map during a choice dialog

#### Event Data

| **Name**         | **Type**  | **Description**                                                                  | **Sub-Elements** |
| ---------------- | --------- | -------------------------------------------------------------------------------- | ---------------- |
| current_location | str       | The player's currently-displayed location on the map                             |                  |
| locations_list   | List[str] | each string is a location ID for one of the locations currently shown on the map |                  |

#### Other Elements

- None

### **close_map_tab**

When the player closes their map tab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **open_impact_map**

When a player publishes the story, the impact map displays

#### Event Data

| **Name**       | **Type**  | **Description** | **Sub-Elements** |
| -------------- | --------- | --------------- | ---------------- |
| feeback_ids    | List[str] |                 |                  |
| feedback_texts | List[str] |                 |                  |

#### Other Elements

- None

### **close_impact_map**

Player clicks button to close the impact map.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **reached_checkpoint**

Event when player reaches a checkpoint

#### Event Data

| **Name** | **Type** | **Description**                                 | **Sub-Elements** |
| -------- | -------- | ----------------------------------------------- | ---------------- |
| node_id  | str      | The node ID from which the checkpoint was saved |                  |

#### Other Elements

- None

### **stat_update**

happens when a stat is updated

#### Event Data

| **Name** | **Type**                                                               | **Description**                          | **Sub-Elements** |
| -------- | ---------------------------------------------------------------------- | ---------------------------------------- | ---------------- |
| node_id  | str                                                                    | Node ID in which the stat update happens |                  |
| stats    | Dict[enum(ENDURANCE, RESOURCEFUL, TECH, SOCIAL, TRUST, RESEARCH), int] | Mapping of stat types to change amounts  |                  |

#### Other Elements

- None

### **change_background_image**

a change in the background image behind text

#### Event Data

| **Name**   | **Type** | **Description**                                   | **Sub-Elements** |
| ---------- | -------- | ------------------------------------------------- | ---------------- |
| node_id    | str      | The node in which the background image is changed |                  |
| image_name | str      | The image file's name without file extension.     |                  |

#### Other Elements

- None

### **show_popup_image**

a change in popup image next to text

#### Event Data

| **Name**    | **Type** | **Description**                                | **Sub-Elements** |
| ----------- | -------- | ---------------------------------------------- | ---------------- |
| is_animated | bool     | True if the image is animated, otherwise false |                  |
| node_id     | str      | The node in which the popup image is displayed |                  |
| image_name  | str      | The image file's name without file extension.  |                  |

#### Other Elements

- None

### **change_location**

a change in player location

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| new_location_id | str      |                 |                  |

#### Other Elements

- None

### **unlocked_notebook**

When the player unlocks the notebook early in the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **open_notebook**

When the player opens the notebook (not editor notes)

#### Event Data

| **Name**     | **Type**   | **Description**                                                                                                       | **Sub-Elements**                                                                                                                                                                               |
| ------------ | ---------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| snippet_list | List[Dict] | A list of snippet ids available on the left of the notebook                                                           | **snippet_id** : str, **snippet_type** : enum(IMAGE, QUOTE), **snippet_quality** : enum(BAD, GOOD, GREAT), **snippet_attributes** : List[enum(COLOR, FACTS, USEFUL)], **is_selectable** : bool |
| layout       | List[Dict] | A list whose elements are 'slots', each with a type and the id of the currently-assigned snippet, if one is assigned. | **type** : enum(ANY,PICTURE), **is_wide** : bool, **assigned_snippet** : Optional[snippet_id]                                                                                                  |

#### Other Elements

- None

### **select_snippet**

When a player selects a snippet in the notebook

#### Event Data

| **Name**           | **Type**                         | **Description**                                  | **Sub-Elements** |
| ------------------ | -------------------------------- | ------------------------------------------------ | ---------------- |
| snippet_id         | str                              |                                                  |                  |
| snippet_type       | enum(IMAGE, QUOTE)               | Whether the given snippet is an image or a quote |                  |
| snippet_quality    | enum(BAD, GOOD, GREAT)           | good, bad, great                                 |                  |
| snippet_attributes | List[enum(COLOR, FACTS, USEFUL)] |                                                  |                  |

#### Other Elements

- None

### **place_snippet**

When a player places a snippet into a spot on the story layout

#### Event Data

| **Name**          | **Type**               | **Description**                                                                                                       | **Sub-Elements**                                                                              |
| ----------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| layout            | List[Dict]             | A list whose elements are 'slots', each with a type and the id of the currently-assigned snippet, if one is assigned. | **type** : enum(ANY,PICTURE), **is_wide** : bool, **assigned_snippet** : Optional[snippet_id] |
| location          | int                    |                                                                                                                       |                                                                                               |
| snippet_id        | str                    | str                                                                                                                   |                                                                                               |
| snippet_type      | enum(IMAGE, QUOTE)     | image or quote                                                                                                        |                                                                                               |
| snippet_quality   | enum(BAD, GOOD, GREAT) | good, bad, great                                                                                                      |                                                                                               |
| snippet_attribute | List[]                 | color, facts, useful                                                                                                  |                                                                                               |

#### Other Elements

- None

### **remove_snippet**

When a player removes an item from the story layout

#### Event Data

| **Name**          | **Type**   | **Description**                                                                                                       | **Sub-Elements**                                                                              |
| ----------------- | ---------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| layout            | List[Dict] | A list whose elements are 'slots', each with a type and the id of the currently-assigned snippet, if one is assigned. | **type** : enum(ANY,PICTURE), **is_wide** : bool, **assigned_snippet** : Optional[snippet_id] |
| location          | int        |                                                                                                                       |                                                                                               |
| snippet_id        |            | str                                                                                                                   |                                                                                               |
| snippet_type      |            | image or quote                                                                                                        |                                                                                               |
| snippet_quality   |            | good, bad, great, lousy                                                                                               |                                                                                               |
| snippet_attribute |            | List[] made up of color, facts, useful                                                                                |                                                                                               |

#### Other Elements

- None

### **open_editor_note**

Event when user is in the notebook and clicks to open editor's notes

#### Event Data

| **Name**          | **Type**                     | **Description**                                                                                                            | **Sub-Elements**                                                        |
| ----------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| current_breakdown | Dict                         | The color/fact/useful breakdown of the current story                                                                       | **color_weight** : int, **facts_weight** : int, **useful_weight** : int |
| target_breakdown  | Dict                         | The target color/fact/useful breakdown assigned to the story                                                               | **color_weight** : int, **facts_weight** : int, **useful_weight** : int |
| current_quality   | List[enum(BAD, GOOD, GREAT)] | The quality for each snippet used in the story, sorted by quality. Note that 'GOOD' quality is not displayed to the player |                                                                         |

#### Other Elements

- None

### **close_editor_note**

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **close_notebook**

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **time_limit_assigned**

#### Event Data

| **Name** | **Type**  | **Description**                              | **Sub-Elements** |
| -------- | --------- | -------------------------------------------- | ---------------- |
| node_id  | str       | The node for which a time limit was assigned |                  |
| how_long | timedelta |                                              |                  |

#### Other Elements

- None

### **open_timer**

A player clicks to view the timer tab

#### Event Data

| **Name**  | **Type**  | **Description** | **Sub-Elements** |
| --------- | --------- | --------------- | ---------------- |
| time_left | timedelta |                 |                  |

#### Other Elements

- None

### **close_timer**

The player closes the timer tab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **time_elapsed**

#### Event Data

| **Name** | **Type** | **Description**                 | **Sub-Elements** |
| -------- | -------- | ------------------------------- | ---------------- |
| node_id  | str      |                                 |                  |
| how_much | int      | The amount of time that elapsed |                  |

#### Other Elements

- None

### **time_expired**

#### Event Data

| **Name**      | **Type** | **Description**                                                                                                          | **Sub-Elements** |
| ------------- | -------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| node_id       | str      |                                                                                                                          |                  |
| leftover_time | int      | If the player's time expired because remaining choices all are too long, this is the remaining time they would have had. |                  |

#### Other Elements

- None

### **snippet_received**

#### Event Data

| **Name**           | **Type**                         | **Description**                                  | **Sub-Elements** |
| ------------------ | -------------------------------- | ------------------------------------------------ | ---------------- |
| node_id            | str                              |                                                  |                  |
| snippet_id         | str                              |                                                  |                  |
| snippet_type       | enum(IMAGE, QUOTE)               | Whether the given snippet is an image or a quote |                  |
| snippet_quality    | enum(BAD, GOOD, GREAT)           | good, bad, great                                 |                  |
| snippet_attributes | List[enum(COLOR, FACTS, USEFUL)] |                                                  |                  |

#### Other Elements

- None

### **story_updated**

Event when a snippet is placed or removed, changing the current story

#### Event Data

| **Name**         | **Type**                     | **Description**                                                                                                            | **Sub-Elements**                                                        |
| ---------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| new_breakdown    | Dict                         | The color/fact/useful breakdown of the submitted story                                                                     | **color_weight** : int, **facts_weight** : int, **useful_weight** : int |
| target_breakdown | Dict                         | The target color/fact/useful breakdown assigned to the story                                                               | **color_weight** : int, **facts_weight** : int, **useful_weight** : int |
| new_quality      | List[enum(BAD, GOOD, GREAT)] | The quality for each snippet used in the story, sorted by quality. Note that 'GOOD' quality is not displayed to the player |                                                                         |
| story_score      | float                        | calculated score based on overall quality                                                                                  |                                                                         |
| story_alignment  | float                        | score based on how well the player followed the target composition                                                         |                                                                         |

#### Other Elements

- None

### **publish_story_click**

When a player clicks to submit the story for publishing

#### Event Data

| **Name**     | **Type**   | **Description**                                                                                                       | **Sub-Elements**                                                                                                                                                                               |
| ------------ | ---------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| snippet_list | List[Dict] | A list of snippet ids available on the left of the notebook                                                           | **snippet_id** : str, **snippet_type** : enum(IMAGE, QUOTE), **snippet_quality** : enum(BAD, GOOD, GREAT), **snippet_attributes** : List[enum(COLOR, FACTS, USEFUL)], **is_selectable** : bool |
| layout       | List[Dict] | A list whose elements are 'slots', each with a type and the id of the currently-assigned snippet, if one is assigned. | **type** : enum(ANY,PICTURE), **is_wide** : bool, **assigned_snippet** : Optional[snippet_id]                                                                                                  |

#### Other Elements

- None

### **display_published_story**

#### Event Data

| **Name**     | **Type**   | **Description**                                                                                                       | **Sub-Elements**                                                        |
| ------------ | ---------- | --------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| story_layout | List[Dict] | A list whose elements are 'slots', each with a type and the id of the currently-assigned snippet, if one is assigned. | **type** : enum(TEXT,PICTURE,EMPTY), **is_wide** : bool, **text** : str |

#### Other Elements

- None

### **close_published_story**

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| -------- | -------- | --------------- | ---------------- |

#### Other Elements

- None

### **start_level**

When a new level is started

#### Event Data

| **Name**      | **Type** | **Description** | **Sub-Elements** |
| ------------- | -------- | --------------- | ---------------- |
| level_started | int      |                 |                  |

#### Other Elements

- None

### **complete_level**

The event when a level is completely finished, following a fade to black

#### Event Data

| **Name**        | **Type** | **Description** | **Sub-Elements** |
| --------------- | -------- | --------------- | ---------------- |
| level_completed | int      |                 |                  |

#### Other Elements

- None

### **start_endgame**

When the player finishes the last level, and enters the 'endgame' portion showing where their town ended up

#### Event Data

| **Name**   | **Type** | **Description** | **Sub-Elements** |
| ---------- | -------- | --------------- | ---------------- |
| city_score | float    |                 |                  |
| scenario   | int      | 1, 2, or 3      |                  |

#### Other Elements

- None

### **level_fail**

When a player fails a level and is unable to continue

#### Event Data

| **Name**   | **Type**                                                                  | **Description**                                                                                                        | **Sub-Elements** |
| ---------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ---------------- |
| fail_types | enum(Time, Choice, Research, Resourceful, Endurance, Tech, Social, Trust) | The reason for fail event. There can be multiple reasons for an event fail. Enum values are in int form based on index |                  |

#### Other Elements

- None

### **resumed_checkpoint**

When a player resumes a checkpoint

#### Event Data

| **Name** | **Type** | **Description**                                                        | **Sub-Elements** |
| -------- | -------- | ---------------------------------------------------------------------- | ---------------- |
| node_id  | string   | The hexadecimal id of the checkpoint node                              |                  |
| origin   | string   | Whether the origin of the checkpoint resume was from menu or from fail |                  |

#### Other Elements

- None

## Detected Events

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.

None

## Processed Features

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.

**ChoiceClickCount** : _int_, _Aggregate feature_ (disabled)  
The number of choices made by user in a session  
_Sub-features_:

- **Action** : _int_, The number of action choices made by a user in a session

**GameComplete** : _bool_, _Aggregate feature_  
Whether a player completed a level

**TextClickCount** : _int_, _Aggregate feature_ (disabled)  
The number of choices made by user in a session

**SessionPlayTime** : _timedelta_, _Aggregate feature_ (disabled)  
A feature to calculate total time spent idle in session; configured to define 'idle' as spending 15 seconds or more without making a 'meaningful' action  
_Sub-features_:

- **Count** : _int_, The total number of times the player entered an idle state

- **Total Time** : _timedelta_, Total play time in the session

- **Total Play Time** : _timedelta_, Total play time in session minus idle time  
  _Other elements_:

IDLE_THRESH_SECONDS : 60

**PlayTime** : _timedelta_, _Aggregate feature_  
Amount of non-idle time player spent on session  
_Sub-features_:

- **Total Time** : _timedelta_, The total time the player spent on the game, disregarding idle time

- **Idle Time** : _timedelta_, The total time the player spent idle  
  _Other elements_:

IDLE_THRESH_SECONDS : 60

**UserPlayTime** : _timedelta_, _Aggregate feature_  
Amount of non-idle time spent by user across sessions  
_Sub-features_:

- **TotalTime** : _timedelta_, Total time user spent across sessions, from start to end

**SnippetReceivedCount** : _int_, _Aggregate feature_  
The number of snippets and types received by the user in a session  
_Sub-features_:

- **Bad** : _int_, Count of bad snippets

- **Good** : _int_, Count of good snippets

- **Great** : _int_, Count of great snippets

**StoryCompleteTime** : _float_, _Aggregate feature_ (disabled)  
Average amount of time spent completing stories, marked from first snippet received to level change event  
_Sub-features_:

- **DeltaTimeLogs** : _List[deltatime]_, List of delta times between snippet receive and level complete

- **RawTimeLogs** : _List[tuple]_, List of raw times for snippet receive and level complete, in tuples

**SkillSequenceCount** : _int_, _Aggregate feature_  
Count skill update events and log these events in a sequence  
_Sub-features_:

- **EventSequence** : _List[String]_, String of skill update events in order

**MeanSnippetTime** : _float_, _Aggregate feature_ (disabled)  
Average amount of time per snippet collected(between start of game and last snippet collect), as well as timestamps of all snippet collects  
_Sub-features_:

- **TimeLog** : _List[int]_, List of datetimes for snippet collects

**PlayerAttributes** : _String_, _Aggregate feature_  
Final Attributes of Player in a session  
_Sub-features_:

- **endurance**
- **resourcefulness**
- **tech**
- **social**
- **trust**
- **research**

**QuitLevel** : _int_, _Aggregate feature_  
The level of player/session on last logged event  
_Sub-features_:

- **EventName** : _String_, The last event done by the player

- **NodeID** : _String_, The last nodeID on quit event

**QuitType** : _str_, _Aggregate feature_  
A feature to return a bool for the type of quit event by the player  
_Sub-features_:

- **BetweenLevels** : _bool_, Quit was between levels

- **OnFail** : _bool_, Quit was on fail

- **OnCheckpoint** : _bool_, Quit was on a checkpoint

- **Other** : _bool_, Quit wasn't on fail or between levels

**WorstAttribute** : _int_, _Aggregate feature_  
indicates the value of the lowest attribute the player has.  
_Sub-features_:

- **Names** : _List[str]_, A list of all names of lowest attributes

**TopAttribute** : _int_, _Aggregate feature_  
indicates the value of the top attribute the player has.  
_Sub-features_:

- **Names** : _List[str]_, A list of all names of top attributes

**TotalFails** : _int_, _Aggregate feature_  
count of total fail events of all types

**ContinuesOnFail** : _int_, _Aggregate feature_  
Number of continues on a level after fail

**QuitNode** : _str_, _Aggregate feature_  
Most popular 5 quit nodes at population level  
_Other elements_:

enabled: : True

**StoryEditorTime** : _timedelta_, _Per-count feature_ (disabled)  
A feature to calculate total time spent in the story editor- same logic as SessionPlayTime, but only enabled between editor open/close events  
_Sub-features_:

- **Count** : _int_, The total number of times the player entered an idle state

- **Total Time** : _timedelta_, Total play time in the session

- **Total Play Time** : _timedelta_, Total play time in session minus idle time  
  _Other elements_:

IDLE_THRESH_SECONDS : 60

**AttributeView** : _int_, _Per-count feature_  
A feature for times a player goes into attribute dist., by level

**EditorNoteOpen** : _int_, _Per-count feature_  
A feature for times a player goes into editor notes, by level

**StoryScore** : _float_, _Per-count feature_  
A player's final score on a story, by level

**StoryScoreSequence** : _List[float]_, _Per-count feature_  
The sequence of changes in story score with each change of story composition, by level

**StoryAlignment** : _float_, _Per-count feature_  
Final alignment value of the user's story by level

**StoryAlignmentSequence** : _List[float]_, _Per-count feature_  
The sequence of changes in alignment with each change of story composition, by level

**SnippetReplace** : _int_, _Per-count feature_ (disabled)  
The number of times a snippet is replaced in a level  
_Sub-features_:

- **AverageReplace** : _float_, (Number of times replaced)/(num times notebook click)

**SnippetsCollected** : _List[str]_, _Per-count feature_  
A list of all snippets collected by the user, by level

**WorstPlayerAttribute** : _str_, _Per-count feature_  
Population level count of worst player attributes  
_Sub-features_:

- **Count** : _int_, A count of a specific attribute

**TopPlayerAttribute** : _str_, _Per-count feature_  
Population level count of top player attributes  
_Sub-features_:

- **Count** : _int_, A count of a specific attribute

**TopPlayerQuitType** : _str_, _Per-count feature_  
Population level count of top player attributes  
_Sub-features_:

- **Count** : _int_, A count of a specific attribute

**MaxedPlayerAttribute** : _str_, _Per-count feature_  
Population level count of maxed player attributes  
_Sub-features_:

- **Count** : _int_, A count of a specific attribute

**LevelCompleteCount** : _int_, _Per-count feature_  
Population level count of total level completes

**LevelCompleted** : _bool_, _Per-count feature_  
Boolean perLevel feature for whether a level was completed in session

**LevelTime** : _timedelta_, _Per-count feature_  
time spent on a level [sum of differences in time between 'BEGIN' and 'COMPLETE' event(s)]

**SnippetsSubmitted** : _List[str]_, _Per-count feature_  
List of all snippet ids included when a player submits their story.

**FailureCount** : _int_, _Per-count feature_  
How many times a level was failed  
_Sub-features_:

- **OutOfTime** : _int_, A count of how many failures were due to running out of time

- **LowAttribute** : _int_, A count of how many failures were due to the player having an attribute value too low

No changelog prepared
