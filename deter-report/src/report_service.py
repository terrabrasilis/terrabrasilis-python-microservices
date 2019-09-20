#!/usr/bin/python3
import os, sys
import traceback
from datetime import date, datetime, timedelta
from read_data_dao import ReadDataDao
sys.path.insert(0, os.path.realpath( os.path.realpath(os.path.dirname(__file__))+'/../../common_modules/email' ) )
from send import SenderMail

class ReportService:

    def __init__(self):
         # get env var setted in Dockerfile
        self.is_docker_env = os.getenv("DOCKER_ENV", False)
        # If the environment is docker then use the absolute path to write log file
        if self.is_docker_env:
            self.LOG_FILE='/usr/local/data/report_service.log'
        else:
            self.LOG_FILE=os.path.realpath(os.path.dirname(__file__)) + '/report_service.log'

    def generateReport(self):
        """
        Process the read data from publish database and generate the report.
        """

        bodyHeader='Informe diário sobre o programa DETER para a Amazônia Legal'
        bodyFooter='Att. Equipe do projeto DETER-AMZ.'

        try:
            dao = ReadDataDao()
            deforestation_classes="'MINERACAO','DESMATAMENTO_VEG','DESMATAMENTO_CR'"
            degradation_classes="'CICATRIZ_DE_QUEIMADA','CS_GEOMETRICO','CS_DESORDENADO','DEGRADACAO'"

            releaseDate = dao.getDateOfLastReleaseData()
            releaseDate = releaseDate["release_date"].strftime('%d/%m/%Y')
            #currentMonthYear = datetime.today().strftime('%m/%Y')

            bodyHtml=[]

            data = dao.getNewAlerts(deforestation_classes)
            newDeforestation=data["area"]
            bodyHtml += [
                '<table cellspacing="0" cellpadding="4" border="0" style="background-color:#f1f1f1;width:400px;">',
                '<tr><td colspan="2" style="color:darkblue;border-bottom:1px solid gray;">DESMATAMENTO - novos alertas (TOTAL).</td></tr>',
                '<tr><td>Número de polígonos:</td><td>{0}</td></tr>'.format(data["num_polygons"]),
                '<tr><td>Data inicial:</td><td>{0}</td></tr>'.format(data["start_date"].strftime('%d/%m/%Y') if data["start_date"] else '-'),
                '<tr><td>Data final:</td><td>{0}</td></tr>'.format(data["end_date"].strftime('%d/%m/%Y') if data["end_date"] else '-'),
                '<tr><td>Área medida:</td><td>{0} km²</td></tr>'.format(data["area"]),
                '</table><br><br>'
            ]

            data = dao.getNewAlertsDayByDay(deforestation_classes)
            bodyHtml += [
                '<table cellspacing="0" cellpadding="4" border="0" style="background-color:#f1f1f1;width:400px;">',
                '<tr><td colspan="3" style="color:darkblue;border-bottom:1px solid gray;">DESMATAMENTO - novos alertas (DIA A DIA).</td></tr>',
                '<tr><td>Data</td><td>Número de polígonos</td><td>Área medida</td></tr>'
            ]
            for record in data:
                bodyHtml += [
                    '<tr><td>{0}</td>'.format(record["date"].strftime('%d/%m/%Y') if record["date"] else '-'),
                    '<td>{0}</td>'.format(record["num_polygons"]),
                    '<td>{0} km²</td></tr>'.format(record["area"]),
                ]
            
            bodyHtml += ['</table><br><br>']

            data = dao.getNewAlerts(degradation_classes)
            newDegradation=data["area"]
            bodyHtml += [
                '<table cellspacing="0" cellpadding="4" border="0" style="background-color:#f1f1f1;width:400px;">',
                '<tr><td colspan="2" style="color:darkblue;border-bottom:1px solid gray;">DEGRADAÇÃO - novos alertas (TOTAL).</td></tr>',
                '<tr><td>Número de polígonos:</td><td>{0}</td></tr>'.format(data["num_polygons"]),
                '<tr><td>Data inicial:</td><td>{0}</td></tr>'.format(data["start_date"].strftime('%d/%m/%Y') if data["start_date"] else '-'),
                '<tr><td>Data final:</td><td>{0}</td></tr>'.format(data["end_date"].strftime('%d/%m/%Y') if data["end_date"] else '-'),
                '<tr><td>Área medida:</td><td>{0} km²</td></tr>'.format(data["area"]),
                '</table><br><br>'
            ]

            data = dao.getNewAlertsDayByDay(degradation_classes)
            bodyHtml += [
                '<table cellspacing="0" cellpadding="4" border="0" style="background-color:#f1f1f1;width:400px;">',
                '<tr><td colspan="3" style="color:darkblue;border-bottom:1px solid gray;">DEGRADAÇÃO - novos alertas (DIA A DIA).</td></tr>',
                '<tr><td>Data</td><td>Número de polígonos</td><td>Área medida</td></tr>'
            ]
            for record in data:
                bodyHtml += [
                    '<tr><td>{0}</td>'.format(record["date"].strftime('%d/%m/%Y') if record["date"] else '-'),
                    '<td>{0}</td>'.format(record["num_polygons"]),
                    '<td>{0} km²</td></tr>'.format(record["area"]),
                ]
            
            bodyHtml += ['</table><br><br>']

            if newDeforestation>0 or newDegradation>0:
                self.__sendMail(bodyHeader, bodyFooter, bodyHtml, releaseDate)
            else:
                bodyHtml='<p><h3 style="color:red;">Não há incremento de área para publicar.</h3></p>'
                self.__sendMail(bodyHeader, bodyFooter, bodyHtml, releaseDate)
            
        except BaseException as error:
            self.__writeLog(error)

    def __sendMail(self, bodyHeader, bodyFooter, bodyHtml, releaseDate):

        pathToConfigFile = os.path.abspath(os.path.dirname(__file__) + '/config')

        bodyHtml = ''.join(bodyHtml)#.encode('utf-8')
        bodyHtml = """\
            <html>
                <head></head>
                <body>
                <p>
                <h3>{0}</h3>
                <h4>Data de liberação ao público (referente a data de auditoria): {3}</h4>
                </p>
                {1}
                <p style="color:#C0C0C0;">{2}</p>
                </body>
            </html>
            """.format(bodyHeader, bodyHtml, bodyFooter, releaseDate)
        try:
            ref_date=datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            subject='[DETER-AMAZÔNIA] - Informe de novos alertas em {0}.'.format(ref_date)
            mail = SenderMail(pathToConfigFile)
            mail.send(subject, bodyHeader, bodyHtml)
        except BaseException as error:
            self.__writeLog(error)

    def __writeLog(self, error):

        with open(self.LOG_FILE, "a") as lf:
            lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            lf.write(datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
            lf.write('-' * 50)