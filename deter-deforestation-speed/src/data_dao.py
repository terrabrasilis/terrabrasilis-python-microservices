#!/usr/bin/python3
import os, sys
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../' ) )
from common_modules.configuration.src.common_config import ConfigLoader
from common_modules.postgresql.src.psqldb import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError


class DataDao:

    #constructor
    def __init__(self):
        
        relative_path = os.path.abspath(os.path.dirname(__file__) + '/config')
        self.db = PsqlDB(relative_path,'db.cfg','publish')

    def makeClusters(self, schema="public", working_table="deter_forest_monitor", buffer_len=0.000540541):
        """
        Discover deforestation scenarios using clusters to isolate each one.
        Before thing we try to drop the old cluster table.

        The buffer_len parameter is used to calculate the proximity between polygons to define if its is putting together on one cluster.
        Its value depends of the projection of the geographic data on analised table. The default value, 0.000540541, is in degrees and corresponds to 60 meters.

        Other configuration to compute clusters is the minimal points of proximity among polygons, minpoints, defined direct on code.

        To filter the candidates to compose the clusters, we have two more parameters,
        interval_filter used to obtain polygons up to 6 months old and
        classname_filter used to get only deforestation polygons.
        """
        minpoints=2
        interval_filter="6 month"
        classname_filter="'DESMATAMENTO_VEG','DESMATAMENTO_CR','MINERACAO'"

        sql = "DROP TABLE IF EXISTS public.deforestation_cluster;"
        self.__execSQL(sql)

        sql = "CREATE TABLE public.deforestation_cluster AS "
        sql += "SELECT cluster_id, ST_UNION(geom) AS cluster_geom, array_agg(parcel_id) AS ids_in_cluster FROM ( "
        sql += "SELECT tb1.id as parcel_id, ST_ClusterDBSCAN(tb1.geom, eps := {0}, minpoints := {1}) over () AS cluster_id, tb1.geom ".format(buffer_len, minpoints)
        sql += "FROM {0}.{1} as tb1 ".format(schema, working_table)
        sql += "WHERE tb1.view_date::date >= (now() - '{0}'::interval)::date ".format(interval_filter)
        sql += "AND tb1.classname in ({0}) ".format(classname_filter)
        sql += ") sq "
        sql += "GROUP BY cluster_id;"

        self.__execSQL(sql)

    def getClusters(self):
        """
        Read the cluster's id by dissolved polygons.
        """
        sql = "SELECT cluster_id FROM public.deforestation_cluster WHERE cluster_id IS NOT NULL GROUP BY cluster_id"
        return self.__fetch(sql)

    def computeParametersByClusterId(self, cluster_id, schema="public", working_table="deter_forest_monitor"):
        """
        Compute the contiguity and the deforestation speed and update values on working table.
        
        cluster_id used to isolate one deforestation scenario
        buffer_len is the offset used to identify direct relations among polygons of the one specifique scenario
        """
        sql =  "WITH statistic_pols AS ( "
        sql += "SELECT COUNT(*) as num_pols, SUM(areamunkm) as area, MIN(view_date::date) as start_date, MAX(view_date::date) as end_date, "
        sql += "CASE WHEN (MAX(view_date::date)-MIN(view_date::date)) > 0 THEN (MAX(view_date::date)-MIN(view_date::date)) ELSE 1 END as delta_t "
        sql += "FROM {0}.{1} ".format(schema, working_table)
        sql += "WHERE id in (SELECT unnest(ids_in_cluster) FROM public.deforestation_cluster where cluster_id={0}) ".format(cluster_id)
        sql += ") "
        sql += "UPDATE {0}.{1} ".format(schema, working_table)
        sql += "SET contiguity=1, speed=(area/delta_t) "
        sql += "FROM statistic_pols "
        sql += "WHERE num_pols > 1 AND id in (SELECT unnest(ids_in_cluster) FROM public.deforestation_cluster WHERE cluster_id={0}) ".format(cluster_id)
        
        self.__execSQL(sql)

        """
        Compute the percent of participation of one polygon into their cluster.
        """
        sql = "WITH cluster_data AS ( "
        sql += "SELECT ST_area(cluster_geom::geography)/1000000 as cluster_area, unnest(ids_in_cluster) as ids "
        sql += "FROM public.deforestation_cluster WHERE cluster_id={0} ".format(cluster_id)
        sql += ") "
        sql += "UPDATE public.deter_forest_monitor "
        sql += "SET participation=(ST_area(geom::geography)/1000000*100)/cluster_area "
        sql += "FROM cluster_data cd "
        sql += "WHERE id in (cd.ids) "
        
        self.__execSQL(sql)

    def resetParameters(self, schema="public", working_table="deter_forest_monitor"):
        """
        Reset contiguity to prevent the case when polygons that lost the cluster.
        - contiguity (integer)
        - participation (double precision)
        - speed (double precision)
        """
        sql = "UPDATE {0}.{1} SET contiguity=0, participation=0.0, speed=0.0;".format(schema, working_table)
        self.__execSQL(sql)

    def createParameters(self, schema="public", working_table="deter_forest_monitor"):
        """
        Prepare the table with new columns to receive new data if these columns don't exists.
        - contiguity (integer)
        - participation (double precision)
        - speed (double precision)
        """
        sql = "ALTER TABLE {0}.{1} ADD COLUMN IF NOT EXISTS contiguity integer DEFAULT 0;".format(schema, working_table)
        self.__execSQL(sql)
        sql = "ALTER TABLE {0}.{1} ADD COLUMN IF NOT EXISTS participation double precision DEFAULT 0.0;".format(schema, working_table)
        self.__execSQL(sql)
        sql = "ALTER TABLE {0}.{1} ADD COLUMN IF NOT EXISTS speed double precision DEFAULT 0.0;".format(schema, working_table)
        self.__execSQL(sql)

    def __fetch(self, sql):
        data = None
        try:
            self.db.connect()
            data = self.db.fetchData(sql)
        except BaseException:
            # by default return None
            return data
        finally:
            self.db.close()

        return data

    def __execSQL(self, sql):
        
        try:
            self.db.connect()
            data = self.db.execQuery(sql)
            self.db.commit()
        except BaseException as error:
            raise error
        finally:
            self.db.close()

    # def __execSQLWithMultiResults(self, sql):
    #     data = None
    #     ret_data = []
    #     try:
    #         self.db.connect()
    #         data = self.db.fetchData(sql)
    #     except BaseException:
    #         # by default return None
    #         return data
    #     finally:
    #         self.db.close()

    #     if(len(data)>1 and len(data[0])==3):
    #         for record in data:
    #             if(record[2]!=None):
    #                 row={
    #                     'num_polygons':record[0],
    #                     'date':record[1],
    #                     'area':record[2]
    #                 }
    #                 ret_data.append(row)
        
    #     return ret_data
