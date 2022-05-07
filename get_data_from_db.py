import sqlite3
from timeit import default_timer as timer
import os.path

def query_db(dbfile, sql_query):
    """queries database, returning a list of tuples, where each list entry is a table row and each tuple containing
    the columns """
    # check if dbfile actually already exists, avoiding empty database creation
    record = None
    if os.path.exists(dbfile):
        try:
            # connects to sqlite database file - if path is faulty, creates a new and empty database
            sqliteConnection = sqlite3.connect(dbfile)
            cursor = sqliteConnection.cursor()
            print('Connection to SQLite-File',dbfile,'>> SUCCESS!')
            # set timer start to measure query duration
            q_start = timer()
            # set cursor on table according to the provided query
            cursor.execute(sql_query)
            # save queried table locally in record
            record = cursor.fetchall()
            # more timer stuff (ending time point, calculating duration and printing)
            q_end = timer()
            q_duration = q_end - q_start
            print('\n Elapsed time for SQLite query: ', q_duration,'\n')
        except sqlite3.Error as error:
            print('SQLite error: ', error)
        finally:
            # in case of a fault, the sqlite connection will still be shut down
            if (sqliteConnection):
                cursor.close()
                sqliteConnection.close()
                print('The SQLite connection is closed')
    else:
        raise FileNotFoundError('Invalid path (dbfile): '+dbfile+' - *.db file doesn\'t exist.')
    return record

def query_db_var(dbfile, sql_query, var):
    """queries database, returning a list of tuples, where each list entry is a table row and each tuple containing
    the columns """
    # check if dbfile actually already exists, avoiding empty database creation
    record = None
    if os.path.exists(dbfile):
        try:
            # connects to sqlite database file - if path is faulty, creates a new and empty database
            sqliteConnection = sqlite3.connect(dbfile)
            cursor = sqliteConnection.cursor()
            print('Connection to SQLite-File',dbfile,'>> SUCCESS!')
            # set timer start to measure query duration
            q_start = timer()
            # set cursor on table according to the provided query
            cursor.execute(sql_query, (var,))
            # save queried table locally in record
            record = cursor.fetchall()
            # more timer stuff (ending time point, calculating duration and printing)
            q_end = timer()
            q_duration = q_end - q_start
            print('\n Elapsed time for SQLite query: ', q_duration,'\n')
        except sqlite3.Error as error:
            print('SQLite error: ', error)
        finally:
            # in case of a fault, the sqlite connection will still be shut down
            if (sqliteConnection):
                cursor.close()
                sqliteConnection.close()
                print('The SQLite connection is closed')
    else:
        raise FileNotFoundError('Invalid path (dbfile): '+dbfile+' - *.db file doesn\'t exist.')
    return record

#my_query = '''  SELECT e.event_id, e.time, t.type, d.person, d.link, d.legMode
#                FROM (events e INNER JOIN types t ON e.type_id == t.type_id) 
#                INNER JOIN dep_arr_events d ON e.event_id == d.event_id 
#                WHERE t.type == "departure" AND d.legMode == "car"'''

#for row in data:
#    for tpl in row:
#        pass

# test_query=''' SELECT vehicle, link FROM vehicle_link_events '''
# dbfile="/Users/dstobbe/Desktop/Uni/Bachelorarbeit/MATSIM Output/DBFiles/b-drt-mpm-1pct.db"

# test=query_db(dbfile, test_query)