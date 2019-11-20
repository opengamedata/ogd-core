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


_interactive_entry_to_enum = {v: k for k, v in _enum_to_interactive_entry.items()}


def interactive_entry_to_enum(entry_fqid):
  return _interactive_entry_to_enum.get(entry_fqid)

_assessment_answers = {
  1: ['tunic.entry_tunic','HACKME','tunic.entry_basketballplaque','tunic.entry_cleanerslip'],
  2: ['tunic.entry_cleanerslip','tunic.entry_expert','tunic.entry_cleanercard','tunic.entry_logbook',
     'tunic.entry_newspaper','tunic.entry_theodora'],
  3: ['tunic.entry_teddytaken','tunic.entry_javajacket','tunic.entry_archivistcoffee','tunic.entry_taxidermy'],
  4: ['tunic.entry_tracks', 'tunic.entry_ecologyflag', 'tunic.entry_theta','tunic.entry_nelson','tunic.entry_activists']
}
