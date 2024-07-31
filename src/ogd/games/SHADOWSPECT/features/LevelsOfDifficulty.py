# import libraries
from typing import Any, List
import json
import pandas as pd
import numpy as np
import json
import hashlib
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict
# import locals
from ogd.core.generators.Generator import GeneratorParameters
from ogd.core.generators.extractors.SessionFeature import SessionFeature
from ogd.core.models.FeatureData import FeatureData
from ogd.core.models.Event import Event
from ogd.core.models.enums.ExtractionMode import ExtractionMode

pd.options.mode.chained_assignment = None  # default='warn'
    
listActionEvents = ['move_shape', 'rotate_shape', 'scale_shape',
                    'check_solution', 'undo_action', 'redo_action',
                    'rotate_view', 'snapshot', 'mode_change',
                    'create_shape', 'select_shape', 'delete_shape', 'select_shape_add']

orderMapping = {'1. One Box': 1, '2. Separated Boxes': 2, '3. Rotate a Pyramid': 3, '4. Match Silhouettes': 4, '5. Removing Objects': 5, '6. Stretch a Ramp': 6, '7. Max 2 Boxes': 7, '8. Combine 2 Ramps': 8, '9. Scaling Round Objects': 9,
                'Square Cross-Sections': 10, 'Bird Fez': 11, 'Pi Henge': 12, '45-Degree Rotations': 13,  'Pyramids are Strange': 14, 'Boxes Obscure Spheres': 15, 'Object Limits': 16, 'Warm Up': 17, 'Angled Silhouette': 18,
                'Sugar Cones': 19,'Stranger Shapes': 20, 'Tall and Small': 21, 'Ramp Up and Can It': 22, 'More Than Meets Your Eye': 23, 'Not Bird': 24, 'Unnecesary': 25, 'Zzz': 26, 'Bull Market': 27, 'Few Clues': 28, 'Orange Dance': 29, 'Bear Market': 30}

# mapping to positions
typeMapping = {'1. One Box': 'Basic Puzzles', '2. Separated Boxes': 'Basic Puzzles', '3. Rotate a Pyramid': 'Basic Puzzles', '4. Match Silhouettes': 'Basic Puzzles', '5. Removing Objects': 'Basic Puzzles', '6. Stretch a Ramp': 'Basic Puzzles', '7. Max 2 Boxes': 'Basic Puzzles', '8. Combine 2 Ramps': 'Basic Puzzles', '9. Scaling Round Objects': 'Basic Puzzles',
               'Square Cross-Sections': 'Intermediate Puzzles', 'Bird Fez': 'Intermediate Puzzles', 'Pi Henge': 'Intermediate Puzzles', '45-Degree Rotations': 'Intermediate Puzzles',  'Pyramids are Strange': 'Intermediate Puzzles', 'Boxes Obscure Spheres': 'Intermediate Puzzles', 'Object Limits': 'Intermediate Puzzles', 'Angled Silhouette': 'Intermediate Puzzles',
               'Sugar Cones': 'Advanced Puzzles', 'Stranger Shapes': 'Advanced Puzzles', 'Tall and Small': 'Advanced Puzzles', 'Ramp Up and Can It': 'Advanced Puzzles', 'More Than Meets Your Eye': 'Advanced Puzzles', 'Not Bird': 'Advanced Puzzles', 'Unnecessary': 'Advanced Puzzles', 'Zzz': 'Advanced Puzzles', 'Bull Market': 'Advanced Puzzles', 'Few Clues': 'Advanced Puzzles', 'Orange Dance': 'Advanced Puzzles', 'Bear Market': 'Advanced Puzzles', 'Warm Up': 'Intermediate Puzzles'}

thresHoldActivity = 60

class LevelsOfDifficulty(SessionFeature):
    def __init__(self, params:GeneratorParameters):
        super().__init__(params=params)
        self._numberActions = 0
        self._numberAttempts = 0
        
        self._activePuzzle = None
        self._activeTime = []
        self._previousEvent = None
        self._userPuzzleDict = dict()

    # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _eventFilter(cls, mode:ExtractionMode) -> List[str]:
        return ['move_shape', 'rotate_shape', 'scale_shape',
                'check_solution', 'undo_action', 'redo_action',
                'rotate_view', 'snapshot', 'mode_change',
                'create_shape', 'select_shape', 'delete_shape',
                'deselect_shape', 'select_shape_add', 'start_level',
                'puzzle_started', 'puzzle_complete', 'restart_puzzle',
                'click_nothing', 'toggle_paint_display', 'palette_change',
                'paint', 'toggle_snapshot_display']

    @classmethod
    def _featureFilter(cls, mode:ExtractionMode) -> List[str]:
        return []

    def _updateFromEvent(self, event:Event) -> None:
        ignoreEvent = False
        if event.EventName in ["start_level", "puzzle_started"]:
            self._activePuzzle = event.EventData["task_id"]

            if self._activePuzzle not in self._userPuzzleDict.keys():
                self._userPuzzleDict[self._activePuzzle] = {"completed":0, "n_actions":0, "n_attempts":0, "active_time":0}

        elif event.EventName == "puzzle_complete":
            if self._activePuzzle in self._userPuzzleDict.keys():
                self._userPuzzleDict[self._activePuzzle]["completed"] = 1
        
        if self._activePuzzle is None:
            ignoreEvent = True
        
        if ignoreEvent == False:
            if self._previousEvent is None:
                self._previousEvent = event
                ignoreEvent = True
            
            if ignoreEvent == False:
                #Add new active_time
                delta_seconds = (event.Timestamp - self._previousEvent.timestamp).total_seconds()
                if delta_seconds < thresHoldActivity:
                    self._activeTime.append(delta_seconds)
                
                if (event.EventName in listActionEvents):
                    self._numberActions += 1
                
                if (event.EventName == "check_solution"):
                    self._numberAttempts += 1
                    
                self._previousEvent = event
                    
                if (event.EventName in ['puzzle_complete', 'exit_to_menu', 'disconnect']):
                    self._userPuzzleDict[self._activePuzzle]['n_attempts'] += self._numberAttempts
                    self._userPuzzleDict[self._activePuzzle]['n_actions'] += self._numberActions
                    self._userPuzzleDict[self._activePuzzle]['active_time'] += round(np.sum(self._activeTime)/60, 2)
                    
                    self._previousEvent = None
                    self._activeTime = []
                    self._activePuzzle = None
                    self._numberAttempts = 0
                    self._numberActions = 0
            
    def _updateFromFeatureData(self, feature:FeatureData):
        return

    def _getFeatureValues(self) -> List[Any]:
        listReturn = []
        listAttempts = {}
        listActions = {}
        listActiveTime = {}
        listCompleted = {}
        listIncorrect = {}
        listAbandoned = {}
        for puzzle in self._userPuzzleDict.keys():
            listAttempts[puzzle] = self._userPuzzleDict[puzzle]['n_attempts']
            listActions[puzzle] = self._userPuzzleDict[puzzle]['n_actions']
            listActiveTime[puzzle] = self._userPuzzleDict[puzzle]['active_time']
            listCompleted[puzzle] = self._userPuzzleDict[puzzle]['completed']
            if self._userPuzzleDict[puzzle]['n_attempts'] > 0:
                listIncorrect[puzzle] = 100-100*(self._userPuzzleDict[puzzle]['completed']/self._userPuzzleDict[puzzle]['n_attempts'])
            else:
                listIncorrect[puzzle] = 100
            listAbandoned[puzzle] = 1 - self._userPuzzleDict[puzzle]['completed']
        listReturn.append("WorkInProgress")
        listReturn.append(json.dumps(listAttempts))
        listReturn.append(json.dumps(listActions))
        listReturn.append(json.dumps(listActiveTime))
        listReturn.append(json.dumps(listCompleted))
        listReturn.append(json.dumps(listIncorrect))
        listReturn.append(json.dumps(listAbandoned))
        
        return listReturn
        
    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["n_attempts", "n_actions", "active_time", "completed", "p_incorrect", "n_abandoned"]
