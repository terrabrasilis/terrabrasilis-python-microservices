#!/usr/bin/python3
import sys, os
import psycopg2
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)+'/../../configuration/src'))
from common_config import ConfigLoader

class ConnectionError(BaseException):
    """Exception raised for errors in the DB connection.
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class QueryError(BaseException):
    """Exception raised for errors in the DB Queries.
    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class PsqlDB:
    """
        For connection to database use this parameters:
        relative_path = 'the/path/to/config/file/'
        filename = 'db.cfg'
        section = 'session_name_to_db_config'

    """
    def __init__(self, relative_path, filename, section):
        self.conn = None
        self.cur = None
        # read connection parameters
        try:
            conf = ConfigLoader(relative_path, filename, section)
            self.params = conf.get()
            # get user and password for postgres from secrets
            self.db_user = os.getenv("POSTGRES_USER_FILE", "postgres")
            if os.path.exists(self.db_user):
                self.db_user = open(self.db_user, 'r').read()
            self.db_pass = os.getenv("POSTGRES_PASS_FILE", "postgres")
            if os.path.exists(self.db_pass):
                self.db_pass = open(self.db_pass, 'r').read()
        except Exception as configError:
            raise configError

    def connect(self):
        try:
            # connect to the PostgreSQL server
            str_conn="dbname={0} user={1} password={2} host={3} port={4}".format(self.params["dbname"],self.db_user,self.db_pass,self.params["host"],self.params["port"])
            self.conn = psycopg2.connect(str_conn)
            self.cur = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            raise ConnectionError('Missing connection:', str(error))
    
    def close(self):
        # close the communication with the PostgreSQL
        if self.cur is not None:
            self.cur.close()
            self.cur = None
        # disconnect from the PostgreSQL server
        if self.conn is not None:
            self.conn.close()

    def commit(self):
        # disconnect from the PostgreSQL server
        if self.conn is not None:
            # commit the changes
            self.conn.commit()
    
    def rollback(self):
        # disconnect from the PostgreSQL server
        if self.conn is not None:
            # commit the changes
            self.conn.rollback()

    def execQuery(self, query, isInsert=None):
        try:
            
            if self.cur is None:
                raise ConnectionError('Missing cursor:', 'Has no valid database cursor ({0})'.format(query))
            # execute a statement
            self.cur.execute(query)

            if isInsert:
                data=self.cur.fetchone()
                if(data):
                    return data[0]
                else:
                    return None

        except (Exception, psycopg2.DatabaseError) as error:
            self.rollback()
            raise QueryError('Query execute issue', error)
        except (BaseException) as error:
            self.rollback()
            raise QueryError('Query execute issue', error)
            

    def fetchData(self, query):
        data = None
        try:
            # execute a statement
            self.execQuery(query)
            # retrive data
            data = self.cur.fetchall()
            
        except QueryError as error:
            raise error

        return data