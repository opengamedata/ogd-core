## Adding a new game data exporter/extractor:

First, a bit of terminology:
- feature: Some bit of data considered to be useful for analysis of game play. Usually calculated from game event data.
- per-level feature: A feature that records data about what a player did over the course of a level in the game. 
- per-custom-count feature: A feature that records data about some _thing_ that may have multiple instances over a gameplay session. A common example would be question-answer prompts. 
- aggregate feature: A feature which records data across an entire gameplay session (as opposed to an individual level, for example). 
- raw csv: A csv file containing raw game event data. More-or-less a database dump, but with JSON objects split across columns.
- processed csv: A csv file primarily containing feature data. This typically includes a great many per-level features (i.e. one instance of each feature per game level), a few per-custom-count features, and a moderate number of aggregate features.

In order to add a new game to the feature extraction tool, complete the following steps:

1. First, we must define some things about the data we are extracting. We do this in a JSON file, under the **schemas/JSON** folder.
By convention, the name of the JSON file should be the same as the game ID used in the database.  
e.g. For the "Wave" game, the database uses an app_id of `WAVES`, so we name the JSON schema file as **WAVES.json**
A JSON schema file has three elements:
   - `db_columns`: This element should be a dictionary mapping the names of each column in the database table to a string describing the column.
   - `events`: This element should be a dictionary mapping names of event types to sub-dictionaries defining the data in the events.
      - These sub-dictionaries are similar to the db_columns dictionary. They map each property name for a given event type to the type of that property.
   - `features`: This element should in turn contain three elements:
      - `perlevel`: This sub-element should be a dictionary mapping the names of per-level features to descriptions of how the features are calculated.
      - `per_custom_count`: This sub-element should be a dictionary mapping the names of features which are repeated for some specific number of times to a subdictionary. This, again, has three elements:
         - `count`: The number of times the feature is repeated
         - `prefix`: The prefix to use to distinguish repeats of the feature in the output file
         - `desc`: A description of how the feature is calculated
        
        Note, if you know a priori the number of levels in your game, you may enter all your `perlevel` features as `per_custom_count` features. The only difference between the two is that `perlevel` features have a hard-coded prefix ("lvl") and the number of levels is inferred from the max level in the database.
     - `aggregate`: This sub-element should be a dictionary mapping the names of features aggregated over a whole session to descriptions of how the features are calculated.
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
   - `extractFromRow(self, level, event_data_complex_parsed, event_client_time)`: This function is responsible for extracting feature data from a single database entry. The `level` and `event_client_time` tell us what level the event came from (so we know which level to use for per-level features), and when the event occurred (useful for features tracking time per level, for example). `event_data_complex_parsed` is a dictionary, parsed from JSON in the `event_data_complex` column of the database. If step 1 was completed correctly, the `event_data_complex_parsed` ought to match one of the `event`s from the JSON schema.
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
     Also note that in general, we use `event_data_complex_parsed["event_custom"]` to distinguish event types. Even if the original database entry did not have `event_custom` as a part of the JSON, the `ProcManager` class will insert the value of the `event` database column as `event_custom` in the `event_data_complex_parsed` object, so there is at least _some_ way to tell what type of event is being processed.
    - `calculateAggregateFeatures(self)`: This function should use the values in its per-level and per-custom-count features to calculate the aggregate (across whole session) features. The code for calculating individual aggregate features may be broken into separate private functions if desired, although in practice most aggregate features can be calculated with just a couple lines of code apiece, so this is not usually necessary. This function will generally be called just once during each extractor's lifetime, after all rows corresponding to that session have been processed. 