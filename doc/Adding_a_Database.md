# Adding a Database

- The sub-dictionaries are similar to the db_columns dictionary. They map each property name for a given event type to the type of that property.

- `db_columns`:
    A description of the structure of the database table.
    This element should be a dictionary mapping the names of each column in the database table to a string describing the column.

`db_columns` is used to ensure the raw csv file metadata contains descriptions of each database column.
`events` are used to get names for the members of each kind of event so we can extract features (and create columns in the raw csv).
`features` are used to ensure the processed csv file metadata contains descriptions of each feature, and to help document the features for whoever writes the actual feature extraction code.

```javascript
    "db_columns": {
        "id":"Unique identifier for a row",
    },
```