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

    def makeBodyTable(self, dao, nextFriday, nextDateOfData, classes):
        # reference to weekly close
        todayDate = datetime.today().date()
        # get data from database
        data = dao.getNewAlertsDayByDay(classes)
        bodyHtml=[]
        weekTotalHtml=""
        itDate=None # crtl to print the provisioned last date of the release week
        if(todayDate>nextFriday):
            totalAreaLastWeek=0 # ctrl to sum area for last week
            for record in data:
                if(record["date"]<=nextFriday):
                    totalAreaLastWeek+=record["area"]
                    itDate=record["date"]

            totalAreaLastWeek=str(totalAreaLastWeek).replace('.',',')
            weekTotalHtml="""<tr style="color:black;background-color:#e1e1e1;">
            <td style="border-top:1px solid gray;" colspan="2">
            Fechamento semanal <b>de {0} até {1}</b></td>
            <td style="border-top:1px solid gray; colspan="1"><b>{2}</b> km²
            </td></tr>""".format(nextDateOfData.strftime('%d/%m/%Y'),(itDate).strftime('%d/%m/%Y') if itDate else '-',totalAreaLastWeek)

        index=1 # ctrl to alternate background color line
        for record in data:
            trStyle="#fafafa" if (index%2) else "#f1f1f1"
            index=index+1
            bodyHtml += [
                '<tr style="background-color:{1};"><td>{0}</td>'.format(record["date"].strftime('%d/%m/%Y') if record["date"] else '-', trStyle),
                '<td>{0}</td>'.format(record["num_polygons"]),
                '<td>{0} km²</td></tr>'.format(str(record["area"]).replace('.',',')),
            ]
            if(itDate==record["date"] and itDate>=nextFriday):
                bodyHtml += [weekTotalHtml]
        
        return bodyHtml

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

            # The date of the more recent data into the database released to the public.
            lastReleaseDate = dao.getDateOfLastReleaseData()
            currentDate = lastReleaseDate["date"].strftime('%d/%m/%Y')
            nextDateOfData = lastReleaseDate["date"] + timedelta(days=1)

            # The date used to release data weekly. Refers to the image date.
            publishDate = dao.getPublishDateOfLastReleaseData()
            nextFriday = publishDate["date"] + timedelta(days=7)
            nextRelease = (publishDate["date"] + timedelta(days=7)).strftime('%d/%m/%Y')
            releaseDate = (publishDate["date"] + timedelta(days=14)).strftime('%d/%m/%Y')

            bodyHtml=[]

            # By deforestation classes
            bodyHtml += [
                '<table cellspacing="0" cellpadding="4" border="0" style="background-color:#f1f1f1;width:500px;">',
                '<tr><td colspan="3" style="color:white;border-bottom:1px solid #adadad;background-color:#636363;">DESMATAMENTO - novos avisos.</td></tr>',
                '<tr style="color:darkblue;border-bottom:1px solid gray;background-color:#e1e1e1;"><td>Data da imagem</td><td>Número de polígonos</td><td>Área medida</td></tr>'
            ]
            
            bodyHtml += self.makeBodyTable(dao, nextFriday, nextDateOfData, deforestation_classes)

            data = dao.getNewAlerts(deforestation_classes)
            areaTotalDeforestation=data["area"]
            polTotalDeforestation=data["num_polygons"]
            intervalDeforestation='de {0} até {1}'.format(data["start_date"].strftime('%d/%m/%Y'),data["end_date"].strftime('%d/%m/%Y'))
            bodyHtml += [
                    '<tr><td colspan="3" style="color:black;border-bottom:1px solid gray;background-color:#e1e1e1;">DESMATAMENTO TOTAL {0}</td></tr>'.format(intervalDeforestation),
                    '<tr><td>Todas</td>',
                    '<td>{0}</td>'.format(polTotalDeforestation),
                    '<td>{0} km²</td></tr>'.format( str(areaTotalDeforestation).replace('.',',') ),
                ]

            bodyHtml += ['</table><br><br>']

            # By degradation classes
            bodyHtml += [
                '<table cellspacing="0" cellpadding="4" border="0" style="background-color:#f1f1f1;width:500px;">',
                '<tr><td colspan="3" style="color:white;border-bottom:1px solid #adadad;background-color:#636363;">DEGRADAÇÃO - novos avisos.</td></tr>',
                '<tr style="color:darkblue;border-bottom:1px solid gray;background-color:#e1e1e1;"><td>Data da imagem</td><td>Número de polígonos</td><td>Área medida</td></tr>'
            ]
            
            bodyHtml += self.makeBodyTable(dao, nextFriday, nextDateOfData, degradation_classes)
            
            data = dao.getNewAlerts(degradation_classes)
            areaTotalDegradation=data["area"]
            polTotalDegradation=data["num_polygons"]
            intervalDegradation='de {0} até {1}'.format(data["start_date"].strftime('%d/%m/%Y'),data["end_date"].strftime('%d/%m/%Y'))
            bodyHtml += [
                    '<tr><td colspan="3" style="color:black;border-bottom:1px solid gray;background-color:#e1e1e1;">DEGRADAÇÃO TOTAL {0}</td></tr>'.format(intervalDegradation),
                    '<tr><td>Todas</td>',
                    '<td>{0}</td>'.format(polTotalDegradation),
                    '<td>{0} km²</td></tr>'.format( str(areaTotalDegradation).replace('.',',') ),
                ]

            bodyHtml += ['</table><br><br>']

            if areaTotalDeforestation>0 or areaTotalDegradation>0:
                self.__sendMail(bodyHeader, bodyFooter, bodyHtml, currentDate, releaseDate, nextRelease)
            else:
                bodyHtml='<p><h3 style="color:red;">Não há incremento de área para publicar.</h3></p>'
                self.__sendMail(bodyHeader, bodyFooter, bodyHtml, currentDate, releaseDate, nextRelease)
            
        except BaseException as error:
            self.__writeLog(error)

    def __sendMail(self, bodyHeader, bodyFooter, bodyHtml, currentDate, releaseDate, nextRelease):

        pathToConfigFile = os.path.abspath(os.path.dirname(__file__) + '/config')

        bodyHtml = ''.join(bodyHtml)#.encode('utf-8')
        bodyHtml = """\
            <html>
                <head></head>
                <body>
                <p>
                <h3>{0}</h3>
                <h5>Dados liberados ao público até: {3}</h5>
                <h5>Em {4} serão liberados os dados até: {5}</h5>
                </p>
                {1}
                <p style="color:#C0C0C0;">{2}</p>
                </body>
            </html>
            """.format(bodyHeader, bodyHtml, bodyFooter, currentDate, releaseDate, nextRelease)
        try:
            ref_date=datetime.today().strftime('%d/%m/%Y %H:%M:%S')
            subject='[DETER-AMAZÔNIA] - Informe de avisos em {0}.'.format(ref_date)
            mail = SenderMail(pathToConfigFile)
            mail.send(subject, bodyHeader, bodyHtml)
        except BaseException as error:
            self.__writeLog(error)

    def __writeLog(self, error):

        with open(self.LOG_FILE, "a") as lf:
            lf.write(''.join(traceback.format_exception(etype=type(error), value=error, tb=error.__traceback__)))
            lf.write(datetime.today().strftime('%d/%m/%Y %H:%M:%S'))
            lf.write('-' * 50)