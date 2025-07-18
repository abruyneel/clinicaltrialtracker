import psycopg2
from config import load_config
import pandas as pd
import datetime as dt

def lastupdate(delta = 0):
    config  = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT runs_data FROM runs ORDER BY runs_id DESC LIMIT 1")
                rows = cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if len(rows) == 0:
            return dt.datetime.now()- dt.timedelta(days=delta)    
        else:
            return pd.to_datetime(rows[0][0]- dt.timedelta(days=delta))

def trial_exists(nct):
    config  = load_config()
    rows = [] 
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                for it in nct:
                    cur.execute("SELECT COUNT(trials_id) FROM trials WHERE trials_nct = %s", (it,))
                    rows.append(cur.fetchone()[0] == 0)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return rows

def insert_trials(trial_list):
    sql = "INSERT INTO trials(trials_nct, trials_name, trials_lastupdate) VALUES(%s, %s, %s) RETURNING *"
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.executemany(sql, trial_list)
            # commit the changes to the database
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    

def update_trials(trialsupdate):
    sql = """ UPDATE trials
                SET trials_lastupdate = %s
                WHERE trials_nct = %s"""
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                for row in trialsupdate:
                    # execute the UPDATE statement
                    cur.execute(sql, (row[0], row[1]))
            # commit the changes to the database
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def insert_run(run_date):
    sql = """INSERT INTO runs(runs_data)
             VALUES(%s) RETURNING runs_id;"""
    vendor_id = None
    config = load_config()
    try:
        with  psycopg2.connect(**config) as conn:
            with  conn.cursor() as cur:
                # execute the INSERT statement
                cur.execute(sql, (run_date,))
                # get the generated id back
                rows = cur.fetchone()
                if rows:
                    vendor_id = rows[0]
                # commit the changes to the database
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        return vendor_id
