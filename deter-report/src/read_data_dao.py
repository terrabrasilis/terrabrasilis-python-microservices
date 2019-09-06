#!/usr/bin/python3
import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ) )
from common_modules.configuration.src.common_config import ConfigLoader
from common_modules.postgresql.src.psqldb import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError


class ReadDataDao:

    #constructor
    def __init__(self):
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config')
        self.db = PsqlDB(relative_path,'db.cfg','publish')

    def getLastAlerts(self, filter):
        """
        Read the last data from publishing table to last month.

        @return dict, the following values: {num_polygons,start_date,end_date,area}
        """
        sql = "SELECT COUNT(*) as num_polygons, MIN(date) as start_date, MAX(date) as end_date, SUM(areamunkm) as area "
        sql += "FROM terrabrasilis.deter_table "
        sql += "WHERE date <= (SELECT date FROM public.deter_publish_date) "
        sql += "AND to_char(date at time zone 'UTC', 'YYYY') = to_char(now() at time zone 'UTC', 'YYYY') "
        sql += "AND to_char(date at time zone 'UTC', 'MM') = to_char(now() at time zone 'UTC', 'MM') "
        sql += "AND areatotalkm >= 0.0625 "
        sql += "AND uf != ('MS') "
        sql += "AND classname in ({0})".format(filter)

        return self.__execSQL(sql)

    def getNewAlerts(self, filter):
        """
        Read the new data from publishing table to last month.

        @return dict, the following values: {num_polygons,start_date,end_date,area}
        """
        sql = "SELECT COUNT(*) as num_polygons, MIN(date) as start_date, MAX(date) as end_date, SUM(areamunkm) as area "
        sql += "FROM terrabrasilis.deter_table "
        sql += "WHERE date > (SELECT date FROM public.deter_publish_date) "
        sql += "AND to_char(date at time zone 'UTC', 'YYYY') = to_char(now() at time zone 'UTC', 'YYYY') "
        sql += "AND to_char(date at time zone 'UTC', 'MM') = to_char(now() at time zone 'UTC', 'MM') "
        sql += "AND areatotalkm >= 0.0625 "
        sql += "AND uf != ('MS') "
        sql += "AND classname in ({0})".format(filter)

        return self.__execSQL(sql)


    def getAllAlerts(self, filter):
        """
        Read the all data from publishing table to last month.

        @return dict, the following values: {num_polygons,start_date,end_date,area}
        """
        sql = "SELECT COUNT(*) as num_polygons, MIN(date) as start_date, MAX(date) as end_date, SUM(areamunkm) as area "
        sql += "FROM terrabrasilis.deter_table "
        sql += "WHERE to_char(date at time zone 'UTC', 'YYYY') = to_char(now() at time zone 'UTC', 'YYYY') "
        sql += "AND to_char(date at time zone 'UTC', 'MM') = to_char(now() at time zone 'UTC', 'MM') "
        sql += "AND date <= now() " # to protect the result if date is will major that today
        sql += "AND areatotalkm >= 0.0625 "
        sql += "AND uf != ('MS') "
        sql += "AND classname in ({0})".format(filter)

        return self.__execSQL(sql)
        
    def __execSQL(self, sql):
        data = None
        ret_data = {
            'num_polygons':0,
            'start_date':0,
            'end_date':0,
            'area':0
        }
        try:
            self.db.connect()
            data = self.db.fetchData(sql)
        except BaseException:
            # by default return None
            return data
        finally:
            self.db.close()

        if(len(data)==1 and len(data[0])==4 and data[0][3]!=None):
            ret_data={
                'num_polygons':data[0][0],
                'start_date':data[0][1],
                'end_date':data[0][2],
                'area':round(data[0][3],2)
            }
        
        return ret_data

    def getDateOfLastReleaseData(self):
        """
        Read the released date of the last data.
        """
        sql = "SELECT date FROM public.deter_publish_date"

        data = None
        ret_data = {
            'release_date':0,
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
                'release_date':data[0][0]
            }
        
        return ret_data

