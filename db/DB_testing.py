__author__ = 'zachdischner'

#import mysql.connector
import MySQLdb as MDB
import numpy as NP
import datetime
import sys

# Gotta import sys
# sys.path.append('./')    - in top dir,    sys.path.append('./db/')
# import DB_testing.py as db

con = None
print "Now trying to test out a script or something to connect to my database"


#from collections import namedtuple
#>>> xx=namedtuple("xx",x[0].keys())



def select(query,*args):
    try:
#    cnx = mysql.connector.connect(user='root', database='test')
        cnx = MDB.connect(host='localhost', user='root', passwd='', db='test')    # host, user, password, database
        cursor = cnx.cursor(MDB.cursors.DictCursor)

        cursor.execute(query, args)
    #    for result in cursor:
    #        yield result
        result = cursor.fetchallDict()

        cursor.close()
        cnx.close()
        return result

    except MDB.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    finally:
        if cnx.open:
            cnx.close()

# result[0]['volume']   => 10000. Yay!!!


#try:
#
#    con = _mysql.connect('localhost', 'root', '','stocks')
#
#    con.query("SELECT VERSION()")
#    result = con.use_result()
#
#    print "MySQL version: %s" %\
#          result.fetch_row()[0]
#
#except _mysql.Error, e:
#
#    print "Error %d: %s" % (e.args[0], e.args[1])
#    sys.exit(1)
#
#finally:
#
#    if con:
#        con.close()




#select('SELECT * FROM STOCK_TEST LIMIT 1')

