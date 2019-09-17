Python re-implementation of some of the features of the original logger code.  
In particular, this includes code to extract features from a database, and write the results to a csv.

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