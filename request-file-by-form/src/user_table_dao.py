#!/usr/bin/python3
import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ) )
from common_modules.configuration.src.common_config import ConfigLoader
from common_modules.postgresql.src.psqldb import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError

class UserTableDao:

    #constructor
    def __init__(self):
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config')
        self.db = PsqlDB(relative_path,'db.cfg','publish')

    def getUUID(self, email):
        """
        Get UUID from table for one user.

        @return UUID, a string that represents the UUID related with one user
        """
        sql = "SELECT uuid "
        sql += "FROM public.downloads_by_uuid "
        sql += "WHERE user_id=(SELECT id FROM public.user WHERE email='{0}')".format(email)

        return self.__fetch(sql)

    def generateUUID(self, user_id):
        """
        Generates one UUID for one user.

        @return uuid, the UUID to user or None if no data was returned
        """
        sql = "INSERT INTO public.downloads_by_uuid(uuid,user_id) VALUES "
        sql += "(gen_random_uuid(), {0}) RETURNING uuid".format(user_id)

        ret_data={
            'uuid':None
        }
        data=self.__execSQL(sql,True)
        if(data!=None):
            ret_data={
                'uuid':data
            }
        return ret_data

    def storeClient(self, name, email, institution):
        """
        Store the client data.

        @return user_id, the user id or None if user email exists
        """
        sql = "INSERT INTO public.user(name,email,institution) VALUES "
        sql += "('{0}','{1}','{2}') ON CONFLICT (email) DO NOTHING RETURNING id".format(name,email,institution)

        ret_data={
            'user_id':None
        }
        data=self.__execSQL(sql,True)
        if(data!=None):
            ret_data={
                'user_id':data
            }
        return ret_data

    def __fetch(self, sql):
        data = None
        ret_data = {
            'uuid':None
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
                'uuid':data[0][0]
            }
        
        return ret_data

    def __execSQL(self, sql, withReturn=False):
        try:
            self.db.connect()
            if withReturn:
                data = self.db.execQuery(sql,True)
                self.db.commit()
                return data
            else:
                self.db.execQuery(sql)
                self.db.commit()
        except BaseException:
            self.db.rollback()
            raise DatabaseError('Query execute issue', sql)
        finally:
            self.db.close()
