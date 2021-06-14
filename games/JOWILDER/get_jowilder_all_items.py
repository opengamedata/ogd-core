import os, re, json

def getListOfFiles(dirName):
    # create a list of file and sub directories
    # names in the given directory
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory
        if not os.path.isdir(fullPath):
            allFiles.append(fullPath)
        else:
            allFiles += getListOfFiles(fullPath)
    return allFiles

def get_all_items(jowilder_path, outpath):
    # get all files from the scenes folder
    owd = os.getcwd()
    levels_path = os.path.join(jowilder_path, 'assets/data/levels')
    os.chdir(levels_path)
    allfiles = getListOfFiles('tunic/scenes')
    os.chdir(owd)

    # seperate all that to json
    all_items = []
    pattern = re.compile(r"""tmp_.*_command\.raw_[a]*text = "(.*)";\ntmp_.*_command\.speaker = (.*);""")
    for path in allfiles:
        true_path = os.path.join(levels_path, path)
        # get text of any applicable character
        with open(true_path) as f:
            text_speaker = pattern.findall(f.read())

        # make path dictionary
        path_list = path.replace('.meta', '').split('/')
        if len(path_list) > 6:
            all_items.append({
                'path':  true_path,
                'scene': path_list[2],
                'room': path_list[4],
                'type': path_list[5],
                'fqid': '.'.join(path_list[6:]),
                'text_speaker': text_speaker
            })

    with open(outpath, 'w+') as outfile:
        json.dump(all_items, outfile, indent=4)

if __name__ == '__main__':
    jowilder_path = '/Users/johnmccloskey/Development/jo_wilder'
    outpath = 'game_info/Jowilder/jowilder_all_items.json'
    get_all_items(jowilder_path=jowilder_path, outpath=outpath)
