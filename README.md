# Python3 implementation of the Open Game Gata feature extractor  

This code pulls raw game data from a SQL database, BigQuery database, or export file; chooses appropiate features to extract based on the "game_id"; and writes results to a file for data mining.

See [http://fielddaylab.wisc.edu/opengamedata](http://fielddaylab.wisc.edu/opengamedata) for exports of raw events and the features created by this code for a collection of education games.
See [https://www.youtube.com/watch?v=gelyDJjxIeg](https://www.youtube.com/watch?v=gelyDJjxIeg) for a walkthorugh of the high-level code structure.

Please feel free to modify this code, add new features or games and share back to the authors. We will deploy improvements to the Open Game Data site.

Setup:

* Install python3 (could write a whole chapter on this)
* Install python dependencies: "pip3 install -r requirements.txt"
* Copy `config.py.template` to `config.py` and set server/authentication data
* Download any authentication keys needed for BigQuery game data projects

Running Data Exports:  

```none
usage: <python> main.py <cmd> [<args>]

<python> is your python command.
<cmd>    is one of the available commands:
         - export
         - export-events
         - export-features
         - info
         - readme
         - help
[<args>] are the arguments for the command:
         - export: game_id, [start_date, end_date]
             game_id    = id of game to export
             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)
             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)
         - export-events: game_id, [start_date, end_date]
             game_id    = id of game to export
             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)
             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)
         - export-features: game_id, [start_date, end_date]
             game_id    = id of game to export
             start_date = beginning date for export, in form mm/dd/yyyy (default=first day of current month)
             end_date   = ending date for export, in form mm/dd/yyyy (default=current day)
         - info: game_id
             game_id    = id of game whose info should be shown
         - readme: game_id
             game_id    = id of game whose readme should be generated
         - help: *None*
[<opt-args>] are option arguments, which affect certain commands:
         --file: specifies a file to export events or features
         --monthly: with this flag, specify dates by mm/yyyy instead of mm/dd/yyyy
```

(you can see a similar printout directly from the system by running ```python3 main.py --help```)

Example use:

```none
python3 main.py export JOWILDER 1/1/2019 2/28/2019
```

In the example above, all JOWILDER data from beginning of January to end of February (in 2019) is exported. This includes both the events and the processed session features.

```none
python3 main.py export JOWILDER --monthly 1/2019
```

In the example above, all JOWILDER data from the month of January 2019 is exported. This includes both the events and the processed session features.

```none
python3 main.py export-events JOWILDER 1/1/2019 2/28/2019
```

In the example above, only the events from the JOWILDER data during given date range are exported.

```none
python3 main.py export-features JOWILDER 1/1/2019 2/28/2019
```

In the example above, only the processed session/player/population features from the JOWILDER data during given date range are exported.

<!-- ```
python3 main.py export JOWILDER --file=C:\path\to\opengamedata-backend\data\JOWILDER\JOWILDER_20190101_to_20190228_1234abc_events.zip
```
In the example above, events and processed session features are exported from the data at the specified file path. -->
