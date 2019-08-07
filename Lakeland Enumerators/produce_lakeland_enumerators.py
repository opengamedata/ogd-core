import re
import json
event_categories = {
        "gamestate": 0,
        "startgame": 1,
        "checkpoint": 2,
        "selecttile": 3,
        "selectfarmbit": 4,
        "selectitem": 5,
        "selectbuy": 6,
        "buy": 7,
        "cancelbuy": 8,
        "roadbuilds": 9,
        "tileuseselect": 10,
        "itemuseselect": 11,
        "togglenutrition": 12,
        "toggleshop": 13,
        "toggleachievements": 14,
        "skiptutorial": 15,
        "speed": 16,
        "achievement": 17,
        "farmbitdeath": 18,
        "blurb": 19,
        "click": 20,
        "rainstopped": 21,
        "history": 22,
        "endgame": 23
    }


def main(path_to_lakeland_readme, outpath=None):
    """
    This function takes in a path to the lakeland readme and outputs a json file of all the enumerators to the outpath.
    This assumes event categories have not changed (as of 8/7/19) and the readme is up-to-date and has maintained its
    current format..
    :param path_to_lakeland_readme: str
    :param outpath: str
    :return: dict corresponding to the produced json
    """
    json_enums = {}
    table_enums = {}
    json_enums['Event Categories'] = event_categories

    with open(path_to_lakeland_readme) as infile:
        enums = False
        table = ''
        write = False
        for line in infile:
            if line.strip() == "## Enumerators and Constants":
                enums = True
                continue
            elif line.strip() == "## Data Structures":
                enums = False
                continue
            elif enums:
                print(table, write, line)
                if line.strip()[:4] == "####":
                    table = line.strip()[4:].strip()
                    table_enums = {}
                    continue
                elif table and line.strip()[:2] == "<a":
                    json_enums[table] = table_enums
                    table = ''
                    write = False
                    continue
                elif table:
                    if line.strip() == "| --- | --- | --- |":
                        write = True
                    elif write:
                        if line.strip() and line.strip()[0] == "|":
                            matches = re.match(r'\|(.*)\|(.*)\|(.*)\|', line)
                            if len(matches.groups()) == 3:
                                idx = int(matches.groups()[0].strip())
                                val = matches.groups()[1].strip()
                                table_enums[val] = idx
    if outpath:
        with open(outpath,'w') as file:
            json.dump(json_enums, file, indent=2)
    return json_enums


