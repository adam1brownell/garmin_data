# garmin_data

This code is part of a workflow outlined [here](https://towardsdatascience.com/accessing-and-cleaning-data-from-garmin-wearables-for-analysis-56c22b83d932) regarding how to access and clean data from Garmin wearables.

The `clean_garmin.py` file in this repo pivots the garmin csv files by timestamp so that the columns are meaningful, as this is makes easily checking metrics by time of recoding simple. This also greatly reduces file size.

You can generate a clean garmin dataset by running the following from the command line:

```
python clean_garmin.py -i the_original_garmin_file.csv -o the_new_garmin_file.csv
```

Requires: Python 3.6+, Pandas 1.3+
