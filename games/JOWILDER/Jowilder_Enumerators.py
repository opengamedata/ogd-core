import json
from typing import Dict, List, Optional

_enum_to_interactive_entry : Dict[int, str] = {
  0: 'tunic.entry_voteforgramps',
  1: 'tunic.entry_tunic',
  2: 'tunic.entry_cleanerslip',
  3: 'tunic.entry_basketballplaque',
  4: 'tunic.entry_teddytaken',
  5: 'tunic.entry_javajacket',
  6: 'tunic.entry_onthecase',
  7: 'tunic.entry_archivistcoffee',
  8: 'tunic.entry_expert',
  9: 'tunic.entry_logbook',
  10: 'tunic.entry_cleanercard',
  11: 'tunic.entry_microfiche',
  12: 'tunic.entry_newspaper',
  13: 'tunic.entry_taxidermy',
  14: 'tunic.entry_wellsid',
  15: 'tunic.entry_stacks_slip',
  16: 'tunic.entry_theodora',
  17: 'tunic.entry_scratches',
  18: 'tunic.entry_glasses',
  19: 'tunic.entry_teddyfree',
  20: 'tunic.entry_teddyfound',
  21: 'tunic.entry_key',
  22: 'tunic.entry_staffdir',
  23: 'tunic.entry_flag',
  24: 'tunic.entry_wellshoof',
  25: 'tunic.entry_tracks',
  26: 'tunic.entry_littering',
  27: 'tunic.entry_flaglady',
  28: 'tunic.entry_ecologyflag',
  29: 'tunic.entry_theta',
  30: 'tunic.entry_nelson',
  31: 'tunic.entry_activists'
}

def enum_to_interactive_entry(enum:int) -> str:
  return _enum_to_interactive_entry.get(enum, "INTERACTIVE ENTRY NOT FOUND!")

_interactive_entry_to_char = {v: chr(65+i+(i>25)*6) for i, v in _enum_to_interactive_entry.items()}
"""{'tunic.entry_voteforgramps': 'A',
 'tunic.entry_tunic': 'B',
 'tunic.entry_cleanerslip': 'C',
 'tunic.entry_basketballplaque': 'D',
 'tunic.entry_teddytaken': 'E',
 'tunic.entry_javajacket': 'F',
 'tunic.entry_onthecase': 'G',
 'tunic.entry_archivistcoffee': 'H',
 'tunic.entry_expert': 'I',
 'tunic.entry_logbook': 'J',
 'tunic.entry_cleanercard': 'K',
 'tunic.entry_microfiche': 'L',
 'tunic.entry_newspaper': 'M',
 'tunic.entry_taxidermy': 'N',
 'tunic.entry_wellsid': 'O',
 'tunic.entry_stacks_slip': 'P',
 'tunic.entry_theodora': 'Q',
 'tunic.entry_scratches': 'R',
 'tunic.entry_glasses': 'S',
 'tunic.entry_teddyfree': 'T',
 'tunic.entry_teddyfound': 'U',
 'tunic.entry_key': 'V',
 'tunic.entry_staffdir': 'W',
 'tunic.entry_flag': 'X',
 'tunic.entry_wellshoof': 'Y',
 'tunic.entry_tracks': 'Z',
 'tunic.entry_littering': 'a',
 'tunic.entry_flaglady': 'b',
 'tunic.entry_ecologyflag': 'c',
 'tunic.entry_theta': 'd',
 'tunic.entry_nelson': 'e',
 'tunic.entry_activists': 'f'}"""

def interactive_entry_to_char(entry_fqid) -> str:
  return _interactive_entry_to_char.get(entry_fqid) or ''

_assessment_answers : Dict[int, List[str]] = {
  1: ['tunic.entry_tunic','HACKME','tunic.entry_basketballplaque','tunic.entry_cleanerslip'],
  2: ['tunic.entry_cleanerslip','tunic.entry_expert','tunic.entry_cleanercard','tunic.entry_logbook',
     'tunic.entry_newspaper','tunic.entry_theodora'],
  3: ['tunic.entry_teddytaken','tunic.entry_javajacket','tunic.entry_archivistcoffee','tunic.entry_taxidermy'],
  4: ['tunic.entry_tracks', 'tunic.entry_ecologyflag', 'tunic.entry_theta','tunic.entry_nelson','tunic.entry_activists']
}

q_to_assessment : Dict[int, int] = {
 0: 1,
 1: 1,
 2: 1,
 3: 1,
 4: 2,
 5: 2,
 6: 2,
 7: 2,
 8: 2,
 9: 2,
 10: 3,
 11: 3,
 12: 3,
 13: 3,
 14: 4,
 15: 4,
 16: 4,
 17: 4,
 18: 4
}

assessement_to_lvl : Dict[int, int] = {
    1: 4,
    2: 12,
    3: 12,
    4: 22
}

assessment_to_last_q : Dict[int, int] = {
    1: 3,
    2: 9,
    3: 13,
    4: 18
}

_answer_fqid_to_q_num : Dict[str, int] = {
  'tunic.entry_tunic4': 0,
 'HACKME4': 1,
 'tunic.entry_basketballplaque4': 2,
 'tunic.entry_cleanerslip4': 3,
 'tunic.entry_cleanerslip12': 4,
 'tunic.entry_expert12': 5,
 'tunic.entry_cleanercard12': 6,
 'tunic.entry_logbook12': 7,
 'tunic.entry_newspaper12': 8,
 'tunic.entry_theodora12': 9,
 'tunic.entry_teddytaken12': 10,
 'tunic.entry_javajacket12': 11,
 'tunic.entry_archivistcoffee12': 12,
 'tunic.entry_taxidermy12': 13,
 'tunic.entry_tracks22': 14,
 'tunic.entry_ecologyflag22': 15,
 'tunic.entry_theta22': 16,
 'tunic.entry_nelson22': 17,
 'tunic.entry_activists22': 18
}

answer_to_question = lambda ans,lvl: _answer_fqid_to_q_num[f'{ans}{lvl}']

_answer_chars : List[Optional[str]] = ['B',
 None, # standin for D or C
 'D',
 'C',
 'C',
 'I',
 'K',
 'J',
 'M',
 'Q',
 'E',
 'F',
 'H',
 'N',
 'Z',
 'c',
 'd',
 'e',
 'f']

# objective is defined but what you have to click in order to start that objective.
# objective 0 is slightly different as you start the game with that objective
# do you always need an objective? idk.
fqid_to_enum : Dict[str, int] = {
  'tunic.historicalsociety.closet.gramps.intro_0_cs_0': 0,
  'tunic.historicalsociety.closet.teddy.intro_0_cs_0': 1,
  'tunic.historicalsociety.closet.notebook': 2,
  'tunic.historicalsociety.entry.groupconvo': 3,
  'tunic.historicalsociety.collection.cs': 4,
  'tunic.historicalsociety.collection.gramps.found': 5,
  'tunic.kohlcenter.halloffame.plaque.face.date': 6,
  'tunic.kohlcenter.halloffame.togrampa': 7,
  'tunic.capitol_0.hall.boss.chap1_finale_0': 8,
  'tunic.capitol_0.hall.boss.chap1_finale_1': 9,
  'tunic.capitol_0.hall.boss.chap1_finale_2': 10,
  'tunic.capitol_0.hall.chap1_finale_c': 11,
  'tunic.historicalsociety.closet_dirty.what_happened': 12,
  'tunic.historicalsociety.closet_dirty.trigger_scarf': 13,
  'tunic.historicalsociety.closet_dirty.trigger_coffee': 14,
  'tunic.historicalsociety.closet_dirty.gramps.news': 15,
  'tunic.historicalsociety.frontdesk.archivist.hello': 16,
  'tunic.historicalsociety.frontdesk.magnify': 17,
  'tunic.historicalsociety.frontdesk.archivist.have_glass': 18,
  'tunic.humanecology.frontdesk.worker.intro': 19,
  'tunic.humanecology.frontdesk.businesscards.card_bingo.bingo': 20,
  'tunic.drycleaner.frontdesk.worker.hub': 21,
  'tunic.drycleaner.frontdesk.logbook.page.bingo': 22,
  'tunic.drycleaner.frontdesk.worker.done': 23,
  'tunic.library.frontdesk.worker.hello': 24,
  'tunic.library.microfiche.reader.paper2.bingo': 25,
  'tunic.library.frontdesk.wellsbadge.hub': 26,
  'tunic.library.frontdesk.worker.wells': 27,
  'tunic.historicalsociety.frontdesk.archivist.newspaper': 28,
  'tunic.historicalsociety.stacks.journals.pic_2.bingo': 29,
  'tunic.capitol_1.hall.chap2_finale_c': 30,
  'tunic.capitol_1.hall.boss.chap2_finale_0': 31,
  'tunic.capitol_1.hall.boss.chap2_finale_1': 32,
  'tunic.capitol_1.hall.boss.chap2_finale_2': 33,
  'tunic.capitol_1.hall.boss.chap2_finale_3': 34,
  'tunic.capitol_1.hall.boss.chap2_finale_4': 35,
  'tunic.capitol_1.hall.boss.chap2_finale_5': 36,
  'tunic.capitol_1.hall.boss.chap2_finale_6': 37,
  'tunic.capitol_1.hall.gramps.chap2_teddy_finale_0': 38,
  'tunic.capitol_1.hall.boss.chap2_teddy_finale_1': 39,
  'tunic.capitol_1.hall.gramps.chap2_teddy_finale_2': 40,
  'tunic.capitol_1.hall.wells.chap2_teddy_finale_3': 41,
  'tunic.capitol_1.hall.gramps.chap2_teddy_finale_4': 42,
  'tunic.historicalsociety.basement.ch3start': 43,
  'tunic.historicalsociety.basement.seescratches': 44,
  'tunic.historicalsociety.cage.teddy.trapped': 45,
  'tunic.historicalsociety.cage.glasses.afterteddy': 46,
  'tunic.historicalsociety.frontdesk.key': 47,
  'tunic.historicalsociety.cage.unlockdoor': 48,
  'tunic.historicalsociety.cage.confrontation': 49,
  'tunic.historicalsociety.basement.savedteddy': 50,
  'tunic.historicalsociety.collection_flag.gramps.flag': 51,
  'tunic.historicalsociety.entry.groupconvo_flag': 52,
  'tunic.historicalsociety.entry.wells.flag': 53,
  'tunic.historicalsociety.entry.boss.flag': 54,
  'tunic.wildlife.center.crane_ranger.crane': 55,
  'tunic.wildlife.center.remove_cup': 56,
  'tunic.wildlife.center.expert.removed_cup': 57,
  'tunic.wildlife.center.tracks.hub.deer': 58,
  'tunic.wildlife.center.coffee': 59,
  'tunic.wildlife.center.wells.animals': 60,
  'tunic.wildlife.center.wells.nodeer': 61,
  'tunic.flaghouse.entry.flag_girl.hello': 62,
  'tunic.flaghouse.entry.colorbook': 63,
  'tunic.flaghouse.entry.flag_girl.symbol': 64,
  'tunic.library.frontdesk.worker.flag': 65,
  'tunic.library.microfiche.reader_flag.paper2.bingo': 66,
  'tunic.library.frontdesk.worker.nelson': 67,
  'tunic.historicalsociety.frontdesk.archivist_glasses.confrontation': 68,
  'tunic.capitol_2.hall.chap4_finale_c': 69,
  'tunic.capitol_2.hall.boss.chap4_finale_0': 70,
  'tunic.capitol_2.hall.boss.chap4_finale_1': 71,
  'tunic.capitol_2.hall.boss.chap4_finale_2': 72,
  'tunic.capitol_2.hall.boss.chap4_finale_3': 73,
  'tunic.capitol_2.hall.boss.chap4_finale_4': 74,
  'tunic.capitol_2.hall.boss.chap4_finale_5': 75,
  'tunic.nelson.trail.conclusion': 76,
  'tunic.nelson.trail.coffee': 77,
  'tunic.nelson.trail.display': 78,
  'tunic.capitol_3.hall.chap5_finale_c': 79,
  'tunic.historicalsociety.closet.teddy.intro_0_cs_5': 80,
  'tunic.historicalsociety.closet.doorblock': 81,
  'tunic.historicalsociety.closet.photo': 82,
  'tunic.historicalsociety.closet.retirement_letter.hub': 83,
  'tunic.historicalsociety.basement.gramps.seeyalater': 84,
  'tunic.historicalsociety.basement.gramps.whatdo': 85,
  'tunic.historicalsociety.basement.janitor': 86,
  'tunic.historicalsociety.entry.block_tocollection': 87,
  'tunic.historicalsociety.entry.block_tomap1': 88,
  'tunic.historicalsociety.entry.block_tomap2': 89,
  'tunic.historicalsociety.entry.boss.flag_recap': 90,
  'tunic.historicalsociety.entry.boss.talktogramps': 91,
  'tunic.historicalsociety.entry.directory.closeup.archivist': 92,
  'tunic.historicalsociety.entry.gramps.hub': 93,
  'tunic.historicalsociety.entry.wells.flag_recap': 94,
  'tunic.historicalsociety.entry.wells.talktogramps': 95,
  'tunic.historicalsociety.collection': 96,
  'tunic.historicalsociety.collection.gramps.look_0': 97,
  'tunic.historicalsociety.collection.gramps.lost': 98,
  'tunic.historicalsociety.collection.slip': 99,
  'tunic.kohlcenter.halloffame.block_0': 100,
  'tunic.kohlcenter.halloffame.block_1': 101,
  'tunic.kohlcenter.halloffame.plaque.face': 102,
  'tunic.capitol_0.hall.boss.chap1_finale_0_fail': 103,
  'tunic.capitol_0.hall.boss.chap1_finale_1_fail': 104,
  'tunic.capitol_0.hall.boss.chap1_finale_plaquefirst_0': 105,
  'tunic.capitol_0.hall.boss.chap1_finale_plaquefirst_0_fail': 106,
  'tunic.capitol_0.hall.boss.chap1_finale_plaquefirst_1': 107,
  'tunic.capitol_0.hall.boss.chap1_finale_slipfirst_0': 108,
  'tunic.capitol_0.hall.boss.chap1_finale_slipfirst_0_fail': 109,
  'tunic.capitol_0.hall.boss.chap1_finale_slipfirst_1': 110,
  'tunic.capitol_0.hall.boss.talktogramps': 111,
  'tunic.capitol_0.hall.gramps.hub': 112,
  'tunic.historicalsociety.closet_dirty.door_block_clean': 113,
  'tunic.historicalsociety.closet_dirty.door_block_talk': 114,
  'tunic.historicalsociety.closet_dirty.gramps.archivist': 115,
  'tunic.historicalsociety.closet_dirty.gramps.helpclean': 116,
  'tunic.historicalsociety.closet_dirty.gramps.nothing': 117,
  'tunic.historicalsociety.closet_dirty.photo': 118,
  'tunic.historicalsociety.stacks.block': 119,
  'tunic.historicalsociety.stacks.journals': 120,
  'tunic.historicalsociety.stacks.journals_flag': 121,
  'tunic.historicalsociety.stacks.journals_flag.pic_0.bingo': 122,
  'tunic.historicalsociety.stacks.journals_flag.pic_1.bingo': 123,
  'tunic.historicalsociety.stacks.journals_flag.pic_2.bingo': 124,
  'tunic.historicalsociety.stacks.outtolunch': 125,
  'tunic.historicalsociety.frontdesk.archivist.foundtheodora': 126,
  'tunic.historicalsociety.frontdesk.archivist.have_glass_recap': 127,
  'tunic.historicalsociety.frontdesk.archivist.need_glass_0': 128,
  'tunic.historicalsociety.frontdesk.archivist.need_glass_1': 129,
  'tunic.historicalsociety.frontdesk.archivist.newspaper_recap': 130,
  'tunic.historicalsociety.frontdesk.archivist_glasses.confrontation_recap': 131,
  'tunic.historicalsociety.frontdesk.block_magnify': 132,
  'tunic.humanecology.frontdesk.block_0': 133,
  'tunic.humanecology.frontdesk.block_1': 134,
  'tunic.humanecology.frontdesk.businesscards': 135,
  'tunic.humanecology.frontdesk.worker.badger': 136,
  'tunic.drycleaner.frontdesk.block_0': 137,
  'tunic.drycleaner.frontdesk.block_1': 138,
  'tunic.drycleaner.frontdesk.logbook': 139,
  'tunic.drycleaner.frontdesk.worker.done2': 140,
  'tunic.drycleaner.frontdesk.worker.takealook': 141,
  'tunic.library.frontdesk.block_badge': 142,
  'tunic.library.frontdesk.block_badge_2': 143,
  'tunic.library.frontdesk.block_nelson': 144,
  'tunic.library.frontdesk.worker.droppedbadge': 145,
  'tunic.library.frontdesk.worker.flag_recap': 146,
  'tunic.library.frontdesk.worker.hello_short': 147,
  'tunic.library.frontdesk.worker.nelson_recap': 148,
  'tunic.library.frontdesk.worker.preflag': 149,
  'tunic.library.frontdesk.worker.wells_recap': 150,
  'tunic.library.microfiche.block_0': 151,
  'tunic.library.microfiche.reader': 152,
  'tunic.capitol_1.hall.boss.chap2_finale_0_fail': 153,
  'tunic.capitol_1.hall.boss.chap2_finale_1_fail': 154,
  'tunic.capitol_1.hall.boss.chap2_finale_2_fail': 155,
  'tunic.capitol_1.hall.boss.chap2_finale_3_fail': 156,
  'tunic.capitol_1.hall.boss.chap2_finale_4_fail': 157,
  'tunic.capitol_1.hall.boss.chap2_finale_5_fail': 158,
  'tunic.capitol_1.hall.boss.chap2_finale_6_fail': 159,
  'tunic.capitol_1.hall.boss.chap2_teddy_finale_1_fail': 160,
  'tunic.capitol_1.hall.boss.haveyougotit': 161,
  'tunic.capitol_1.hall.boss.writeitup': 162,
  'tunic.capitol_1.hall.gramps.chap2_teddy_finale_0_fail': 163,
  'tunic.capitol_1.hall.gramps.chap2_teddy_finale_2_fail': 164,
  'tunic.capitol_1.hall.gramps.chap2_teddy_finale_4_fail': 165,
  'tunic.capitol_1.hall.wells.chap2_teddy_finale_3_fail': 166,
  'tunic.capitol_1.hall.wells.hub': 167,
  'tunic.historicalsociety.cage.glasses.beforeteddy': 168,
  'tunic.historicalsociety.cage.lockeddoor': 169,
  'tunic.historicalsociety.cage.need_glasses': 170,
  'tunic.historicalsociety.collection_flag.gramps.recap': 171,
  'tunic.wildlife.center.expert.recap': 172,
  'tunic.wildlife.center.fox.concern': 173,
  'tunic.wildlife.center.wells.animals2': 174,
  'tunic.wildlife.center.wells.nodeer_recap': 175,
  'tunic.flaghouse.entry.flag_girl.hello_recap': 176,
  'tunic.flaghouse.entry.flag_girl.symbol_recap': 177,
  'tunic.capitol_2.hall.boss.chap4_finale_0_fail': 178,
  'tunic.capitol_2.hall.boss.chap4_finale_1_fail': 179,
  'tunic.capitol_2.hall.boss.chap4_finale_2_fail': 180,
  'tunic.capitol_2.hall.boss.chap4_finale_3_fail': 181,
  'tunic.capitol_2.hall.boss.chap4_finale_4_fail': 182,
  'tunic.capitol_2.hall.boss.chap4_finale_5_fail': 183,
  'tunic.capitol_2.hall.boss.haveyougotit': 184,
  'tunic.nelson.trail.gramps.question': 185,
  'tunic.capitol_3.hall.crowd.hub': 186,
  'tunic.capitol_3.hall.gramps.hub': 187,
  'tunic.capitol_3.hall.teddy.speak': 188}

max_objective : int = 79

save_code_to_obj : Dict[str, int] = {
  'startgame': 0,
  'notebook': 3,
  'wiscwonders': 4,
  'mysteryslip': 6,
  'plaque': 8,
  'notajersey': 12,
  'trashed': 13,
  'archivist': 19,
  'textile': 21,
  'logbook': 23,
  'suffragist': 26,
  'taxidermist': 28,
  'wellsdidit': 30,
  'saveteddy': 43,
  'scratches': 45,
  'hesalive': 46,
  'akey': 48,
  'rescued': 50,
  'backtowork': 52,
  'sadanimals': 62,
  'flaglady': 65,
  'ecologists': 67,
  'donethework': 69,
  'sunset': 77
}

# level to first objective in level.
level_to_start_obj : Dict[int, int] = {
  0: 0, 1: 3, 2: 4, 3: 6, 4: 8, 5: 12, 6: 13, 7: 19, 8: 21, 9: 23, 10: 26, 11: 28, 12: 30, 13: 43,
  14: 45, 15: 46, 16: 48, 17: 50, 18: 52, 19: 62, 20: 65, 21: 67, 22: 69, 23: 77
}

def quiz_question_to_index(quiz_num:int, question_num:int) -> int:
  """See: https://github.com/fielddaylab/jo_wilder/blob/master/src/scenes/quiz.js

  Each quiz is defined as a seperate dictionary, which means the index of each
  question is specific to its position in that dictionary, rather than its position
  in the overall question list.

  The quiz_indexes dictionary contains the proper indexing for all questions in each 
  of the 5 quizzes.

  Returns:
    The remapped index given a quiz and question number.
  """
  quiz_indexes : Dict[int, Dict[int, int]] = {
    0: {0: 0, 1: 1},
    2: {0: 2, 1: 3, 2: 4, 3: 5},
    3: {0: 6, 1: 7, 2: 8, 3: 9},
    4: {0: 10, 1: 11, 2: 12, 3: 13},
    5: {0: 14, 1: 15, 2: 16, 3: 17}
  }

  return quiz_indexes[quiz_num][question_num]


def quizn_to_index(quizn:int) -> int:
  """See: https://github.com/fielddaylab/jo_wilder/blob/master/src/scenes/quiz.js

  For some reason there are 5 quizzes, but there is no quiz numbered 1.
  
  Returns:
    The correct quiz number for quizzes 2-5, or 0 for quiz 0.
  """
  return quizn - 1 if quizn >= 2 else quizn

if __name__ == '__main__':
 print({i:v for i,(k,v) in enumerate(save_code_to_obj.items())})