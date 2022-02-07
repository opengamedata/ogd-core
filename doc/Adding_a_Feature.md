In order to add a new feature for a game, you must complete the following steps:

1. **Code a feature extractor**
In this step, you need to write the individual feature extractor.
This should be a python file, placed in the `<ogd-core-root>/games/<GAME_NAME>/extractors` folder, which inherits from the Feature class.
At minimum, you must create an `__init__(...)` function, and implement the `GetEventTypes(self)`, `CalculateFinalValues(self)`, and `_extractFromEvent(self, event)` functions.
You are free to add whatever `__init__` parameters you like, but you should at least include parameters to map to `name`, `description`, and `count_index` when calling the superclass constructor.
Do not change the parameters of the other functions, as they are implementing abstract functions of the base class.  
    - `GetEventTypes` should simply return a list of the names of the events your Feature would like to analyze.  
    *For example*, a feature to calculate the time spent on a level should request the game's "start level" and "end level" events.  
    - `_extractFromEvent` will run once on each occurrence of an event whose type is requested in `GetEventTypes`.
    This function is where you will tabulate whatever data you need from individual events.  
    *For example*, a feature to calculate the number of times a player clicked a button would create a "count" variable in its `__init__` function, and increment that variable here.
    - `CalculateFinalValues` should return whatever the "metric" or value of the Feature is, given whatever events have been seen so far.  
    *For example*, a function to calculate the average number of moves a player made in a level would count the moves and levels started in `_extractFromEvent`, then divide the move count by the number of levels in this function.
    Finally, it would return the calculated average.

2. **Add feature to extractors package**
Next, you need to ensure your new feature is included when the top-level Extractor class imports the `extractors` folder.
Open the `<ogd-core-root>/games/<GAME_NAME>/extractors/__init__.py` file, which should look something like this:

    ```python
    __all__ = [
        "AverageLevelTime",
        "LevelCompletionTime",
        "SessionDuration",
        "SessionID",
    ]

    from . import AverageLevelTime
    from . import LevelCompletionTime
    from . import SessionDuration
    from . import SessionID

    ```

    Add the name of your feature class to the `__all__` list, and add the `import` for your feature class in the list of imports below.

3. **Register feature in the top-level Extractor**
Now, we must ensure your game's Extractor class knows how to load actual instances of your Feature.
This will be done in the `<ogd-core-root>/games/<GAME_NAME>/<GameName>Extractor.py` file
(as an aside, note that the convention is to name the `<GAME_NAME>` folder with ALL CAPS, while the naming convention for Extractor classes is to use PascalCase).
Open up the `<GameName>Extractor.py` file, and look for the `_loadFeature` function, whose body should look something like this:

    ```python
    def _loadFeature(self, feature_type:str, name:str, feature_args:Dict[str,Any], count_index:Union[int,None] = None) -> Feature:
        ret_val : Feature
        if feature_type == "AverageLevelTime":
            ret_val = AverageLevelTime.AverageLevelTime(name, feature_args["description"])
        elif feature_type == "LevelCompletionTime":
            ret_val = LevelCompletionTime.LevelCompletionTime(name, feature_args["description"], count_index)
        elif feature_type == "SessionDuration":
            ret_val = SessionDuration.SessionDuration(name, feature_args["description"])
        elif feature_type == "SessionID":
            ret_val = SessionID.SessionID(name, feature_args["description"], self._session_id)
        else:
            raise NotImplementedError(f"'{feature_type}' is not a valid feature for Aqualab.")
        return ret_val

    ```

    Add a case for your new Feature class, checking if `feature_type` matches the name of your Feature class (more specifically, you're checking if it matches the name you give your feature in the configuration file in step 4, but using the name of the Feature class is a *strongly recommended* convention).
    Within this case, set the `ret_val` to a new instance of your Feature, passing in whatever parameters you added to your `__init__` function.
    Note that any parameters you add to `__init__` must be for data the top-level Extractor class can access and pass to the constructor.

4. **Add feature configuration to the game's schema**
    All of the coding required was covered in the first three steps.
    You wrote the code to perform extraction, then registered the class in the set of extractors, and added code to create instances of your Feature extractor.
    The final step is to adjust the configuration for the game, so that the system will include the Feature when performing data exports.
    Here, you will need to open `<ogd-core-root>/games/<GAME_NAME>/<GAME_NAME>.json`.
    This file will have the following layout:
    ```json
    {
        "level_range": { 
            ...
        },

        "events": {
            ...
        },

        "features": {
            "per_count": {
                "LevelCompletionTime": {
                    "enabled": false,
                    "count":"level_range",
                    "prefix": "job",
                    "description": "Time taken to complete a given level"
                },
            },
            "aggregate":{
                "AverageLevelTime": {
                    "enabled": false,
                    "description":"Average time spent per level played"
                },
                "SessionDuration": {
                    "enabled": true,
                    "description":"Time spent playing in a given session"
                },
                "SessionID": {
                    "enabled": true,
                    "description":"The player's session ID number for this play session"
                }
            }
        },

        "db_columns": {
            ...
        },
        "config": {
            ...
        },
    }

    ```

    Note that the ellipses are stand-ins for the actual content found in the file - those contents are not important for this step.  
    You will add a configuration for your feature in the features dictionary.
    There are two fundamental kinds of features:  

    - "aggregate" features, which will have one instance per gameplay session (e.g. the overall duration of a session).
    These are also called "session" features.  
    - "per-count" features, which will have a defined number of instances for each session (e.g. the time spent individually on each level, or responses to each of four pre-game survey questions).

    If your Feature is meant to function as an "aggregate" feature, you will add it to the `aggregate` dictionary.
    Each item maps the name of the Feature to a sub-dictionary.
    We **strongly** recommend using the name of your `Feature` subclass (as created in step 1) as the name here, although technically you may use any name you want.  
    The sub-dictionary for your Feature needs two elements: "enabled" and "description," where "enabled" is a boolean telling the system whether to use this Feature, and "description" is a human-readable description of what the Feature calculates.
    If desired, you can add extra elements to the sub-dictionary for use as parameters of your Feature.
    For example, if you would like to parameterize a feature to use either the mean or median as a measure of center, you could add the following to your `aggregate` dictionary:

    ```json
    "TypicalLevelTime" : {
        "enabled" : true,
        "center" : "median",
        "description" : "Calculates either the player's average or median level time, depending on the parameter"
    }
    ```

    You would then have access to the parameter in step 3 (adding the feature to `_loadFeature`) as an element of `feature_args`.

    On the other hand, if your Feature is meant to function as a "per-count" feature, you'll add it to the `per_count` dictionary.
    The process is similar to adding a feature to `aggregate`, requiring "enabled" and "description" as elements.
    In the "per-count" case, you will need to include "count" and "prefix" elements as well.
    - Here, the "count" is an integer telling the system how many instances of the Feature to create for each gameplay session.  
    *For example*, if your Feature records responses to each of four survey questions in a game, you'll want to set count to 4.
    Then each session will get four instances of the feature, numbered 0, 1, 2, and 3.  
    As a convenience, you may set count to the string "level_range", and the system will use the range of values defined in "level_range" within the `<GAME_NAME>.json` file.
    This is not a general feature, and any other strings will fail.
    The feature only exists because many games have a concept of level, and levels are often a useful unit of analysis.
    When in doubt, default to using an integer value for the count.
    - The "prefix" element maps to a string, which will be used to help distinguish different classes of per-count feature.  
    *For example*, suppose you have ClickCount as a feature counting number of clicks on each level, and Response as a feature recording survy responses.
    You might choose "level" as a prefix for ClickCount, and "survey" as a prefix for Response.
    Then the final feature names for each of those Feature instances will be:  
    ```level0_ClickCount, level1_ClickCount, level2_ClickCount, ... , survey0_Response, survey1_Response, ...```  
    When browsing columns in a spreadsheet of Feature values, it becomes much easier to distinguish which features occur per-level, which occur per-survey-item, etc.

    As with "aggregate" features, "per-count" features can have additional elements in their sub-dictionaries, which can then be accessed for use as parameters in the `feature_args` variable in `_loadFeature`.
