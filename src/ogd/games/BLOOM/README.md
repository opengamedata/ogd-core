# Game: BLOOM

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
| MapMode | ['VIEW', 'BUILD', 'DESTROY'] |
| BuildingType | ['EMPTY', 'ROAD', 'TOLLBOOTH', 'CITY', 'DAIRYFARM', 'GRAINFARM', 'STORAGE', 'PROCESSOR', 'EXPORTDEPOT', 'PROCESSORBROKEN', 'OBSTACLE'] |
| TileType | ['LAND', 'WATER', 'DEEP_WATER'] |
| CardinalDirection | ['N', 'NE', 'SE', 'S', 'SW', 'NW'] |
| PolicyCategory | ['ECONOMY', 'ECOLOGY'] |
| PolicyType | ['SALES', 'IMPORT', 'RUNOFF', 'CLEANUP'] |
| SalesPolicy | ['NOT_SET', 'NONE', 'LOW_TAX', 'HIGH_TAX', 'SUBSIDY'] |
| ImportPolicy | ['NOT_SET', 'NONE', 'MILK', 'GRAIN', 'FERTILIZER'] |
| RunoffPolicy | ['NOT_SET', 'NONE', 'LOW', 'HIGH', 'VERY_HIGH'] |
| CleanupPolicy | ['NOT_SET', 'NONE', 'LOW_SKIMMING', 'HIGH_SKIMMING', 'SKIM_AND_DREDGE'] |
| CharacterClass | ['TODO : This includes ECONOMY_ADVISOR, ECOLOGY_ADVISOR, PHOS4US, GRAIN_FARMER, DAIRY_FARMER, etc. but need to get full list'] |
| AlertType | ['null', 'Bloom', 'ExcessRunoff', 'DieOff', 'CritImbalance', 'UnusedProcessor', 'DecliningPop', 'SellingLoss', 'Disconnected', 'Dialogue', 'Global'] |
| ZoomType | ['BUTTON', 'SCROLL'] |
| LossType | ['CityFailed', 'TooManyBlooms', 'OutOfMoney'] |
| AttributeStatus | ['GOOD', 'OK', 'BAD'] |
| ViewType | ['PHOSPHORUS_VIEW', 'ECONOMY_VIEW'] |  

### Game State  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| seconds_from_launch | float | The number of seconds of game time elapsed since the game was launched, *not including time when the game was paused*. | |
| current_county | str | The current county where the player is located | |
| current_money | int | The current amount of money the county has available | |
| map_mode | MapMode | Whether the player is currently in view, build, or destroy mode. | |
| county_policies | Dict[str, Any] | The set of policies in the current county. Has elements for each of the four policy choices, which each in turn are subdictionaries that have elements with the policy choice and whether the choice is locked. |**sales** : Dict, **import_subsidy** : Dict{policy_choice, is_locked}, **runoff** : Dict{policy_choice, is_locked}, **cleanup** : Dict{policy_choice, is_locked} |
| phosphorus_view_enabled | bool | Whether the player currently has the phosphorus overlay mode enabled | |  

### User Data  

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **session_start**

When the app is started and the gameplay session is assigned a session ID

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **game_start**

When a game is actually loaded/started, showing the player their interface and map.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| music_volume | float | The volume for the in-game music, set in the new/resume game panel. | |
| fullscreen_enabled | bool | True if the player has enabled fullscreen play, or false if not. | |
| hq_graphics_enabled | bool | True if the player has enabled high-quality graphics, or false if not. | |
| map_state | Dict[str, List[Dict]] | A collection of individual county maps for the game, in their initial states at load time. Each county map is made up of a list of sub-dictionaries defining individual build tiles, which contain the tile's hex coordinates, elevation, tile type, and objects on the tile. If this event is a 'resume', some of the tiles will contain buildings (a sub-dict with tile ID, building type, and list of road connections on the tile). |**index** : int, **height** : int, **type** : TileType, **building** : BuildingType, **connections** : List[CardinalDirection] |  

### **win_game**

When the player enters the game win state, and is shown the 'you win' cutscene

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| map_state | TODO : BuildMap | The state of the build map when the player entered the win state. | |  

### **lose_game**

When the player enters the game lose state, and is taken back to a checkpoint to try again.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| lose_condition | LossType | The state of the build map when the player entered the win state. | |  

### **click_new_game**

When the player clicks the button for a new game. This should bring the 'new game' menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_resume_game**

When the player clicks the button for a new game. This should bring up the 'resume' game menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_play_game**

When the player clicks the button to actually launch the game, whether from the 'new' or 'resume' menu

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **pause_game**

When the player presses the spacebar or escape key to pause the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **unpause_game**

When the player presses the spacebar or escape key to un-pause the game

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_credits**

When the player clicks to play the game credits. Not actually sure if this feature still exists...

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **close_credits**

When the player exits the credits sequence

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_return_main_menu**

When the player clicks the button to return to the main menu from the (not sure if this used to be from the game or the new/resume game menu, in either case, it seems like this no longer exists...)

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **toggle_fullscreen_setting**

When the player ticks/unticks the fullscreen setting the new/resume game panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| enabled | bool | True if the click enabled the fullscreen setting, or false if it disabled the setting. | |  

### **toggle_hq_graphics**

When the player ticks/unticks the box for the high-quality graphics setting the new/resume game panel

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| enabled | bool | True if the click enabled the hq graphics setting, or false if it disabled the setting. | |  

### **set_music_volume**

When the player clicks or releases the music volume slider, setting a new volume level

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| old_volume | float | The initial value of the slider. | |
| new_volume | float | The initial value of the slider. | |  

### **county_unlocked**

When the game unlocks a new county for the player to explore

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| county_name | str | The name of the newly-unlocked county. | |
| county_state | List[Dict] | A collection of sub-dictionaries defining individual build tiles in the county map, which contain the tile's hex coordinates, elevation, tile type, and objects on the tile. |**index** : int, **height** : int, **type** : TileType, **building** : BuildingType, **connections** : List[CardinalDirection] |  

### **cutscene_start**

When a game cutscene is triggered

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| cutscene_id | str | The ID for the specific cutscene. | |  

### **cutscene_end**

When a game cutscene is completed

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| cutscene_id | str | The ID for the specific cutscene. | |  

### **cutscene_page_displayed**

When a new page of the cutscene is displayed for the player to read

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| cutscene_id | str | The ID for the specific cutscene. | |
| page_id | str | The ID for the specific page of the cutscene, which can be cross-referenced with game metadata. | |
| frame_ids | List[str] | The list, in order, of IDs for each frame within the given cutscene page. | |
| page_text | str | The text content of the cutscene page. | |  

### **click_cutscene_next**

When the player has finished reading the current cutscene page, and clicks to advance to the next one.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| cutscene_id | str | The ID for the specific cutscene. | |
| page_id | str | The ID for the specific cutscene page that was just finished, which can be cross-referenced with game metadata. | |  

### **dialog_start**

When an in-game dialog scene begins, whether a part of a tutorial, the result of the player clicking a dialog notification, or clicking a warning notification

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| node_id | str | The ID for the specific dialog node, which can be cross-referenced with game metadata to recover the contents of the dialog. | |
| skippable | bool | Whether this particular dialog can be skipped/ignored, or must be viewed before resuming the game. | |  

### **dialog_end**

When an in-game dialog scene completes, whether it was triggered as a part of a tutorial, the result of the player clicking a dialog notification, or clicking a warning notification

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| node_id | str | The ID for the specific dialog node, which can be cross-referenced with game metadata to recover the contents of the dialog. | |
| skippable | bool | Whether this particular dialog can be skipped/ignored, or must be viewed before resuming the game. | |  

### **character_line_displayed**

When a character has a line displayed during in-game dialog

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| character_name | str | The specific name of the character 'speaking' the line of dialog. | |
| character_type | CharacterType | The kind of character who is 'speaking,' such as an advisor or farmer. | |
| line_text | str | The actual content of the line of dialog. | |  

### **click_next_character_line**

When the player finishes reading the current line of dialog, and clicks to advance to the next

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| character_name | str | The specific name of the character 'speaking' the line of dialog. | |
| character_type | CharacterType | The kind of character who is 'speaking,' such as an advisor or farmer. | |
| line_text | str | The actual content of the line of dialog that was just completed (not the line that will be shown next). | |  

### **leave_county**

When player leaves from one county to another.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| to_county | str | The new county the player is entering as they leave the current county. | |  

### **enter_county**

When player has crossed into a county from another, and the interface updates to show the new county's money, policies, etc.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| from_county | str | The county the player left to enter the current one. | |  

### **open_economy_view**

When the player clicks to open the economy breakdown view

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **close_economy_view**

When the player exits the economy breakdown view

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **toggle_map_mode**

When the player toggles between view and build mode for the map.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| new_mode | MapMode | The mode the player toggled into, should only be able to go into VIEW or BUILD modes | |  

### **build_menu_displayed**

When the game displays the build menu, in response to the player entering build mode.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| available_buildings | List[Dict] | The buildings available for the player to construct |**name** : str, **price** : int |  

### **enter_destroy_mode**

When the player is in build mode, and clicks the 'destroy' button to go into destroy mode

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **exit_destroy_mode**

When the player is in destroy mode, and clicks to return to normal build mode

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **global_alert_displayed**

When game displays a 'global' alert pop-up, which pauses game time until the player clicks the alert.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alert_type | AlertType | The kind of alert that was displayed. | |  

### **click_global_alert**

When the player clicks on a 'global' in-game alert pop-up, which will in turn trigger a dialog to begin.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alert_type | AlertType | The kind of alert the player clicked. | |
| node_id | str | The ID of the node displayed when the alert is clicked | |  

### **local_alert_displayed**

When game displays a 'local' alert pop-up, which appears above the building tile for which the alert occurred, and does not pause game time.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alert_type | AlertType | The kind of alert that was displayed. | |
| tile_index | int | The index, within the global map, of the tile containing the building with the alert. | |  

### **click_local_alert**

When the player clicks on a 'local' in-game alert pop-up, which will in turn trigger a dialog to begin.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| alert_type | AlertType | The kind of alert the player clicked. | |
| tile_index | int | The index, within the global map, of the tile containing the building with the alert. | |
| node_id | str | The ID of the node displayed when the alert is clicked | |  

### **bloom_alert_displayed**

When game displays a 'bloom' alert pop-up, which appears above a newly-formed bloom, and does not pause game time.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile containing the bloom. | |
| phosphorus_value | int | The amount of phosphorus on the tile. | |  

### **click_bloom_alert**

When the player clicks on a 'bloom' in-game alert pop-up, which will in turn trigger a dialog to begin.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile containing the building with the alert. | |
| phosphorus_value | int | The amount of phosphorus on the tile. | |
| node_id | str | The ID of the node displayed when the alert is clicked | |  

### **change_zoom**

When the player clicks on an in-game notification/alert pop-up, such as a bloom warning, a farm losing money, or an optional dialog.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| zoom_type | ZoomType | Whether the player zoomed with the zoom buttons or a mouse/trackpad scroll. | |
| start_zoom | float | The initial zoom level, before the button click/scroll | |
| end_zoom | float | The final zoom level, after the button click/scroll | |  

### **click_open_policy_category**

When the player clicks to pop up the list of policies within the economy or ecology policy category.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| category | PolicyCategory | Whether the player opened up the economic or ecologic category. | |  

### **click_open_policy**

When the player clicks to open the policy card choices for a specific policy type.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| policy | PolicyType | The specific policy that was clicked, i.e. sales tax, import subsidy, runoff fine, or cleanup initiative. | |
| from_taskbar | bool | Whether the player opened the policy from the county taskbar. If false, the policy was opened from the 'category' open as in a click_open_policy_category event. | |  

### **hover_policy_card**

When the player moves their mouse over a new policy card.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| policy | PolicyType | The specific policy whose cards are displayed, i.e. sales tax, import subsidy, runoff fine, or cleanup initiative. | |
| choice_number | int | The index, among all cards for the given policy, of the hovered policy. | |
| choice_name | SalesPolicy | ImportPolicy | RunoffPolicy | CleanupPolicy | The enum-ified name of the hovered policy. | |
| choice_text | str | The text content of the hovered card. | |  

### **select_policy_card**

When the player clicks a policy card, selecting it as the new setting for the given policy in the current county.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| policy | PolicyType | The specific policy whose card was selected. | |
| choice_number | int | The index, among all cards for the given policy, of the selected policy. | |
| choice_name | SalesPolicy | ImportPolicy | RunoffPolicy | CleanupPolicy | The enum-ified name of the selected policy. | |
| choice_text | str | The text content of the selected card. | |  

### **click_inspect_building**

When the player clicks a building on the map, to review its current state.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | BuildingType | The specific type of building selected for inspection. | |
| tile_index | int | The index, within the county map, of the tile containing the building being inspected. | |
| connections | List[CardinalDirection] | The directions on the tile containing road connections. | |  

### **building_inspector_displayed**

When the inspector panel for a building is displayed to the user, for any building that does not have a more-specific `*_inspector_displayed` event.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | BuildingType | The specific type of building selected for inspection. | |
| tile_index | int | The index, within the county map, of the tile containing the building being inspected. | |
| connections | List[CardinalDirection] | The directions on the tile containing road connections. | |  

### **storage_inspector_displayed**

When the inspector panel for a manure storage building is displayed to the user.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the county map, of the tile containing the building being inspected. | |
| connections | List[CardinalDirection] | The directions on the tile containing road connections. | |
| units_filled | int | The number of storage units filled within the storage building, as displayed in the panel. | |  

### **city_inspector_displayed**

When the inspector panel for a city is displayed to the user.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the county map, of the tile containing the building being inspected. | |
| connections | List[CardinalDirection] | The directions on the tile containing road connections. | |
| city_name | str | The display name of the city/town being inspected. | |
| population | AttributeStatus | Whether the population is growing (GOOD), stable (OK), or falling (BAD). | |
| water | AttributeStatus | Whether the local water quality is good, ok, or bad. | |
| milk | AttributeStatus | Whether the available quantity of milk is plenty (GOOD), enough (OK), or not enough (BAD). | |  

### **grain_inspector_displayed**

When the inspector panel for a grain farm is displayed to the user.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the county map, of the tile containing the building being inspected. | |
| farm_name | str | The name of the specific farm being displayed. | |
| connections | List[CardinalDirection] | The directions on the tile containing road connections. | |
| grain_tab | Dict[str, bool | str | int] | A data displayed in the grain tab of the grain farm inspector. |**is_active_tab** : bool, **buyer_name** : str, **buyer_county** : str, **base_price** : int, **shipping_cost** : int, **total_profit** : int |
| fertilizer_tab | Dict[str, bool | str | int] | A data displayed in the grain tab of the grain farm inspector. |**is_active_tab** : bool, **seller_name** : str, **seller_county** : str, **base_price** : int, **shipping_cost** : int, **sales_policy** : int, **import_policy** : int, **total_profit** : int |  

### **dairy_inspector_displayed**

When the inspector panel for a dairy farm is displayed to the user.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the county map, of the tile containing the building being inspected. | |
| farm_name | str | The name of the specific farm being displayed. | |
| connections | List[CardinalDirection] | The directions on the tile containing road connections. | |
| grain_tab | Dict[str, bool | str | int] | A data displayed in the grain tab of the grain farm inspector. |**is_active_tab** : bool, **seller_name** : str, **seller_county** : str, **base_price** : int, **shipping_cost** : int, **sales_policy** : int, **import_policy** : int, **total_profit** : int |
| dairy_tab | Dict[str, bool | str | int] | A data displayed in the grain tab of the grain farm inspector. |**is_active_tab** : bool, **buyer_name** : str, **buyer_county** : str, **base_price** : int, **total_profit** : int |
| fertilizer_tab | Dict[str, bool | str | int] | A data displayed in the grain tab of the grain farm inspector. |**is_active_tab** : bool, **buyer_name** : str, **buyer_county** : str, **base_price** : int, **shipping_cost** : int, **runoff_fine** : int, **total_profit** : int |  

### **dismiss_building_inspector**

When the player clicks away from a building inspector.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | BuildingType | The specific type of building that was inspected. | |
| tile_index | int | The index, among all cards for the given policy, of the selected policy. | |
| connections | List[CardinalDirection] | The text content of the selected card. | |  

### **click_inspector_tab**

When the player clicks to switch to a particular tab of the inspector panel.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tab_name | str | Whether the tab is grain, dairy, or fertilizer | |  

### **building_queued**

When the player clicks a map point, adding a new building to the build queue. Note that a road may be 'queued' as the result of undo-ing a road destroy.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the building was placed. For roads, this is the 'start' tile, where the player started their click-drag to define the road. | |
| building_type | BuildingType | The specific type of building added to the queue. | |
| total_cost | int | The new running total cost in the build queue. | |
| funds_remaining | int | The remaining county funds, if the current queue is built (including the new building). | |  

### **building_dequeued**

When the player clicks a map point in destroy mode, removing a building to the build queue.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the player removed the building. For roads, this is the 'start' tile, where the player started their click-drag to define the road. | |
| building_type | BuildingType | The specific type of building removed from the queue. | |
| total_cost | int | The new running total cost in the build queue. | |
| funds_remaining | int | The remaining county funds, if the current queue is built (after the building is removed from the queue). | |  

### **click_build**

When the player clicks a map point, attempting to place a new building in the build queue.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the player tried to add the building. For roads, this is the 'start' tile, where the player started their click-drag to define the road. | |
| building_type | BuildingType | The specific type of building added to the queue. | |  

### **click_destroy**

When the player clicks a map point, attempting to destroy a building on the tile

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the player tried to destroy a building. | |
| building_type | BuildingType | The specific type of building, if any, on the tile. | |  

### **click_undo**

When the player clicks a map point, attempting to destroy a building on the tile

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_build_invalid**

When the player clicks a map point, attempting to place a new building in the build queue, but the selected tile is not a valid option.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the player tried to add the building. For roads, this is the 'start' tile, where the player started their click-drag to define the road. | |
| building_type | BuildingType | The specific type of building added to the queue. | |  

### **click_destroy_invalid**

When the player clicks a map point, attempting to destroy a building on the tile, but the tile does not contain a valid building to be destroyed

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the player tried to destroy a building. | |
| building_type | BuildingType | The specific type of building, if any, on the tile. | |  

### **click_execute_build**

When the player clicks to complete the building of all buildings in the build queue.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| built_items | List[BuildingType] | The specific buildings in the build queue. | |
| total_cost | int | The total cost of the buildings in the build queue. | |
| funds_remaining | int | The remaining county funds, after building all buildings in the queue. | |  

### **click_destroy_mode**

When the player clicks to enter destroy mode.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_confirm_destroy**

When the player clicks to confirm destruction of the selected... things to be destroyed. TODO: need to confirm this, like do we actually destroy existing buildings? And is there a queue-ing mechanism?

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **click_exit_destroy**

When the player clicks to leave destroy mode, without performing any destructions.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |  

### **select_building_type**

When the player selects a new type of building from the list of options to build

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | BuildingType | The specific type of building removed from the queue. | |
| cost | int | The cost to build the given building. | |  

### **hover_build_tile**

When the player hovers the mouse over a candidate tile for adding a new building

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile being hovered. | |
| is_valid | bool | Whether the given building type can be placed on the given tile. | |  

### **hover_destroy_tile**

When the player hovers the mouse over a candidate tile for destroying a building

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile being hovered. | |
| is_valid | bool | Whether the hovered tile has a building that can be destroyed. | |  

### **building_type_unlocked**

When a new building type is unlocked in the build list.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | BuildingType | The specific type of building that was unlocked. | |  

### **policy_unlocked**

When a new policy type is unlocked for the player's counties.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | PolicyType | The specific type of building that was unlocked. | |  

### **view_unlocked**

When a new view type is unlocked.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| building_type | ViewType | Which type of view was unlocked. | |  

### **algae_growth_begin**

When a new bloom begins to grow on a map tile

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the algae grew. | |
| algae_percent | float | The proportion of algae that already existed on the tile, at the time it began to grow. | |
| phosphorus_value | int | The amount of phosphorus on the tile, at the time it began to grow. | |  

### **algae_growth_end**

When a new bloom stops growing on a map tile, whether because it grew to its maximum or because the growth was stopped through good water management.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the algae grew. | |
| algae_percent | float | The proportion of algae that existed on the tile, at the time it stopped growing. | |
| phosphorus_value | int | The amount of phosphorus on the tile, at the time it stopped growing. | |  

### **skimmer_appeared**

When a new skimmer appears on a lake tile, as a result of policy funding for skimmers/dredgers.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the skimmer appeared. | |
| is_dredger | bool | Whether the skimmer that appeared is a dredger, or a regular skimmer. | |  

### **skimmer_disappeared**

When a skimmer leaves a lake tile, as a result of revoked policy funding for skimmers/dredgers.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the skimmer disappeared. | |
| is_dredger | bool | Whether the skimmer that disappeared was a dredger, or a regular skimmer. | |  

### **export_depot_spawned**

When the export depot spawns in the map.

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| tile_index | int | The index, within the global map, of the tile where the export depot appeared. | |  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**ActiveTime** : *timedelta*, *Aggregate feature*   
Active time of a player  
*Other elements*:  

threshold : 30  

**NumberOfSessionsPerPlayer** : *int*, *Aggregate feature*   
Number of sessions per player  
  

**CountyUnlockCount** : *int*, *Aggregate feature*   
ANumber of Counties unlocked  
  

**FailCount** : *int*, *Aggregate feature*   
Number of failure count  
  

**PersistedThroughFailure** : *int*, *Aggregate feature*   
Number of times faied a but persisted through the task  
  

## Other Elements  

Other (potentially non-standard) elements specified in the game's schema, which may be referenced by event/feature processors.  

### Other Ranges  

Extra ranges specified in the game's schema, which may be referenced by event/feature processors.

No changelog prepared

