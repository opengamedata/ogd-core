# Rudolph, the red-nosed reindexer...
import json
import os
import utils

def meta_to_index(meta, data_dir):
    # just in case it didn't already end with a /
    if not data_dir.endswith("/"):
        data_dir = data_dir + "/"
    # raw_stat = os.stat(raw_csv_full_path)
    # proc_stat = os.stat(proc_csv_full_path)
    return \
        {
            "proc":f"{data_dir}{meta['proc'].split('/')[-1]}" if meta['proc'] is not None else None,
            "raw":f"{data_dir}{meta['raw'].split('/')[-1]}" if meta['raw'] is not None else None,
            "events":f"{data_dir}{meta['events'].split('/')[-1]}" if meta['events'] is not None else None,
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
    top = name.split('.')
    pieces = top[0].split('_')
    game_id = pieces[0]
    start_date = pieces[1]
    end_date = pieces[3]
    dataset_id  = f"{game_id}_{start_date}_to_{end_date}"
    kind = pieces[5]
    if not game_id in indexed_files.keys():
        indexed_files[game_id] = {}
    # if we already indexed something with this dataset id, then only update if this one is newer.
    # else, just stick this new meta in the index.
    if not dataset_id in indexed_files[game_id].keys():
        print(f"Indexing {os.path.join(root, name)}")
        indexed_files[game_id][dataset_id] = \
            {
                "proc":f"{root}{name}" if kind == 'session' else None,
                "raw":f"{root}{name}" if kind == 'raw' else None,
                "events":f"{root}{name}" if kind == 'events' else None,
                "start_date"   :start_date,
                "end_date"     :end_date,
                "date_modified":None,
                "sessions"     :None
            }
    else:
        if indexed_files[game_id][dataset_id]["proc"] == None and kind == 'session':
            print(f"Updating index with {os.path.join(root, name)}")
            indexed_files[game_id][dataset_id]["proc"] = f"{root}{name}"
        if indexed_files[game_id][dataset_id]["raw"] == None and kind == 'raw':
            print(f"Updating index with {os.path.join(root, name)}")
            indexed_files[game_id][dataset_id]["raw"] = f"{root}{name}"
        if indexed_files[game_id][dataset_id]["events"] == None and kind == 'events':
            print(f"Updating index with {os.path.join(root, name)}")
            indexed_files[game_id][dataset_id]["events"] = f"{root}{name}"
    return indexed_files

def generate_index(walk_data):
    indexed_files = {}
    zips = []
    for root, subdirs, files in walk_data:
        for name in files:
            ext = name.split('.')[-1]
            if (ext == 'meta'):
                print(f"Indexing {os.path.join(root, name)}")
                indexed_files = index_meta(root, name, indexed_files)
            elif (ext == 'zip'):
                print(f"Reserving {os.path.join(root, name)}")
                zips.append((root, name))
            else:
                print(f"Doing nothing with {os.path.join(root, name)}")
    for root,name in zips:
        indexed_files = index_zip(root, name, indexed_files)
    return indexed_files

data_dirs = os.walk("./data/")
indexed_files = generate_index(data_dirs)
# print(f"Final set of indexed files: {indexed_files}")
indexed_zips_file = open(f"./data/file_list.json", "w")
indexed_zips_file.write(json.dumps(indexed_files, indent=4, sort_keys=True))
indexed_zips_file.close()