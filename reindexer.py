# Rudolph, the red-nosed reindexer...
import json
import logging
import os
import utils

def meta_to_index(meta, data_dir):
    # just in case it didn't already end with a /
    if not data_dir.endswith("/"):
        data_dir = data_dir + "/"
    # raw_stat = os.stat(raw_csv_full_path)
    # sessions_stat = os.stat(sessions_csv_full_path)
    return \
        {
            "sessions_f":f"{data_dir}{meta['sessions_f'].split('/')[-1]}" if ('sessions_f' in meta.keys() and meta['sessions_f'] is not None) else None,
            "raw_f":f"{data_dir}{meta['raw_f'].split('/')[-1]}" if ('raw_f' in meta.keys() and meta['raw_f'] is not None) else None,
            "events_f":f"{data_dir}{meta['events_f'].split('/')[-1]}" if ('events_f' in meta.keys() and meta['events_f'] is not None) else None,
            "start_date"   :meta['start_date'],
            "end_date"     :meta['end_date'],
            "date_modified":meta['date_modified'],
            "sessions"     :meta['sessions']
        }

def index_meta(root, name, indexed_files):
    next_file = open(os.path.join(root, name), 'r')
    next_meta = json.load(next_file)
    next_game = next_meta['game_id']
    next_data_id = next_meta['dataset_id']
    if not next_game in indexed_files.keys():
        indexed_files[next_game] = {}
    # if we already indexed something with this dataset id, then only update if this one is newer.
    # else, just stick this new meta in the index.
    if next_data_id in indexed_files[next_game].keys():
        if next_meta['date_modified'] > indexed_files[next_game][next_data_id]['date_modified']:
            indexed_files[next_game][next_data_id] = meta_to_index(next_meta, root)
    else:
        indexed_files[next_game][next_data_id] = meta_to_index(next_meta, root)
    return indexed_files

def index_zip(root, name, indexed_files):
    # for reference, here's how the indices of a tsv file should look, if we're not dealing with a "cycle" game.
    PIECE_INDICES = {'name':0, 'start_date':1, 'to':2, 'end_date':3, 'id':4, 'file_type':5}
    top = name.split('.')
    pieces = top[0].split('_')
    game_id = pieces[0] if pieces[0] != 'CYCLE' else f"{pieces[0]}_{pieces[1]}"
    start_date = pieces[-5]
    end_date = pieces[-3]
    dataset_id  = f"{game_id}_{start_date}_to_{end_date}"
    kind = pieces[-1]
    if not game_id in indexed_files.keys():
        indexed_files[game_id] = {}
    # if we already indexed something with this dataset id, then only update if this one is newer.
    # else, just stick this new meta in the index.
    if not dataset_id in indexed_files[game_id].keys():
        utils.Logger.toPrint(f"Indexing {os.path.join(root, name)}", logging.INFO)
        indexed_files[game_id][dataset_id] = \
            {
                "sessions_f":f"{root}{name}" if kind == 'session-features' else None,
                "raw_f":f"{root}{name}" if kind == 'raw' else None,
                "events_f":f"{root}{name}" if kind == 'events' else None,
                "start_date"   :start_date,
                "end_date"     :end_date,
                "date_modified":None,
                "sessions"     :None
            }
    else:
        if indexed_files[game_id][dataset_id]["sessions_f"] == None and kind == 'session-features':
            utils.Logger.toPrint(f"Updating index with {os.path.join(root, name)}", logging.INFO)
            indexed_files[game_id][dataset_id]["sessions_f"] = f"{root}{name}"
        if indexed_files[game_id][dataset_id]["raw_f"] == None and kind == 'raw':
            utils.Logger.toPrint(f"Updating index with {os.path.join(root, name)}", logging.INFO)
            indexed_files[game_id][dataset_id]["raw_f"] = f"{root}{name}"
        if indexed_files[game_id][dataset_id]["events_f"] == None and kind == 'events':
            utils.Logger.toPrint(f"Updating index with {os.path.join(root, name)}", logging.INFO)
            indexed_files[game_id][dataset_id]["events_f"] = f"{root}{name}"
    return indexed_files

def generate_index(walk_data):
    indexed_files = {}
    zips = []
    for root, subdirs, files in walk_data:
        for name in files:
            if not 'BACKUP' in root:
                ext = name.split('.')[-1]
                if (ext == 'meta'):
                    utils.Logger.toPrint(f"Indexing {os.path.join(root, name)}", logging.INFO)
                    indexed_files = index_meta(root, name, indexed_files)
                elif (ext == 'zip'):
                    utils.Logger.toPrint(f"Reserving {os.path.join(root, name)}", logging.DEBUG)
                    zips.append((root, name))
                else:
                    utils.Logger.toPrint(f"Doing nothing with {os.path.join(root, name)}", logging.DEBUG)
            else:
                utils.Logger.toPrint(f"Doing nothing with {os.path.join(root, name)}", logging.DEBUG)
    for root,name in zips:
        indexed_files = index_zip(root, name, indexed_files)
    return indexed_files

data_dirs = os.walk("./data/")
indexed_files = generate_index(data_dirs)
# print(f"Final set of indexed files: {indexed_files}")
indexed_zips_file = open(f"./data/file_list.json", "w")
indexed_zips_file.write(json.dumps(indexed_files, indent=4, sort_keys=True))
indexed_zips_file.close()
