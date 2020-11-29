Python3 implementation of the Open Game Gata feature extractor  

This code pulls raw game data from a SQL database or export file, chooses appropiate features to extract based on the "game_id" and writes results to a csv file for data mining.

See http://fielddaylab.wisc.edu/opengamedata for exports of raw events and the features created by this code for a collection of education games.
See https://www.youtube.com/watch?v=gelyDJjxIeg for a walkthorugh of the high-level code structure.

Please feel free to modify this code, add new features or games and share back to the authors. We will deploy improvements to the Open Game Data site.

Setup:

* Install python3 (could write a whole chapter on this)
* Install mysql client: "brew install mysql" on osx
* Install dependancies: "pip3 install -r requirements.txt"
* Install more dependancies: "pip3 install -U scikit-learn scipy pandas gitpython"
* Modify the config.py.template for servers and authentication


```
usage: <python> main.py <cmd> [<args>]

<python> is your python command.
<cmd>    is one of the available commands:
         - export
         - export_month
         - help
[<args>] are the arguments for the command:
         - export: game_id, [start_date, end_date]
             game_id    = id of game to export
             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)
             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)
         - export_month: game_id, [month_year]
             game_id    = id of game to export
             month_year = month (and year) to export, in form mm/yyyy (default=current month)
```

Example use:
```
python3 main.py export 1/1/2019 2/28/2019
```
In the example above, all data from beginning of January to end of February (in 2019) is exported to file.

```
python3 main.py export_month 1/2019
```
In the example above, all data from the month of January 2019 is exported to file.
