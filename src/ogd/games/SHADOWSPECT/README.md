# Game: SHADOWSPECT

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

### **start_game**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| group | string | N/A | |
| version_num | string | N/A | |
| env_configs | dict{} | N/A | |
| game_id | string | N/A | |

#### Other Elements

- None  

### **login_user**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| game_id | string | N/A | |
| user | string | N/A | |
| group | string | N/A | |

#### Other Elements

- None  

### **disconnect**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |

#### Other Elements

- None  

### **exit_to_menu**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |

#### Other Elements

- None  

### **start_level**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| task_id | string | N/A | |
| set_id | string | N/A | |
| fullscreen | bool | N/A | |
| resolution | dict | N/A | |
| conditions | dict | N/A | |

#### Other Elements

- None  

### **puzzle_started**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| task_id | string | N/A | |
| set_id | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |

#### Other Elements

- None  

### **puzzle_complete**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| task_id | string | N/A | |
| set_id | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |

#### Other Elements

- None  

### **restart_puzzle**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |

#### Other Elements

- None  

### **create_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| color | int | N/A | |
| spawnPosition | dict | N/A | |
| input | string | N/A | |
| changeMode | bool | N/A | |
| objSerialization | int | N/A | |
| shapeType | int | N/A | |

#### Other Elements

- None  

### **delete_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| color | int | N/A | |
| input | string | N/A | |
| changeMode | bool | N/A | |
| deletedShapes | List[int] | N/A | |

#### Other Elements

- None  

### **select_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| newSelection | List[int] | N/A | |
| prevSelection | List[int] | N/A | |

#### Other Elements

- None  

### **deselect_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| newSelection | List[int] | N/A | |
| prevSelection | List[int] | N/A | |

#### Other Elements

- None  

### **select_shape_add**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| newSelection | List[int] | N/A | |
| prevSelection | List[int] | N/A | |

#### Other Elements

- None  

### **move_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| selectedObjects | List[int] | N/A | |
| prevPositions | List[dict] | N/A | |
| targetOffset | dict | N/A | |
| validMove | bool | N/A | |

#### Other Elements

- None  

### **rotate_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| selectedObject | int | N/A | |
| rotationOffset | dict | N/A | |

#### Other Elements

- None  

### **scale_shape**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| selectedObject | int | N/A | |
| newScale | dict | N/A | |
| prevScale | dict | N/A | |

#### Other Elements

- None  

### **mode_change**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| mode | int | N/A | |
| prevMode | int | N/A | |
| xfmMode | int | N/A | |
| prevXfmMode | int | N/A | |
| shape | int | N/A | |
| prevShape | int | N/A | |

#### Other Elements

- None  

### **click_nothing**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |

#### Other Elements

- None  

### **rotate_view**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| input | string | N/A | |
| freeformDrag | bool | N/A | |
| freeformRelease | bool | N/A | |
| targetCam | int | N/A | |
| prevCam | int | N/A | |

#### Other Elements

- None  

### **check_solution**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| correct | List[bool] | N/A | |

#### Other Elements

- None  

### **toogle_paint_display**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| isOpen | bool | N/A | |

#### Other Elements

- None  

### **palette_change**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| newPalette | int | N/A | |
| prevPalette | int | N/A | |
| changeMode | bool | N/A | |

#### Other Elements

- None  

### **paint**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| shapeIndex | int | N/A | |
| newColor | int | N/A | |
| prevColor | int | N/A | |

#### Other Elements

- None  

### **toggle_snapshot_display**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| isOpen | bool | N/A | |

#### Other Elements

- None  

### **snapshot**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| actionIndex | int | N/A | |
| cameraAngle | int | N/A | |

#### Other Elements

- None  

### **undo_action**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| input | string | N/A | |
| actionIndex | int | N/A | |
| targetedActionIndex | int | N/A | |

#### Other Elements

- None  

### **redo_action**

N/A

#### Event Data

| **Name** | **Type** | **Description** | **Sub-Elements** |
| ---      | ---      | ---             | ---         |
| user | string | N/A | |
| group | string | N/A | |
| timeStamp | double | N/A | |
| screenPos | dict | N/A | |
| input | string | N/A | |
| actionIndex | int | N/A | |
| targetedActionIndex | int | N/A | |

#### Other Elements

- None  

## Detected Events  

The custom, data-driven Events calculated from this game's logged events by OpenGameData when an 'export' is run.  

None  

## Processed Features  

The features/metrics calculated from this game's event logs by OpenGameData when an 'export' is run.  

**MoveShapeCount** : *int*, *Aggregate feature*   
Total number of shape moves in a given session  
  

**SessionID** : *str*, *Aggregate feature*   
The player's session ID number for this play session  
  

**FunnelByUser** : *List[float | int]*, *Aggregate feature*  (disabled)  
Funnel of puzzles for this play session  
  

**LevelsOfDifficulty** : *List[bool | int | timedelta]*, *Aggregate feature*   
Set of features for each level describing the difficulty of a puzzle (on-going-work)  
  

**SequenceBetweenPuzzles** : **, *Aggregate feature*  (disabled)  
Sequence of puzzles and its funnel stage reached of a given session  


No changelog prepared

