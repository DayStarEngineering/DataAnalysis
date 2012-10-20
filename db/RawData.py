__author__ = 'zachdischner'


import DayStarDB


def rawconnect():
    return DayStarDB.DatabaseConnect(environment='rawdata',debug=1,default_table='rawdata')
