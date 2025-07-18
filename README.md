# Update tracker of trials reported on ClinicalTrials.gov
This simple tracking script searches ClinicalTrials.gov for a set up keywords and stores the results. When the script is run again at a later time, it will generate a report comprised of the new trials and updates to existing trials.

Trial results are stored in a Postgres database, configuration is in database.ini file:
```
[postgresql]
host=xx
database=xx
user=xx
password=xx
```
