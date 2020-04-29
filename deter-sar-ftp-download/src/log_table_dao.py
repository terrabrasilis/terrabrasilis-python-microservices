#!/usr/bin/python3
import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ) )
from common_modules.postgresql.src.psqldb import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError

class LogTableDao:

    #constructor
    def __init__(self):
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config')
        self.db = PsqlDB(relative_path,'db.cfg','publish')

    def getLogID(self, filename):
        """
        Get ID from table for one filename.

        @return ID, a string that represents the ID related with one filename
        """
        sql = "SELECT id "
        sql += "FROM public.deter_sar_import_log "
        sql += "WHERE filename='{0}'".format(filename)

        return self.__fetch(sql)

    def __fetch(self, sql):
        data = None
        ret_data = {
            'id':None
        }
        try:
            self.db.connect()
            data = self.db.fetchData(sql)
        except BaseException:
            # by default return None
            return data
        finally:
            self.db.close()

        if(len(data)==1 and len(data[0])==1 and data[0][0]!=None):
            ret_data={
                'id':data[0][0]
            }
        
        return ret_data

