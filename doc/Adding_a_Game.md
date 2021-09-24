# Adding a new game data exporter/extractor:

First, a bit of terminology:
- **feature**:
    Some piece of *data*, useful for analysis, that we can observe from gameplay event logs, **and/or** the code that extracts the observation from event logs.
    For example, a feature could be as simple as a boolean representing "player started level 1."
    On the other hand, a feature could be very complex, such as a string encoding the entire sequence of a gameplay session.
    In OpenGameData, we write implementations of an abstract `Feature` class, where each implementation calculates one feature given event logs as input.  
    Features may be calculated at varying levels, described in the following definitions:
- **per-session feature**: 
    A feature that records data across an entire gameplay session.
- **per-custom-count feature**:
    A feature that records data about something that may have multiple instances over a gameplay session.
    This could include levels (i.e. a feature may be "clicks in the level", and there are 20 levels), survey prompts, in-game quizzes, etc.
- **per-level feature**:
    A per-custom-count feature that records data specifically about each level in a game.
    This is a sort of "informal" feature in OpenGameData - there are special features available to make Feature development easier for games that include a notion of "level," but these features are optional. 
- **population feature**:
    A feature that records data across many sessions of gameplay.

In order to add a new game to the feature extraction tool, complete the following steps:

1. First, we must define some things about the data we are extracting. We do this in a JSON file, under the **games/<GAME_ID>** folder.
The name of the JSON file should be the same as the game ID used in the database, by convention in all-caps.  
e.g. For the "Wave" game, the database uses an app_id of `WAVES`, so we name the JSON schema file as **WAVES.json**
A JSON schema file has three elements:
   - `events`:
        A description of the event-specific data encoded in each database row.
        This element should be a dictionary mapping names of event types to sub-dictionaries defining the data in the events.
        - These sub-dictionaries are similar to the db_columns dictionary. They map each property name for a given event type to the type of that property.
   - `features`:
        A description of what features OGD should produce, given the events described above.
        This element should in turn contain four sub-elements:
        - `per_level`: This sub-element should be a dictionary mapping the names of per-level features to descriptions of how the features are calculated/used.
        - `per_session`: This sub-element should be a dictionary mapping the names of features aggregated over a whole session to descriptions of how the features are calculated/used.
        - `per_game`: This sub-element should be a dictionary mapping the names of per-game features to descriptions of how the features are calculated/used.
        - `per_custom_count`: This sub-element should be a dictionary mapping the names of features which are repeated for some specific number of times to a subdictionary. This, again, has three elements:
            - `count`: The number of times the feature is repeated
            - `prefix`: A prefix to use to distinguish repeats of the feature in the output file
            - `desc`: A description of how the feature is calculated
    - `db_columns`:
        A description of the structure of the database table.
        This element should be a dictionary mapping the names of each column in the database table to a string describing the column.
        
    - `level_range` (optional):
        You may optionally add the `level_range` element to your JSON schema, which must be a sub-dictionary with `min` and `max` as its elements.
        If you do so, you can then use `level_range` as the `count` for a per-count feature (more information in the "Adding a Feature" doc).
    
`db_columns` is used to ensure the raw csv file metadata contains descriptions of each database column. `events` are used to get names for the members of each kind of event so we can extract features (and create columns in the raw csv). `features` are used to ensure the processed csv file metadata contains descriptions of each feature, and to help document the features for whoever writes the actual feature extraction code.
Below is a sample of JSON schema formatting:
```javascript
{
    "db_columns": {
        "id":"Unique identifier for a row",
    },

    "events": {
        "ARROW_MOVE_RELEASE": {
            "event_custom":"string",
            "begin_val":"float",
            "end_val":"float"
        }
    },

    "features": {
        "perlevel": {
            "totalSliderMoves":"slider moves across a given level",
        },
        "per_custom_count": {
            "questionAnswered" : {"count" : 4, "prefix": "QA", "desc" : "The answer the user gave to a given question (or -1 if unanswered)"},
        },
        "aggregate": {
            "avgSliderMoves" : "totalSliderMoves averaged over all levels",
        }
    }
}
```

2. Next, we need to create the feature extractor. This will be a Python class inheriting from the `Extractor` base class. By convention, the class should use the database app_id as a prefix for the class name, but use CamelCase even if the app_id is not formatted as such.
e.g. For the "Wave" game, we would name the extractor `WaveExtractor` (as opposed to `app_id + "Extractor` => `WAVEExtractor`).
The `Extractor` subclass *must* implement the following functions:
   - `__init__(self, session_id, game_table, game_schema)`: At minimum, this function should call the super constructor. `session_id` has the id of the session we are extracting data from, `game_table` contains information about the database table, and `game_schema` contains the data from the schema we defined in step 1. The super constructor initializes all features to have values of 0. If a different default value is preferred for any features, it would be a good idea to set those values here, after calling the super constructor.
   - `extractFromRow(self, row_with_complex_parsed, game_table)`: This function is responsible for extracting feature data from a single database entry. The `row_with_complex_parsed` should a row returned from the database, but with the item at `event_data_complex` already parsed into a Python dictionary from JSON. If step 1 was completed correctly, the `event_data_complex` ought to match one of the `event`s from the JSON schema.
   The `game_table` holds information about the layout of the database table, as usual. It can be used to get items from the row at specific columns.
   This function should contain code to handle extraction from each `event` type. By convention, the actual extraction code should be split into separate private functions for each `event` type, so that we can get a cleanly-formatted `extractFromRow` function, as below:
     ```python
        event_type = event_data_complex_parsed["event_custom"]
        if event_type == "BEGIN":
            self._extractFromBegin(level, event_client_time)
        elif event_type == "COMPLETE":
            self._extractFromComplete(level, event_client_time)
        elif event_type == "SUCCEED":
            # etc.
     ```  
     Each private function should then update feature values as needed:
     ```python
        def _extractFromComplete(self, level, event_client_time):
            self.end_times[level] = event_client_time
            self.features["completed"][level]["val"] = 1
     ```
     Also note that in general, we use `row_with_complex_parsed["event_data_complex]["event_custom"]` to distinguish event types. Even if the original database entry did not have `event_custom` as a part of the JSON, the `ProcManager` class will insert the value of the `event` database column as `event_custom` in the `row_with_complex_parsed["event_data_complex]` object, so there is at least _some_ way to tell what type of event is being processed.
    - `calculateAggregateFeatures(self)`: This function should use the values in its per-level and per-custom-count features to calculate the aggregate (across whole session) features. The code for calculating individual aggregate features may be broken into separate private functions if desired, although in practice most aggregate features can be calculated with just a couple lines of code apiece, so this is not usually necessary. Also, note that while the function is intended for aggregate feature calculation, in practice you may also need to calculate certain final values of per-level/count features here as well. For example, a feature which gives an average over a level can't be calculated until we know all events for that level have been encountered. Hence, it would be recommended to accumulate a total in extractFromRow, and calculate the average in calculateAggregateFeatures. This function will generally be called just once during each extractor's lifetime, after all rows corresponding to that session have been processed. 

3. Next, we need to ensure DataToCSV knows what the possible games are. In the section of code (presently around line 70) dealing with loading of the schema file, we need to add a case to the if-elif-else block. It should check if the request object has a game_id matching our new game, and if so, we must call the Schema constructor with the name of the schema file from step 1, and we must set `game_extractor` to the Extractor class we created for the game. For example:
```python
    if request.game_id == "WAVES":
        game_schema = Schema(schema_name="WAVES.json")
        game_extractor = WaveExtractor
```

4. Once those three steps are completed, the only thing left is to call DataToCSV with a request using the new game's app_id. This is usually done from main.py.