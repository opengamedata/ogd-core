# Game: WEATHER_STATION

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

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **game_start**

When the player starts a new game (at present, this happens automatically at launch, but in the future the player will launch a new game from a menu).

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

### **grab_tablet**

When the player grabs the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_position | Dict[str, float] | The position of the tablet when the player grabbed it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| start_rotation | Dict[str, float] | The orientation of the tablet when the player grabbed it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player grabbed the tablet with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **release_tablet**

When the player releases the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_position | Dict[str, float] | The position of the tablet when the player released it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| end_rotation | Dict[str, float] | The orientation of the tablet when the player released it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player was moving the tablet with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **grab_workstation_handle**

When the player grabs the workstation adjustment handle

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_height | float | The height of the workstation handle when the player grabbed it. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player grabbed the handle with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **release_workstation_handle**

When the player releases the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_height | float | The height of the workstation handle when the player released it. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player moved the handle with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_rotate_graph_cw**

When the player clicks the button to rotate the phase graph clockwise

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_degrees | float | The rotation of the graph prior to the button press, in degrees, relative to the default graph rotation. | |
| end_degrees | float | The rotation of the graph as a result of the button press, in degrees, relative to the default graph rotation. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player grabbed the handle with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_rotate_graph_ccw**

When the player clicks the button to rotate the phase graph counter-clockwise

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_degrees | float | The rotation of the graph prior to the button press, in degrees, relative to the default graph rotation. | |
| end_degrees | float | The rotation of the graph as a result of the button press, in degrees, relative to the default graph rotation. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player moved the handle with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **grab_graph_ball**

When the player grabs the phase graph's state 'ball' and begins to drag it around

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player grabbed the ball with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **release_graph_ball**

When the player releases the phase graph's state 'ball' at a new position on the graph.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player moved the ball with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_tool_toggle**

When the player clicks the button to enable/disable a tool

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The tool whose toggle button was clicked. | |
| tool_enabled | bool | True if clicking the button enabled the tool, or false if it disabled the tool. | |
| tool_reset | bool | True if clicking the button reset the tool to its default value (0 for most tools). | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_tool_increase**

When the player clicks the button to nudge the tool value up

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The tool whose increase button was clicked. | |
| end_value | float | The tool value after being nudged. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_tool_decrease**

When the player clicks the button to nudge the tool value down

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The tool whose decrease button was clicked. | |
| end_value | float | The tool value after being nudged. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **grab_tool_slider**

When the player grabs the tool slider to adjust the value

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The tool whose decrease button was clicked. | |
| start_value | float | The tool value when the player grabbed the slider, in the tool's units. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **release_tool_slider**

When the player releases the tool slider after adjusting the value

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The tool whose decrease button was clicked. | |
| end_value | float | The tool value after the slider was released, in the tool's units. | |
| auto_release | bool | Indicator for whether the release of the slider was automatically enforced by the system. This could be either because the player's hand got too far from the slider, or because the player pressed another button, such as reset, while dragging the slider. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **gaze_object_end**

When the player has been looking at one of the major objects for at least a full second, and looks away.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object | enum(TABLET, PISTON, GRAPH, CONTROLS) | Which object the player gazed at. | |
| gaze_duration | float | The time in seconds the player spent looking at the object. | |

#### Other Elements

- None  

### **click_view_settings**

When the player presses the tablet button to view settings panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_toggle_setting**

When the player ticks/unticks a setting in the settings panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| setting | enum(AXIS_NUMBERS, GRID_LINES, REGION_LABELS, AXIS_TRACKERS) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |
| enabled | bool | True if the click enabled the given setting, or false if it disabled the setting. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **tool_locked**

When a lab task locks a specific tool, making it unvailable to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The specific tool that was locked. | |

#### Other Elements

- None  

### **tool_unlocked**

When a lab task unlocks a specific tool, making it ailable to the player. Also occurs when returning to Sandbox mode.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE) | The specific tool that was unlocked. | |

#### Other Elements

- None  

### **click_sandbox_mode**

When the player presses the tablet button to enter sandbox mode

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_lab_mode**

When the player presses the tablet button to enter lab mode

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| initial_lab | Dict[str, int] | null | A description of the lab that was started/resumed upon entering lab mode, or null if no lab was start and the player was shown the lab menu instead. |**lab_name** : str, **author** : str, **percent_complete** : float, **sections** : Dict[str, Any] |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_lab_scroll_up**

When the player presses the button to scroll up in the list of available labs in the lab menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_lab_scroll_down**

When the player presses the button to scroll down in the list of available labs in the lab menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **lab_menu_displayed**

When the tablet displays a list of available labs to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_labs | List[Dict] | A list of the labs (w/o section details) displayed to the player (not including any labs that are available but undisplayed). |**lab_name** : str, **author** : str, **percent_complete** : float, **is_active** : bool |

#### Other Elements

- None  

### **select_lab**

When the player selects a lab from the menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| lab | Dict[str, Any] | Details of the lab the player selected, including section and task sub-objects. |**lab_name** : str, **author** : str, **percent_complete** : float, **is_active** : bool, **sections** : List[Dict] |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_lab_home**

When the player presses the button to return to the main lab menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_select_section**

When the player presses the button to change to a new section of the lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| section | Dict[str, Any] | Details of the section the player selected, including task sub-objects. |**lab_name** : str, **section_number** : int, **description** : str, **is_complete** : bool, **is_active** : bool, **tasks** : List[Dict] |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_section_scroll_up**

When the player presses the button to scroll up in the list of available sections in the current lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_section_scroll_down**

When the player presses the button to scroll down in the list of available sections in the current lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **section_list_displayed**

When the tablet displays a list of available sections in the current lab to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_sections | List[Dict] | A list of the lab sections (w/o task details) displayed to the player (not including any sections that are available but undisplayed). |**lab_name** : str, **section_number** : int, **description** : str, **is_complete** : bool, **is_active** : bool |

#### Other Elements

- None  

### **click_select_task**

When the player presses the button to change to a new task in the lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| task | Dict[str, Any] | Details of the task the player selected. |**category** : enum(TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_task_scroll_left**

When the player presses the button to scroll left in the list of available tasks in the current lab section

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_task_scroll_right**

When the player presses the button to scroll right in the list of available tasks in the current lab section

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **task_list_displayed**

When the tablet displays a list of available tasks in the current lab section to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_sections | List[Dict] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |

#### Other Elements

- None  

### **target_state_achieved**

When the simulation reaches a target state defined for a lab task

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| target_state | Dict[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION), float] | The specific details of the target state, as a mapping from sim properties to the target values (note, not every property will be included, only the ones that had a target value specified). | |

#### Other Elements

- None  

### **target_state_lost**

When the simulation leaves a target state defined for a lab task, after previously reaching the target. Note that losing the target state does change the task to be incomplete.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| target_state | Dict[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION), float] | The specific details of the target state, as a mapping from sim properties to the target values (note, not every property will be included, only the ones that had a target value specified). | |
| incorrect_variables | List[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION)] | A list of which properties changed away from their target values. | |

#### Other Elements

- None  

### **constant_variable_achieved**

NOT YET IMPLEMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **constant_variable_lost**

NOT YET IMPLEMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **click_select_answer**

When the player presses the button to select an answer to a quiz question

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| selection_index | int | Index of the newly-selected item in the 'options' list (note that the value of the selected item will appear in `selected_options`. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_deselect_answer**

When the player presses the button to deselect an answer to a quiz question

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| deselection_index | int | Index of the item the player deselected in the 'options' list (note that the value of the deselected item will appear in `options`. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_submit_answer**

When the player presses the button to submit their answer to a quiz question

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| is_correct_answer | bool | Indicator for whether the submitted selection is correct or not (note, this could be derived from the `quiz_task`). | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_reset_quiz**

When the player presses the button to reset the quiz after submitting an answer

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| was_correct_answer | bool | Indicator for whether the previously-submitted selection was correct or not. If false, the player is resetting after a failed attempt. | |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **click_open_word_bank**

When the player presses the button to open the bank of words for a 'word bank' quiz

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| hand | enum(LEFT, RIGHT, MOUSE) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |

#### Other Elements

- None  

### **word_bank_displayed**

When the system displays the bank of available words in a 'word bank' quiz

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| words | List[str] | The list of words available to be chosen from the bank. | |

#### Other Elements

- None  

### **word_bank_closed**

When the system closes the bank of available words in a 'word bank' quiz, typically after the player performed a `click_select_answer`

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| words | List[str] | The list of words available to be chosen from the bank. | |
| selected_word | str | The word the player selected before the bank closed. | |

#### Other Elements

- None  

### **complete_lab**

When the player completes the last incomplete task of the last incomplete section of a lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| lab | Dict[str, int] | null | A description of the lab that was started/resumed upon entering lab mode, or null if no lab was start and the player was shown the lab menu instead. |**lab_name** : str, **author** : str, **percent_complete** : float, **sections** : Dict[str, Any] |

#### Other Elements

- None  

### **complete_section**

When the player completes the last incomplete task of a lab section

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| section | Dict[str, Any] | Details of the section the player selected, including task sub-objects. |**lab_name** : str, **section_number** : int, **description** : str, **is_complete** : bool, **is_active** : bool, **tasks** : List[Dict] |

#### Other Elements

- None  

### **complete_task**

When the player completes the last incomplete task of the last incomplete section of a lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| task | Dict[str, Any] | Details of the task the player selected. |**category** : enum(TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

None

No changelog prepared

