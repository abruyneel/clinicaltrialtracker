# imports
from pytrials.client import ClinicalTrials
import pandas as pd
import datetime as dt
import functions
import dominate
from dominate.tags import h1, h2
from dominate.util import raw
import io

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
df.drop_duplicates(subset=["NCT Number"])

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

# report
doc = dominate.document(title='Clinicaltrialtracker update report')

with doc:
    dominate.tags.h1("Clinicaltrialtracker update report")
    dominate.tags.h2("New trials:")
    raw(df[df["newtrial"] == True].to_html(index=False, columns=["NCT Number", "Study Title", "Last Update Posted"]))
    dominate.tags.h2("Updated trials:")
    raw(df[df["newupdate"] == True].to_html(index=False, columns=["NCT Number", "Study Title", "Last Update Posted"]))

with open("output/"+dt.datetime.now().strftime("%Y-%m-%d")+"_report.html", 'w') as f:
    f.write(doc.render())
