## Data Logging Info:
See https://github.com/fielddaylab/jo_wilder/blob/master/README.md

Jo Wilder data is organized into levels, where each level corresponds to a "save code"/chapter in the game.
Many of the extracted features, however, are based on individual interactions with the environment, or game objectives.

## Survey
Survey questions are listed below, where each question is mapped to an index:
    0: 'What grade are you in?',
    1: 'How well do you read in English?',
    2: 'The game grabs my attention.',
    3: 'I like watching TV shows about history.',
    4: 'Jo is friendly.',
    5: 'I think the characters are funny.',
    6: 'The characters say things that make me laugh.',
    7: 'Time flies while I\'m playing the game.',
    8: 'I like reading about history.',
    9: 'I like Jo.',
    10: 'Jo is kind.',
    11: 'The characters say funny things.',
    12: 'I forget what\'s around me while playing the game.',
    13: 'I like learning history very much.',
    14: 'I think learning history is fun.',
    15: 'I can relate to Jo.',
    16: 'The characters are entertaining.',
    17: 'I feel emotionally involved in the game.'

Survey responses are logged as an integer in `SA{num}_sa_index`, with the text response logged in `SA{num}_sa_text`. Possible responses for each question:
- For question 0 ('What grade are you in?'): 0: '3rd', 1: '4th', 2: '5th', 3: '6th', 4: 'Other'
- For question 1 ('How well do you read in English?'): 0: 'Not a very Good Reader', 1: 'An OK Reader', 2: 'Very Good Reader'
- For remaining **EVEN**-indexed questions: 0: 'Disagree', 1: 'Somewhat Disagree', 2: 'Neutral', 3: 'Somewhat Agree', 4: 'Agree'
- For remaining **ODD**-indexed questions, responses are **reverse coded**: 0: 'Agree', 1: 'Somewhat Agree', 2: 'Neutral', 3: 'Somewhat Disagree', 4: 'Disagree'
