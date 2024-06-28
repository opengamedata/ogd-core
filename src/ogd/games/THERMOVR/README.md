# Game: THERMOVR

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
| HandType | ['LEFT', 'RIGHT', 'MOUSE'] |
| Platform | ['VR, WEB'] |
| ToolType | ['INSULATION', 'LOWER_STOP', 'UPPER_STOP', 'INCREASE_WEIGHT', 'DECREASE_WEIGHT', 'HEAT', 'COOLING', 'CHAMBER_TEMPERATURE', 'CHAMBER_PRESSURE'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched, *not including time when the game was paused*. | |
| region | enum(WATER, VAPOR, TWO_PHASE) | The current graph region of the water in the piston | |
| pressure | float | The current pressure (P) in the piston in kPa | |
| temperature | float | The current temperature (T) of the water in the piston in K | |
| volume | float | The current volume (V) of the water in the piston m^3 | |
| internal_energy | float | The current internal energy (u) in the piston | |
| entropy | float | The current entropy (s) in the piston in kJ/(kgK) | |
| enthalpy | float | The current enthalpy (h) in the piston in kJ/kg | |
| vapor | float | The current percentage (by mass) of water in the vapor phase in the piston | |
| heat_delta | float | Current readout of net heat change due to inputs from the workstation terminal | |
| pos_x | float | The current x-position of the headset at the moment the event occurred. | |
| pos_y | float | The current y-position of the headset at the moment the event occurred. | |
| pos_z | float | The current z-position of the headset at the moment the event occurred. | |
| rot_x | float | The x-component of the orientation of the headset at the moment the event occurred. | |
| rot_y | float | The y-component of the orientation of the headset at the moment the event occurred. | |
| rot_z | float | The z-component of the orientation of the headset at the moment the event occurred. | |
| rot_w | float | The w-component of the orientation of the headset at the moment the event occurred. | |
| insulation_tool | Dict[str, int] | The state of the insulation tool: whether it is enabled, and the percent effectiveness of the insulation. |**enabled** : bool, **slider_val** : float |
| lower_stop_tool | Dict[str, int] | The state of the lower stop tool: whether it is enabled, and the minimum piston volume in m^3/kg. |**enabled** : bool, **slider_val** : float |
| upper_stop_tool | Dict[str, int] | The state of the upper stop tool: whether it is enabled, and the maximum piston volume in m^3/kg. |**enabled** : bool, **slider_val** : float |
| increase_weight_tool | Dict[str, int] | The state of the weight (pressure increase) tool: whether it is enabled, and the pressure increase in kPa. |**enabled** : bool, **slider_val** : float |
| decrease_weight_tool | Dict[str, int] | The state of the balloon (pressure reduction) tool: whether it is enabled, and the pressure reduction in kPa. |**enabled** : bool, **slider_val** : float |
| heat_tool | Dict[str, int] | The state of the bunsen burner tool: whether it is enabled, and the heat per second it generates in kJ/s. |**enabled** : bool, **slider_val** : float |
| cooling_tool | Dict[str, int] | The state of the cooling coil tool: whether it is enabled, and the heat per second it removes in kJ/s. |**enabled** : bool, **slider_val** : float |
| chamber_temperature_tool | Dict[str, int] | The state of the chamber/ambient temperature tool: whether ambient heat exchange is enabled, and the ambient temperature in K. |**enabled** : bool, **slider_val** : float |
| chamber_pressure_tool | Dict[str, int] | The state of the chamber/ambient pressure tool: the ambient pressure in kPa (the ambient pressure is always enabled). |**enabled** : bool, **slider_val** : float |
| current_lab | Dict[str, int] | null | A description of the currently-active lab, or null if not in lab mode. |**lab_name** : str, **author** : str, **percent_complete** : float |
| current_section | Dict[str, int] | null | A description of the currently-active lab section, or null if not in lab mode. |**section_number** : int, **description** : str, **is_complete** : bool |
| current_task | Dict[str, int] | null | A description of the currently-active lab task, or null if not in lab mode. |**category** : enum(TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **task_number** : int, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **session_start**

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **game_start**

When a new game is started

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| mode | Platform | The mode of the game being started, either on a VR headset or the web-based version. | |  

### **click_new_game**

When the player clicks the button for a new game. This should trigger a new `game_start` event, with new session and player IDs

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_reset_sim**

When the player clicks the button to reset the sim to its default state. The default state may be redefined by certain tasks in lab mode.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |
| default_state | Dict[str, float] | A mapping of simulation state variable names to their default values. |**region** : enum(WATER, VAPOR, TWO_PHASE), **pressure** : float, **temperature** : float, **volume** : float, **internal_energy** : float, **entropy** : float, **enthalpy** : float, **vapor** : float |  

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

### **grab_tablet**

When the player grabs the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_position | Dict[str, float] | The position of the tablet when the player grabbed it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| start_rotation | Dict[str, float] | The orientation of the tablet when the player grabbed it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | HandType | Indicator of whether the player grabbed the tablet with their right or left hand, or a mouse. | |  

### **release_tablet**

When the player releases the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_position | Dict[str, float] | The position of the tablet when the player released it |**pos_x** : float, **pos_y** : float, **pos_z** : float |
| end_rotation | Dict[str, float] | The orientation of the tablet when the player released it |**rot_x** : float, **rot_y** : float, **rot_z** : float, **rot_w** : float |
| hand | HandType | Indicator of whether the player was moving the tablet with their right or left hand, or a mouse. | |  

### **click_shift_tablet**

When the player releases the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| shift_direction | enum(LEFT, RIGHT) | TODO | |
| hand | HandType | Indicator of whether the player was moving the tablet with their right or left hand, or a mouse. | |  

### **grab_workstation_handle**

When the player grabs the workstation adjustment handle

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_height | float | The height of the workstation handle when the player grabbed it. | |
| hand | HandType | Indicator of whether the player grabbed the handle with their right or left hand, or a mouse. | |  

### **release_workstation_handle**

When the player releases the tablet object

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| end_height | float | The height of the workstation handle when the player released it. | |
| hand | HandType | Indicator of whether the player moved the handle with their right or left hand, or a mouse. | |  

### **click_rotate_graph_cw**

When the player clicks the button to rotate the phase graph clockwise

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_degrees | float | The rotation of the graph prior to the button press, in degrees, relative to the default graph rotation. | |
| end_degrees | float | The rotation of the graph as a result of the button press, in degrees, relative to the default graph rotation. | |
| hand | HandType | Indicator of whether the player grabbed the handle with their right or left hand, or a mouse. | |  

### **click_rotate_graph_ccw**

When the player clicks the button to rotate the phase graph counter-clockwise

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| start_degrees | float | The rotation of the graph prior to the button press, in degrees, relative to the default graph rotation. | |
| end_degrees | float | The rotation of the graph as a result of the button press, in degrees, relative to the default graph rotation. | |
| hand | HandType | Indicator of whether the player moved the handle with their right or left hand, or a mouse. | |  

### **grab_graph_ball**

When the player grabs the phase graph's state 'ball' and begins to drag it around

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player grabbed the ball with their right or left hand, or a mouse. | |  

### **release_graph_ball**

When the player releases the phase graph's state 'ball' at a new position on the graph.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player moved the ball with their right or left hand, or a mouse. | |  

### **click_tool_toggle**

When the player clicks the button to enable/disable a tool

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool whose toggle button was clicked. | |
| tool_enabled | bool | True if clicking the button enabled the tool, or false if it disabled the tool. | |
| tool_reset | bool | True if clicking the button reset the tool to its default value (0 for most tools). | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **enter_nudge_mode**

When the player clicks the button to nudge the tool value up

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool that was nudged. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **exit_nudge_mode**

When the player clicks the button to nudge the tool value down

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool that was nudged. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **grab_tool_slider**

When the player grabs the tool slider to adjust the value

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool whose slider was grabbed. | |
| start_value | float | The tool value when the player grabbed the slider, in the tool's units. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **release_tool_slider**

When the player releases the tool slider after adjusting the value

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool that was adjusted. | |
| end_value | float | The tool value after the slider was released, in the tool's units. | |
| auto_release | bool | Indicator for whether the release of the slider was automatically enforced by the system. This could be either because the player's hand got too far from the slider, or because the player pressed another button, such as reset, while dragging the slider. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_edit_tool_value**

When the player clicks onto a tool to manually edit the value

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool whose edit area was clicked. | |
| hand | HandType | Always 'MOUSE', since this feature is only available on desktop. | |  

### **set_tool_value**

When the player sets a custom value for a given tool.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool whose value was set. | |
| new_value | float | The tool value entered by the player. | |  

### **set_invalid_tool_value**

When the player attempts to enter a custom value, but it is not in the valid range, or is an invalid type.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool whose value was set. | |
| bad_value | str | The tool value after the slider was released, in the tool's units. | |  

### **cancel_edit_tool_value**

When the player exits the custom value box, without setting a value.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tool_name | ToolType | The tool whose value was set. | |  

### **gaze_object_end**

When the player has been looking at one of the major objects for at least a full second, and looks away.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| object | enum(TABLET, PISTON, GRAPH, CONTROLS) | Which object the player gazed at. | |
| gaze_duration | float | The time in seconds the player spent looking at the object. | |  

### **critical_alert_displayed**

Unknown

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **critical_alert_ended**

Unknown

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_reset_heat_delta**

Unknown

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_view_settings**

When the player presses the tablet button to view settings panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_toggle_setting**

When the player ticks/unticks a setting in the settings panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| setting | enum(AXIS_NUMBERS, GRID_LINES, REGION_LABELS, AXIS_TRACKERS) | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |
| enabled | bool | True if the click enabled the given setting, or false if it disabled the setting. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **tool_locked**

When a lab task locks a specific tool, making it unvailable to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | ToolType | The specific tool that was locked. | |  

### **tool_unlocked**

When a lab task unlocks a specific tool, making it ailable to the player. Also occurs when returning to Sandbox mode.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | ToolType | The specific tool that was unlocked. | |  

### **click_sandbox_mode**

When the player presses the tablet button to enter sandbox mode

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_lab_mode**

When the player presses the tablet button to enter lab mode

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| initial_lab | Dict[str, int] | null | A description of the lab that was started/resumed upon entering lab mode, or null if no lab was start and the player was shown the lab menu instead. |**lab_name** : str, **author** : str, **percent_complete** : float, **sections** : Dict[str, Any] |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_lab_scroll_up**

When the player presses the button to scroll up in the list of available labs in the lab menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_lab_scroll_down**

When the player presses the button to scroll down in the list of available labs in the lab menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **lab_menu_displayed**

When the tablet displays a list of available labs to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_labs | List[Dict] | A list of the labs (w/o section details) displayed to the player (not including any labs that are available but undisplayed). |**lab_name** : str, **author** : str, **percent_complete** : float, **is_active** : bool |  

### **select_lab**

When the player selects a lab from the menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| lab | Dict[str, Any] | Details of the lab the player selected, including section and task sub-objects. |**lab_name** : str, **author** : str, **percent_complete** : float, **is_active** : bool, **sections** : List[Dict] |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_lab_home**

When the player presses the button to return to the main lab menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_select_section**

When the player presses the button to change to a new section of the lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| section | Dict[str, Any] | Details of the section the player selected, including task sub-objects. |**lab_name** : str, **section_number** : int, **description** : str, **is_complete** : bool, **is_active** : bool, **tasks** : List[Dict] |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_section_scroll_up**

When the player presses the button to scroll up in the list of available sections in the current lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_section_scroll_down**

When the player presses the button to scroll down in the list of available sections in the current lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **section_list_displayed**

When the tablet displays a list of available sections in the current lab to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_sections | List[Dict] | A list of the lab sections (w/o task details) displayed to the player (not including any sections that are available but undisplayed). |**lab_name** : str, **section_number** : int, **description** : str, **is_complete** : bool, **is_active** : bool |  

### **click_select_task**

When the player presses the button to change to a new task in the lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| task | Dict[str, Any] | Details of the task the player selected. |**category** : enum(PlainText, TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **visual_aid** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_task_scroll_left**

When the player presses the button to scroll left in the list of available tasks in the current lab section

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_task_scroll_right**

When the player presses the button to scroll right in the list of available tasks in the current lab section

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **task_list_displayed**

When the tablet displays a list of available tasks in the current lab section to the player

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_sections | List[Dict] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **visual_aid** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |  

### **target_state_entered**

When the simulation reaches a target state defined for a lab task

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| target_state | Dict[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION), float] | The specific details of the target state, as a mapping from sim properties to the target values (note, not every property will be included, only the ones that had a target value specified). | |
| tolerances | Dict[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION), float] | The specific details of the target state, as a mapping from sim properties to the target values (note, not every property will be included, only the ones that had a target value specified). | |  

### **target_state_completed**

TODO

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| target_state | Dict[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION) | Tool enum, float] | The specific details of the target state, as a mapping from sim properties to the target values (note, not every property will be included, only the ones that had a target value specified). | |  

### **target_state_lost**

When the simulation leaves a target state defined for a lab task, after previously reaching the target. Note that losing the target state does change the task to be incomplete.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| target_state | Dict[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION), float] | The specific details of the target state, as a mapping from sim properties to the target values (note, not every property will be included, only the ones that had a target value specified). | |
| incorrect_variables | List[enum(TEMPERATURE, PRESSURE, VOLUME, INTERNAL_ENERGY, ENTROPY, ENTHALPY, VAPOR_PROPORTION)] | A list of which properties changed away from their target values. | |
| timer_elapsed | float | The amount of time elapsed before losing the target state. | |
| timer_remaining | float | The amount of time remaining to complete the target state, when the state was lost. | |  

### **constant_variable_achieved**

NOT YET IMPLEMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **constant_variable_lost**

NOT YET IMPLEMENTED

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **target_state_task_began**

When the player has selected a target state task.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **target_state_task_ended**

When the player ends the target state task, moving to another task.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_select_answer**

When the player presses the button to select an answer to a quiz question

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| selection_index | int | Index of the newly-selected item in the 'options' list (note that the value of the selected item will appear in `selected_options`. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_deselect_answer**

When the player presses the button to deselect an answer to a quiz question

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| deselection_index | int | Index of the item the player deselected in the 'options' list (note that the value of the deselected item will appear in `options`. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_submit_answer**

When the player presses the button to submit their answer to a quiz question

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| is_correct_answer | bool | Indicator for whether the submitted selection is correct or not (note, this could be derived from the `quiz_task`). | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_reset_quiz**

When the player presses the button to reset the quiz after submitting an answer

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| was_correct_answer | bool | Indicator for whether the previously-submitted selection was correct or not. If false, the player is resetting after a failed attempt. | |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **click_open_word_bank**

When the player presses the button to open the bank of words for a 'word bank' quiz

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| quiz_task | Dict[str, Any] | A list of the tasks for the current lab section shown to the player (not including any tasks that are available but undisplayed). |**category** : enum(MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str], **options** : List[str | float], **selected_options** : List[str | float], **correct_answer** : float | str | List[float] | List[str] |
| hand | HandType | Indicator of whether the player pressed the button with their right or left hand, or a mouse. | |  

### **word_bank_displayed**

When the system displays the bank of available words in a 'word bank' quiz

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| words | List[str] | The list of words available to be chosen from the bank. | |  

### **word_bank_closed**

When the system closes the bank of available words in a 'word bank' quiz, typically after the player performed a `click_select_answer`

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| words | List[str] | The list of words available to be chosen from the bank. | |
| selected_word | str | The word the player selected before the bank closed. | |  

### **complete_lab**

When the player completes the last incomplete task of the last incomplete section of a lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| lab | Dict[str, int] | null | A description of the lab that was started/resumed upon entering lab mode, or null if no lab was start and the player was shown the lab menu instead. |**lab_name** : str, **author** : str, **percent_complete** : float, **sections** : Dict[str, Any] |  

### **complete_section**

When the player completes the last incomplete task of a lab section

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| section | Dict[str, Any] | Details of the section the player selected, including task sub-objects. |**lab_name** : str, **section_number** : int, **description** : str, **is_complete** : bool, **is_active** : bool, **tasks** : List[Dict] |  

### **complete_task**

When the player completes the last incomplete task of the last incomplete section of a lab

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| task | Dict[str, Any] | Details of the task the player selected. |**category** : enum(TARGET_STATE, CONSTANT_VARIABLE, MULTIPLE_CHOICE, MULTIPLE_SELECT, WORD_BANK), **lab_name** : str, **section_number** : str, **task_number** : int, **is_active** : bool, **is_complete** : bool, **available_tools** : List[enum(INSULATION, LOWER_STOP, UPPER_STOP, INCREASE_WEIGHT, DECREASE_WEIGHT, HEAT, COOLING, CHAMBER_TEMPERATURE, CHAMBER_PRESSURE)], **prompts** : List[str] |  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**LabCompleteCount** : *int*, *Aggregate feature*  (disabled)  
Count of number of labs completed  
  

**LeftHandMoves** : *int*, *Aggregate feature*  (disabled)  
Count of number of Left hand moves  
  

**RighHandMoves** : *int*, *Aggregate feature*  (disabled)  
Count of number of right hand moves  
  

**PhasesReached** : *dict*, *Aggregate feature*  (disabled)  
Phases Reached during a certain task  
  

**PlayMode** : *str*, *Aggregate feature*  (disabled)  
Play mode of the current instance  
  

**TaskCompleteCount** : *int*, *Aggregate feature*   
Count of number of tasks completed  
  

**ToolNudegCount** : *dict*, *Aggregate feature*  (disabled)  
Count of number of times a tool has been nudged  
  

**ToolSliderTime** : *timedelta*, *Aggregate feature*  (disabled)  
Counts the total time the slider has been moved  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.

No changelog prepared

