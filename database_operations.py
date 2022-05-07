import sqlite3
import os.path



def establish_db_connection(dbfile_path):
    """ establishes connection to a sqlite database listed under the dbfile_path and returns cursor, for queries to be executed on
        inputs:     dbfile_path (path where the sqlite_database is)
        outputs:    sqliteConnection (connection that can be closed later)
                    cursor (needed to execute queries in the db"""
# check if dbfile actually already exists, avoiding empty database creation
    if os.path.exists(dbfile_path):
        try:
            # connects to sqlite database file - if path is faulty, creates a new and empty database
            sqliteConnection = sqlite3.connect(dbfile_path)
            cursor = sqliteConnection.cursor()
            print('Connection to SQLite-File',dbfile_path,'>> SUCCESS!')
        except sqlite3.Error as error:
            print('SQLite error: ', error)
        finally:
            pass
    else:
        raise FileNotFoundError('Invalid path (dbfile): '+dbfile_path+' - *.db file doesn\'t exist.')
    return sqliteConnection, cursor

def query_db(sql_query, cursor, var = None):
    """ executes queries on the opened sqlite database, therefore requires the prior execution of establish_db_connection
        inputs: sql_query (query that should be executed)
                cursor (output of establish_db_connection, needed for executing queries)
                var (optional argument for queries that contain changing variables) """
    if cursor:    
        record = None
        if var == None:
            cursor.execute(sql_query)
        else:
            cursor.execute(sql_query, (var,))
        # save queried table locally in record
        record = cursor.fetchall()
        return record
    else:
        print("Database Connection not established, execute establish_db_connection prior to using this function")

def close_db_connection(sqliteConnection, cursor):
    if (sqliteConnection):
            cursor.close()
            sqliteConnection.close()
            print('The SQLite connection is closed')