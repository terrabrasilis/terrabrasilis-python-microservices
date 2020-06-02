"""
Download WFS
Download Shapefile DETER

Copyright 2020 TerraBrasilis

Usage:
  download-deter-data.py

Options:
  no have

Disclaimer.

This is an example, therefore, we do not implement all error handling or cover all
problems related to the download process.
It is highly recommended that you improve and adapt this code to your specifics.

If you run this script in the same directory on the same day, the output file will be replaced.

Before start, read the tecnical posts into our Blog.
http://terrabrasilis.dpi.inpe.br/categoria/conteudo-tecnico/
"""

import requests, os
from requests.auth import HTTPBasicAuth
from datetime import datetime

class DownloadWFS:
  """
    Define configurations on instantiate.

    First parameter: user, The user name used to authentication on the server.

    Second parameter: password, The password value used to authentication on the server.
    
    To change the predefined settings, inside the constructor, edit the
    parameter values ​​in accordance with the respective notes.
    """

  def __init__(self,user=None,password=None):
    """
    Constructor with predefined settings.

    The start date is set by manually changing the value of the START_DATE parameter, below.

    The end date is automatically detected in the machine's calendar.

    The next filter on the states, uses the UF parameter and the
    values ​​are the acronyms of the state names, like PA or AM.

    Important note: If the range used to filter is very wide, the number
    of resources returned may be greater than the maximum limit allowed by the server.
    """

    # warning: before change the time interval, pay attention into notes on constructor.
    self.START_DATE="2020-01-01"
    self.END_DATE=datetime.today().strftime('%Y-%m-%d')
    self.UF="PA"

    self.WORKSPACE_NAME="deter-amz"
    # To change the desired layer, change the following value.
    # The public layer "deter_amz" or the controled layer "deter_amz_auth"
    self.LAYER_NAME="deter_amz"

    # The output file name (layer_name_start_date_end_date_uf)
    self.OUTPUT_FILENAME="{0}_{1}_{2}_{3}".format(self.LAYER_NAME,self.START_DATE,self.END_DATE, self.UF)
    self.AUTH=None

    if user and password:
      self.AUTH=HTTPBasicAuth(user, password)

    self.URL_BASE="terrabrasilis.dpi.inpe.br"

  def __buildQueryString(self):
    """
    Building the query string to call the WFS service.

    To change defined filters and discover more possibilities
    you should learn more about WFS standard and how to filter using CQL.
    https://www.ogc.org/standards/wfs
    """
    # Filters example (by date interval and uf)
    CQL_FILTER="date BETWEEN '{0}' AND '{1}' AND uf='{2}'".format(self.START_DATE,self.END_DATE,self.UF)
    # WFS parameters
    SERVICE="WFS"
    REQUEST="GetFeature"
    VERSION="2.0.0"
    # if OUTPUTFORMAT is changed, check the output file extension within the get method in this class.
    OUTPUTFORMAT="SHAPE-ZIP"
    exceptions="text/xml"
    # define the output projection. We use the layer default projection. (Geography/SIRGAS2000)
    srsName="EPSG:4674"
    # the layer definition
    TYPENAME="{0}:{1}".format(self.WORKSPACE_NAME,self.LAYER_NAME)
    
    allLocalParams=locals()
    allLocalParams.pop("self",None)
    PARAMS="&".join("{}={}".format(k,v) for k,v in allLocalParams.items())
    return PARAMS
  
  def get(self):
    url="http://{0}/geoserver/ows?{1}".format(self.URL_BASE, self.__buildQueryString())
    dir_name=os.path.realpath(os.path.dirname(__file__))
    # the extension of output file is ".zip" because the OUTPUTFORMAT is defined as "SHAPE-ZIP"
    output_file="{0}/{1}.zip".format(dir_name,self.OUTPUT_FILENAME)
    if self.AUTH:
      response=requests.get(url, auth=self.AUTH)
    else:
      response=requests.get(url)
    if response.ok:
      with open(output_file, 'wb') as f:
        f.write(response.content)
    else:
      print("Download fail with HTTP Error: {0}".format(response.status_code))

# To call without credentials (uses the public layer name)
down=DownloadWFS()

# To call with credentials (needs change the layer name)
#down=DownloadWFS("user_name","password")

# Call download
down.get()