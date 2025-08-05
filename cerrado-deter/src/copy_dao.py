#!/usr/bin/python3
import os
from configuration import ConfigLoader
from postgresql import PsqlDB
from app_exceptions import DatabaseError, MissingParameterError


class CopyDao:

    """
    The Copy Data Access Object reads the most recent data from DETER Cerrado production table
    and write them in one output table to DETER Cerrado publish table.

    The input and output databases may are in different hosts.
    See the db.cfg file for access the databases configuration definitions.
    See the model.cfg file for another configurations about the database tables names.

    """
    #constructor
    def __init__(self):
        relative_path = 'cerrado-deter/src/config/'
        self.inputdb = PsqlDB(relative_path,'db.cfg','production')
        self.outputdb = PsqlDB(relative_path,'db.cfg','publish')
        self.__loadConfigurations(relative_path)
        # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # get env var setted in docker stack
        self.date_to_copy = os.getenv("AUDITED_DATE", '2025-08-01')
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.data_dir='/usr/local/data/'
        else:
            self.data_dir=os.path.realpath(os.path.dirname(__file__) + '/../') + '/'


    def __loadConfigurations(self,relative_path):
        # read model parameters
        try:
            productioncfg = ConfigLoader(relative_path, 'model.cfg', 'production')
            self.production_cfg = productioncfg.get()
            publishcfg = ConfigLoader(relative_path, 'model.cfg', 'publish')
            self.publish_cfg = publishcfg.get()
        except Exception as configError:
            raise configError


    def copy(self, renew=False):
        """
        Start copy process

        The renew parameter is used to configure the behaviour of the copy process.
        If renew is equal True them the output table are dropped and all data will be copied.

        Return start and end date values.
        
        Will raise a DatabaseError if exception occured.

        Warning: This method opens connection, run the process and close connection.
        """

        max_audited_date = None

        try:

            if renew:
                # verify if table exists
                if self.__outputTableExists():
                    # DROP the output table for renew all data
                    self.__recreateOutputTable()
                # fixed date based on last clean interpretation database (created_date)
                max_audited_date = self.date_to_copy
            else:
                if not self.__outputTableExists():
                    self.__createOutputTable()

                max_audited_date = self.__getMaxAuditedDate()
                max_audited_date = max_audited_date if max_audited_date else self.date_to_copy

            if not max_audited_date:
                raise MissingParameterError('max_audited_date', 'Max audited date is not defined.')

            # copy data via SQL View
            self.__copyFromInputToOutput(max_audited_date)

            min_view_date, max_view_date, num_alerts = self.__getInformationAboutLastSync()

        except BaseException as error:
            raise error
        
        return min_view_date, max_view_date, num_alerts

    def __getMaxAuditedDate(self):
        """
        Read the last date from output table to audited date.

        Its used to filter new data from production database.

        @return string, one value, the max audited date.
        """
        audited = None

        if self.__outputTableExists():
            # select max date from output table
            sql = "SELECT MAX(audited_date::date)::varchar "
            sql += "FROM {0}.{1} ".format(self.publish_cfg["schema"], self.publish_cfg["table"])
            try:
                self.outputdb.connect()
                data = self.outputdb.fetchData(sql)
            except BaseException:
                # by default return None
                return audited
            finally:
                self.outputdb.close()

            if(len(data)==1 and len(data[0])==1):
                audited = data[0][0]
        
        return audited

    def __getInformationAboutLastSync(self):
        """
        Read the min and max view date from output table after copy.

        Its used to send email with sync information.

        @return string, three values, the minimum and maximum viewing date and the number of alerts copied.
        """
        min_view = max_view = num_alerts = None

        if self.__outputTableExists():
            # select max date from output table
            sql = "SELECT MIN(view_date::date)::varchar, MAX(view_date::date)::varchar, COUNT(*)"
            sql = f"{sql} FROM {self.publish_cfg["schema"]}.{self.publish_cfg["table"]} "
            sql = f"{sql} WHERE created_date = (now())::date"
            try:
                self.outputdb.connect()
                data = self.outputdb.fetchData(sql)
            except BaseException:
                # by default return None
                return min_view, max_view, num_alerts
            finally:
                self.outputdb.close()

            if(len(data)==1 and len(data[0])==3):
                min_view = data[0][0]
                max_view = data[0][1]
                num_alerts = data[0][2]
        
        return min_view, max_view, num_alerts

    def __createSQLView(self):
        """
        Create the SQL View called production_alert.
        This view is used to copy data from input table to output table.

        No return value but in error raise a DatabaseError exception.
        Warning: This method opens connection, run the process and close connection.
        """
        # connection to dblink
        dblink_connection = self.inputdb.getDBLinkConnection()

        sql = f"CREATE OR REPLACE VIEW {self.production_cfg["schema"]}.{self.production_cfg["table"]} "
        sql = f"{sql} AS "
        sql = f"{sql} SELECT remote_data.gid, "
        sql = f"{sql} remote_data.cell_oid, "
        sql = f"{sql} remote_data.uuid, "
        sql = f"{sql} remote_data.path_row, "
        sql = f"{sql} remote_data.sensor, "
        sql = f"{sql} remote_data.satellite, "
        sql = f"{sql} remote_data.class_name, "
        sql = f"{sql} remote_data.area_km, "
        sql = f"{sql} remote_data.view_date, "
        sql = f"{sql} remote_data.created_date, "
        sql = f"{sql} remote_data.audited_date, "
        sql = f"{sql} remote_data.geom "
        sql = f"{sql} FROM dblink('{dblink_connection}'::text, "
        sql = f"{sql} 'SELECT object_id as gid, cell_oid, uuid::text, path_row, sensor, satellite, class_name, area as area_km, view_date, "
        sql = f"{sql} created_date, audited_date, spatial_data as geom FROM {self.publish_cfg["schema"]}.{self.publish_cfg["table"]}'::text) "
        sql = f"{sql} remote_data(gid integer, cell_oid character varying(254), uuid text, path_row character varying(100), sensor character varying(100), "
        sql = f"{sql} satellite character varying(255), class_name character varying(254), area_km double precision, view_date date, "
        sql = f"{sql} created_date date, audited_date date, geom geometry(Polygon,4674)); "

        try:
            self.outputdb.connect()
            self.outputdb.execQuery(sql)
            self.outputdb.commit()
        except BaseException as error:
            self.outputdb.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.outputdb.close()

    def __dropSQLView(self):
        """
        Drop the SQL View called production_alert.
        """

        drop_view = "DROP VIEW IF EXISTS"
        try:
            self.outputdb.connect()
            sql = '{0} {1}.{2}'.format(drop_view, self.production_cfg["schema"], self.production_cfg["table"])
            self.outputdb.execQuery(sql)
            self.outputdb.commit()
        except Exception as error:
            self.outputdb.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.outputdb.close()


    def __copyFromInputToOutput(self, from_date=None, filter_area=0.03):
        """
        Copy data from input table to output table, filter by audited date and min area.
        That method is used to copy using the SQL View called production_alert.

        @param from_date: string, the date to start copy data.
        @param filter_area: number, the min area to get alert data.
        """

        if not from_date or not filter_area:
            raise MissingParameterError('From date or min area', 'From date or min area is not defined.')
        
        read_from_table = write_to_table = ""
        write_to_table = "{0}.{1}".format(self.publish_cfg["schema"], self.publish_cfg["table"])
        read_from_table = "{0}.{1}".format(self.production_cfg["schema"], self.production_cfg["table"])
        sql_filters = []

        if filter_area:
            sql_filters.append(f"ST_Area(ST_Transform(geom,4326)::geography)/1000000 > {filter_area}")

        if from_date:
            sql_filters.append(f"audited_date::date > '{from_date}' AND view_date IS NOT NULL")

        sql = f"INSERT INTO {write_to_table} (object_id, cell_oid, uuid, path_row, sensor, satellite, class_name, area_total_km, view_date, audited_date, spatial_data) "
        sql = f"{sql} SELECT gid, cell_oid, uuid, path_row, sensor, satellite, class_name, area_km, view_date, audited_date, ST_Multi(geom) "
        sql = f"{sql} FROM {read_from_table} "

        if len(sql_filters) > 0:
            sql = f"{sql} WHERE {" AND ".join(sql_filters)}"

        try:
            self.__createSQLView()

            self.outputdb.connect()
            self.outputdb.execQuery(sql)
            self.outputdb.commit()
        except BaseException as error:
            self.outputdb.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.outputdb.close()
            self.__dropSQLView()


    def __outputTableExists(self) -> bool:

        sql = "SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_name='{0}')".format(self.publish_cfg["table"])

        try:
            self.outputdb.connect()
            data = self.outputdb.fetchData(sql)
        except BaseException as error:
            raise error
        finally:
            self.outputdb.close()
        
        return data[0][0]

    def __recreateOutputTable(self):
        """
        Recreate the output table.
        This method is used when the output table exists and we want to copy all data from input table.

        No return value but in error raise a DatabaseError exception.
        Warning: This method opens connection, run the process and close connection.
        """

        self.__dropOutputTable()
        self.__createOutputTable()

    def __dropOutputTable(self):
        """
        Drop output table from the database.
        We using this method when want copy all data from input table and process that data and provide for API.

        No return value but in error raise a DatabaseError exception.
        Warning: This method opens connection, run the process and close connection.
        """

        drop_table = "DROP TABLE IF EXISTS"
        try:
            self.outputdb.connect()
            sql = '{0} {1}.{2}'.format(drop_table, self.publish_cfg["schema"], self.publish_cfg["table"])
            self.outputdb.execQuery(sql)
            self.outputdb.commit()
        except Exception as error:
            self.outputdb.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.outputdb.close()

    def __createOutputTable(self):

        sql = "CREATE TABLE {0}.{1} ".format(self.publish_cfg["schema"], self.publish_cfg["table"])
        sql += "( "
        sql += "object_id integer NOT NULL, "
        sql += "cell_oid character varying(255), "
        sql += "uuid text, "
        sql += "class_name character varying(20) NOT NULL DEFAULT 'DESMATAMENTO_CR'::character varying(20), "
        sql += "satellite text, "
        sql += "sensor text, "
        sql += "spatial_data geometry(MultiPolygon,4674), "
        sql += "area_total_km double precision, "
        sql += "path_row character varying(10), "
        sql += "quadrant character varying(1), "
        sql += "view_date date, "
        sql += "created_date date NOT NULL DEFAULT (now())::date, "
        sql += "audited_date date, "
        sql += "CONSTRAINT {0}_pk PRIMARY KEY (object_id) ".format(self.publish_cfg["table"])
        sql += ") "
        sql += "WITH ( "
        sql += "OIDS = FALSE "
        sql += ")"

        try:
            self.outputdb.connect()
            self.outputdb.execQuery(sql)
            self.outputdb.commit()
        except BaseException as error:
            self.outputdb.rollback()
            raise DatabaseError('Database error:', error)
        finally:
            self.outputdb.close()
