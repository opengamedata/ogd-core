## Data Logging Info:
See https://github.com/fielddaylab/jo_wilder/blob/master/README.md
  
#### Levels
Jo Wilder data is organized into levels, where each level corresponds to a "save code"/chapter in the game.
  
| Index | Name |
| --- | --- |
|0|startgame|
|1|notebook|
|2|wiscwonders|
|3|mystery|
|4|plaque|
|5|notajersey|
|6|trashed|
|7|archivist|
|8|textile|
|9|logbook|
|10|suffragist|
|11|taxidermist|
|12|wellsdidit|
|13|saveteddy|
|14|scratches|
|15|hesalive|
|16|akey|
|17|rescued|
|18|backtowork|
|19|sadanimals|
|20|flaglady|
|21|ecologists|
|22|donethework|
|23|sunset|

#### Interactions and Objectives
  
Many of the extracted features are based on individual [interactions](https://github.com/opengamedata/opengamedata-core/blob/master/games/JOWILDER/interaction_metadata.json) with the environment, or game [objectives](https://github.com/opengamedata/opengamedata-core/blob/master/games/JOWILDER/jo_wilder_fqid_to_enum.json). Linked here are JSON files mapping each interaction and objective to the index it will have in the resulting features data.

#### Survey
Players are given the following survey questions to answer throughout the game.

| Index | Question |
| --- | --- |
|0|What grade are you in?|
|1|How well do you read in English?|
|2|The game grabs my attention.|
|3|I like watching TV shows about history.|
|4|Jo is friendly.|
|5|I think the characters are funny.|
|6|The characters say things that make me laugh.|
|7|Time flies while I'm playing the game.|
|8|I like reading about history.|
|9|I like Jo.|
|10|Jo is kind.|
|11|The characters say funny things.|
|12|I forget what's around me while playing the game.|
|13|I like learning history very much.|
|14|I think learning history is fun.|
|15|I can relate to Jo.|
|16|The characters are entertaining.|
|17|I feel emotionally involved in the game.|

#### Survey Responses
  
For question 0 ("What grade are you in?"):
| Index | Response |
| --- | --- |
|0|3rd|
|1|4th|
|2|5th|
|3|6th|
|4|Other|

For question 1 ("How well do you read in English?"):
| Index | Response |
| --- | --- |
|0|Not a very Good Reader|
|1|An OK Reader|
|2|Very Good Reader|

For remaining **EVEN**-indexed questions:
| Index | Response |
| --- | --- |
|0|Disagree|
|1|Somewhat Disagree|
|2|Neutral|
|3|Somewhat Agree|
|4|Agree|

For remaining **ODD**-indexed questions, responses are **reverse coded**:
| Index | Response |
| --- | --- |
|0|Agree|
|1|Somewhat Agree|
|2|Neutral|
|3|Somewhat Disagree|
|4|Disagree|
