# imports
from pytrials.client import ClinicalTrials
import pandas as pd
import psycopg2
from config import load_config
import datetime as dt
import functions

# initializations
ct = ClinicalTrials()

# read search terms from file
searchterms = pd.read_csv("searchterms.csv") 

# fetch latest
tables = {}
for term in searchterms["search"]:
    cts = ct.get_study_fields(
        search_expr=term,
        fields=["NCT Number", "Study Title", "Last Update Posted"],
        max_studies=100,
        fmt="csv",
        )
    tables[term] = pd.DataFrame.from_records(cts[1:], columns=cts[0])

df = pd.concat(tables)

# flag trials that were not yet in our database
df["newtrial"] = functions.trial_exists(df["NCT Number"])

# flag new updates to existing
df["newupdate"] = pd.to_datetime(df["Last Update Posted"]) >= functions.lastupdate(0)

# add new trials
functions.insert_trials(df.loc[df["newtrial"] == True, ["NCT Number", "Study Title", "Last Update Posted"]].to_numpy())

# update last update posted
functions.update_trials(df.loc[df["newupdate"] == True, ["Last Update Posted", "NCT Number"]].to_numpy())

# set todays date for latest updatee
functions.insert_run(dt.datetime.now())

#
print("New trials:  ")
print(df[df["newtrial"] == True])
print("Updated trials:  ")
print(df[df["newupdate"] == True])
