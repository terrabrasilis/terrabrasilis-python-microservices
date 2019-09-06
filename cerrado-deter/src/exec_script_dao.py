#!/usr/bin/python3
import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ) )
from common_modules.configuration.src.common_config import ConfigLoader
from common_modules.postgresql.src.psqldb import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError


class ExecScriptDao:

    """
    The Dashboard Data Model Data Access Object runs intersections over all
    features in DETER Cerrado publish table for prepare data to analysis
    dashboard using the Dashboard Data Model.

    See configuration file, db.cfg for database connection definitions.

    """
    #constructor
    def __init__(self):
        relative_path = 'cerrado-deter/src/config/'
        self.db = PsqlDB(relative_path,'db.cfg','publish')
        self.data_dir = os.path.realpath(os.path.dirname(__file__) + "/../data/") + "/"
        self.__loadConfigurations(relative_path)


    def __loadConfigurations(self,relative_path):
        # read model parameters
        try:
            cfg = ConfigLoader(relative_path, 'model.cfg', 'publish')
            self.cfg = cfg.get()
        except Exception as configError:
            raise configError

    def execDropScript(self):
        """
        Exec the drop script to clear intermediary relations.

        If the SGBD Postgresql no implements the "IF EXISTS" then DROP statements
        will raise one exception, but this exception no abort the next statement.

        """
        drop_file = self.data_dir + self.cfg['drop_file']
        if not os.path.exists(drop_file):
            raise MissingParameterError('SQL script file','File, {0}, was not found.'.format(drop_file))
        
        scripts = None
        try:
            scripts = [line.rstrip('\r\n') for line in open(drop_file)]
        except Exception as error:
            raise MissingParameterError('SQL script file','Error: {0}'.format(error))
        
        try:
            self.db.connect()
            aQuery=""
            for statement in scripts:
                aQuery = "{0} {1}".format(aQuery, statement if statement.find('--') < 0 else '')
                if statement.find(';') >= 0:
                    try:
                        self.db.execQuery(aQuery)
                        self.db.commit()
                    except BaseException as error:
                        pass
                    finally:
                        aQuery=""
        except BaseException as error:
            self.db.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.db.close()

    def execScript(self):
        """
        Start process.

        Return the name for database to use as a title in output information message.
        
        Will raise a DatabaseError if exception occured.

        Warning: This method opens connection, run the process and close connection.
        """
        script_file = self.data_dir + self.cfg['script_file']
        if not os.path.exists(script_file):
            raise MissingParameterError('SQL script file','File, {0}, was not found.'.format(script_file))
        
        scripts = None
        try:
            scripts = [line.rstrip('\r\n') for line in open(script_file)]
        except Exception as error:
            raise MissingParameterError('SQL script file','Error: {0}'.format(error))
        
        try:
            self.db.connect()
            aQuery=""
            for statement in scripts:
                aQuery = "{0} {1}".format(aQuery, statement if statement.find('--') < 0 else '')
                if statement.find(';') >= 0:
                    self.db.execQuery(aQuery)
                    aQuery=""
            
            self.db.commit()
        except BaseException as error:
            self.db.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.db.close()

        return self.db.params["dbname"]


    def __basicExecute(self, sql):
        """
        Execute a basic SQL statement.
        """
        try:
            self.db.execQuery(sql)
        except Exception as error:
            self.db.rollback()
            raise DatabaseError('Database error:', error)


    def __fetchExecute(self, sql):
        """
        Execute a SQL statement and fetch the result data.
        """
        data = False
        try:
            data = self.db.fetchData(sql)
        except BaseException as error:
            raise DatabaseError('Database error:', error)
        
        return data