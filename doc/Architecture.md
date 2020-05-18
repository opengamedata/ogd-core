**This document gives a general overview of the various pieces of code in the opengamedata project.**  

#### Basic Categories
The project code has three primary parts:
1. **Extraction** code to extract features from raw game log data, retrieved from a database.
2. **Export** code to perform feature extraction at scale, and export the data to files for distribution/archival.
3. **Evaluation** code to run features of a game session through models (generated from past game data), and output model-based predictions.

#### Location(s) of code by category
The extraction code is primarily located in feature_extractors folder, and makes use of data in the schemas folder. Export code mostly lives in the managers folder, and is invoked from main.py. Evaluation code is, at the time of writing, wrapped up in RTServer.py, which was part of a dashboard prototype. In future development, these should be separated somewhat.
Evaluation and Export code make heavy use of the Extraction code.

#### Code hierarchy and structure
The general structure and data flow for the **exporter** code is as follows:  
1. At the highest level, we have main.py. This is the file you run to set off the whole process. The code in main loads the program settings and constructs a "request" for the ExportManager module, which holds the core logic for the process. The details of the request are determined by the command-line args given to main.
2. The next level is ExportManager.py. This is where we do the high-level export processing. Given the export request, ExportManager will load additional data for the game specified by the request, retrieve data for that game from the database, and export both raw and processed csv files.
The "additional data" includes:
   - a GameTable, which has information on the database table with game data, and "what" data is available.
   - a Schema, which has information on the structure of the stored game data itself. Specifically, this deals with data encoded within a string in a specific database column.
   
   ExportManager makes use of two further "manager" classes (one for raw data, one for processed), which each provide functions for processing a single row, and writing out accumulated data to a file. This means ExportManager is only directly responsible for checking the number of sessions available for the game, and retrieving the rows for each session. It then passes each row to the RawManager and the ProcManager, and periodically uses the managers to write the data to file.
   Finally, ExportManager maintains a JSON file with data on all exported csv files.
3. a. RawManager.py is responsible for the details of processing each database row. This basically amounts to splitting any columns that contain JSON data into multiple smaller columns, and ensuring any columns which may have commas in them (strings, sub-objects) are wrapped in quotes. Each time a row is processed, the corresponding csv line is added to a list, which may be written to file at any time. Note, RawManager has a ClearLines function, which should be (and presently is) called after using the WriteRawCSVLines function to avoid writing duplicate lines.
3. b. ProcManager.py has similar responsibilities to RawManager, however the details of processing a row are somewhat more complicated. Because a processed csv has features calculated from data, rather than simply being a lightly processed version of the raw data itself, there is a lot of variation between games. Thus, ProcManager further defers details to Extractor classes, each instance of which can maintain feature data for one session. ProcManager simply makes use of the `extractFromRow` function provided by each Extractor, as well as an Extractor function for writing data to a given file. ProcManager also has a function for calculating aggregate features of all sessions, which should generally be used before writing data to csv.
4. The Extractor classes are based on Extractor.py, which is an abstract class defining a few functions that operate across all subclasses, and a few abstract functions which should be implemented by each subclass.
The abstract functions are `extractFromRow` and `calculateAggregateFeatures`, which are the two points that vary from game to game. Each implementation of `extractFromRow` should handle all possible event types (each row represents one event) for the given game. These events are documented in the game's Schema file.
An extractor stores feature data in a private class, which provides functions for accessing and modifying features by name (useful for aggregate features) or index (e.g. index may be level or question number).

The **evaluator** code is somewhat wrapped up in the code for a real-time dashboard, at present. Future development should result in a cleaner separation of features. The list below is thus less of a hierarchy, more of a description of where each piece (and examples of use) can be found in the code.
1. RTServer.py contains the function of interest for evaluating models, called EvaluateLogRegModel (at present, we are only using logistic regression models; this should expand in the future). This function accepts a "model" and feature data for a given play session. 
2. Models are stored as json files, which at the least must map the "code" name of a model to a corresponding dictionary. The model dictionary maps input parameter names to coefficient values, and at the least will map "display name" to a nicely formatted string used to display the name of the model in an end-user application. It is this dictionary that gets passed to EvaluateLogRegModel.
3. The clearest example for using models is in getPredictionsBySessID within RTServer.py. This uses a model file that adds an extra level to the JSON, separating models by the game level for which they are intended.

In the future, the intent is to have a separate module for model evaluation, which would allow us to do things like run models on test data, and export results for evaluation of model effectiveness, or creation of model benchmarks.


