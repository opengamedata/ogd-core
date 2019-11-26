_enum_to_interactive_entry = {
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


def enum_to_interactive_entry(enum):
  return _enum_to_interactive_entry.get(enum)


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

def interactive_entry_to_char(entry_fqid):
  return _interactive_entry_to_char.get(entry_fqid) or ''


_assessment_answers = {
  1: ['tunic.entry_tunic','HACKME','tunic.entry_basketballplaque','tunic.entry_cleanerslip'],
  2: ['tunic.entry_cleanerslip','tunic.entry_expert','tunic.entry_cleanercard','tunic.entry_logbook',
     'tunic.entry_newspaper','tunic.entry_theodora'],
  3: ['tunic.entry_teddytaken','tunic.entry_javajacket','tunic.entry_archivistcoffee','tunic.entry_taxidermy'],
  4: ['tunic.entry_tracks', 'tunic.entry_ecologyflag', 'tunic.entry_theta','tunic.entry_nelson','tunic.entry_activists']
}
