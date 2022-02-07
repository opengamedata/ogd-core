## Adding a new realtime model for the dashboard project:

First, a bit of terminology:
- **event**: A record of some game event, stored as a single row in the database.
- **feature**: Some bit of data considered to be useful for analysis of game play. Usually calculated on a per-session basis from event data.
- **model**: A function of gameplay data that returns a value indicating something about the gameplay session. While the real-time model system is intended for use with machine-learning or statistical models, this definition is broad enough to include very simple calculations. For example, a model which merely returns the value of a single feature is considered valid under this definition.

From a high level, the realtime code maintains a list of valid models for a particular game. The dashboard front-end sends requests with a list of desired models and sessions to evaluate against those models. The realtime code retrieves data from the session(s), evaluates the model(s), and sends back the results. Adding a new model consists of 3 steps:
1. Create a class with an `Eval(...)` function (or choose an existing class).
2. Add a call to the class constructor in the `ModelManager` code.
3. Register the model, with desired parameters, in a `{app_id}_models.json` file.

Below, we will cover the steps in detail.
1. The first step towards setting up a new realtime model is to create a subclass of the `Model` class.
    A model stores a list of valid levels (or an empty list, if the model is valid for all levels), as well as an "input type."  
    _Note: The need for an input type is an unfortunate result of the fact that some models may use feature data for a session, while others may require access to the raw event data for sequence-based analysis. Separating the input types allows us to automatically parse and send feature data at a single point in the code, rather than requiring each feature-based model to individually include code to run a feature extraction._

    The other important feature of a Model is the `Eval(...)` function. This function receives one or more rows of data, with a form depending on the input type, and evaluates the data against the model to return a result.
    In the case of a linear regression model, for example, the `Eval(...)` function will return a linear combination of feature values, with coefficients determined at model training time.

    To simplify the issue of controlling input types, we provide `FeatureModel` and `SequenceModel` subclasses of `Model`. These simply hard-code the input type passed to the super constructor, so further subclasses need not be concerned with managing the input type. Simply choose either `FeatureModel` or `SequenceModel` as the parent of your new model class.  
    Do note, however, that `FeatureModel` and `SequenceModel` each implement `Eval(...)` with a call to an abstract function `_eval(...)`. **Thus, you should implement the** `_eval(...)` **function when subclassing from** `FeatureModel` **or** `SequenceModel`.

    While your model may be entirely self-contained within the `Model` subclass, you can also add parameters for the class constructor (the `__init__` function, in our case). This allows for easy creation of multiple instances of models of the same type. Consider, for example, the constructor for the `LogisticModel` class:
    ```python
    class LogisticModel(FeatureModel):
        def __init__(self, coefficient_map: typing.Dict[str, float], levels: typing.List[int] = []):
            super().__init__(levels)
            self._coeff_map = coefficient_map
    ```
    This class constructor accepts a `coefficient_map` parameter, which maps feature names to coefficient values.  
    _Note: all `Model` subclass constructors should accept a `levels` parameter, which is passed to the super constructor. It is fine to default to an empty list; this will simply mean the model is interpreted as valid for all levels._  
    The parameters for a specific model instance are set in the {game_name}_models.json file, discussed in a later step.

    A final note, regarding naming of `Model` subclasses.
    You may choose any name you wish, but we recommend a naming convention of `PrefixModel`, where "Prefix" is a description of the model type being implemented. For examle, `LogisticModel` for a class that implements a logistic regression model, or `NeuralModel` for a neural net implementation.

2. Once the `Model` subclass is in place, we need some line of code that calls the subclass constructor to create model instances. 
    This is done at a single point, in the `ModelManager` class, within the `LoadModel(...)` function. Here is a sample of the code:
    ```python
    def LoadModel(self, model_name: str):
        model_info = self._models[model_name]
        if model_info["type"] == "SingleFeature":
            return SingleFeatureModel(**model_info["params"])
        elif model_info["type"] == "Logistic":
            return LogisticModel(**model_info["params"])
        ...
    ```
    Whenever you add a new `Model` sublclass, then, you must add a new case to the `if-elif-else` block. The format should be copied exactly from existing cases, but you must a) replace the string being **compared against** the `model_info["type"]` with a model name of your choosing, and b) replace the class name in the `return` statement with the name of your new subclass.
    In addition, you must add an import at the top of the `ModelManager` file.

    As with the name for your `Model` subclass, the name here may be anything you choose, provided the choice does not conflict with existing cases.
    However, in keeping with the naming convention recommended in step 1, we recommend using the "Prefix" portion of the class name as the type name here.
    Re-using the `NeuralModel` example from before, we would add the following import, assuming the `NeuralModel` class resides in the `models` folder alongside the existing model classes:
    ```python
        from models.NeuralModel import NeuralModel
    ```
    Further, we would add the following code to `LoadModel`:
    ```python
        if model_info["type"] == "Neural":
            return NeuralModel(**model_info["params"])
    ```

 3. The final step in adding a new `Model` subclass is to register a new instance in the `{app_id}_models.json` file. Here, `{app_id}` is an all-caps identifier for the game on whose data the model is based.
    It is the same as the `app_id` column value for the game's events in the database.
    Within each of these `{app_id}_models.json` files, we have a series of entries corresponding to instances of our `Model` subclasses.
    The JSON key for each entry is the name of the instance, and the value for each entry is a dictionary containing entries for `"type"`, `"levels"`, and `"params"`.

- The `"type"` is whatever string was chosen for the `==` comparison in the `if-elif-else` block in step two.
    This is what allows the `ModelManager` to determine the correct type of model to instantiate.
    Again, if following our naming convention, this is the prefix portion of the `Model` subclass name.  
- The `"levels"` entry specifies at which levels of the game the player data may be evaluated. For example, if a model was trained on data from levels 8-10 of a game, you may choose to specify `"levels" : [8, 9, 10]` in the JSON file.
    In this case, the system will only evaluate the model if a given player is in one of those three levels.
    If you leave `"levels"` as an empty list, the system will assume the model is valid for **all** levels.  
- `"params"` specifies the arguments to be passed to a `Model` subclass' *unique* parameters.
    That is, any parameters additional to the `levels` parameter required by the `Model` base class.
    The `"params"` should be specified as a dictionary of parameter-argument pairs.
    For example, if a model requires parameters `a`, `b`, and `c`, then the `"params"` entry should have the following form:
    ```json
    "params" : {"a": 1.5, "b": 3.14, "c": 618}
    ```

    Here is an example for a full model instance for a linear regression using the `sess_count_achievements` and `sess_count_deaths` features from Lakeland:
    ```json
    "MyLogisticModel": {
        "type": "Logistic",
        "levels": [],
        "params": {
            "coefficient_map": {
                "sess_count_achievements": 0.5,
                "sess_count_deaths": 0.25,
                "intercept": 1.4
            }
        }
    }
    ```
    This is all that is required to add new instances of a model.
    Thus, if a type for the model you wish to add already exists, the first two steps of this process may be skipped, and you can simply register a new instance in the JSON file.
    In this way, the system nicely supports code re-use, and makes the addition of new model instances very simple.