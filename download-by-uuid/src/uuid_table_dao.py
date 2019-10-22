#!/usr/bin/python3
import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ) )
from common_modules.configuration.src.common_config import ConfigLoader
from common_modules.postgresql.src.psqldb import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError


class UuidTableDao:

    #constructor
    def __init__(self):
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config')
        self.db = PsqlDB(relative_path,'db.cfg','publish')

    def confirmUUID(self, uuid):
        """
        Verify if UUID is in the table.

        @return exists, true if UUID exists on table or false otherwise
        """
        sql = "SELECT num_downloads "
        sql += "FROM public.downloads_by_uuid "
        sql += "WHERE uuid='{0}'".format(uuid)

        ret=self.__fetch(sql)
        if (ret!=None and ret['num_downloads']>=0):
            return True
        else:
            return False

    def increaseDownloadByUUID(self, uuid):
        """
        Increments the number of downloads using this UUID.

        @return void
        """
        sql = "UPDATE public.downloads_by_uuid "
        sql += "SET num_downloads="
        sql += "(SELECT num_downloads + 1 FROM public.downloads_by_uuid WHERE uuid='{0}') ".format(uuid)

        self.__execSQL(sql)

    def storeClientIP(self, uuid, ip):
        """
        Store the client IP.

        @return void
        """
        sql = "INSERT INTO public.request_by_ip(id_download, ip) VALUES "
        sql += "((select id from public.downloads_by_uuid where uuid='{0}'), '{1}')".format(uuid,ip)

        self.__execSQL(sql)

    def __fetch(self, sql):
        data = None
        ret_data = {
            'num_downloads':-1,
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
                'num_downloads':data[0][0]
            }
        
        return ret_data

    def __execSQL(self, sql):
        try:
            self.db.connect()
            self.db.execQuery(sql)
            self.db.commit()
        except BaseException:
            self.rollback()
            raise DatabaseError('Query execute issue', sql)
        finally:
            self.db.close()
