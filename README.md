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

Running Data Exports:  

```
usage: <python> main.py <cmd> [<args>]

<python> is your python command.
<cmd>    is one of the available commands:
         - export
         - export_month
         - export_all_months
         - extract
         - help
[<args>] are the arguments for the command:
         - export: game_id, [start_date, end_date]
             game_id    = id of game to export
             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)
             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)
         - export_month: game_id, [month_year]
             game_id    = id of game to export
             month_year = month (and year) to export, in form mm/yyyy (default=current month)
         - export_all_months: game_id
             game_id    = id of game to export
         - extract: game_id, file_name
             game_id    = id of game to export
             file_name  = name of a .zip file containing dump data
```
(you can see a similar printout directly from the system by running ```python3 main.py --help```)

Example use:
```
python3 main.py export JOWILDER 1/1/2019 2/28/2019
```
In the example above, all JOWILDER data from beginning of January to end of February (in 2019) is exported to dump and processed files.

```
python3 main.py export_month JOWILDER 1/2019
```
In the example above, all JOWILDER data for the month of January 2019 is exported to dump and processed files.

```
python3 main.py JOWILDER export_all_months
```
In the example above, all available JOWILDER data is exported to dump and processed files, separated by month.

```
python3 main.py extract JOWILDER C:\path\to\opengamedata-backend\data\JOWILDER\JOWILDER_20190101_to_20190228_1234abc_dump.zip
```
In the example above, data from a previously exported dump file of JOWILDER data is extracted to a processed file.