__author__ = 'zachdischner'

#import mysql.connector
import MySQLdb as MDB
import datetime
import sys

# Gotta import sys
# sys.path.append('./')
# import DB_testing.py as db


con = None

print "Now trying to test out a script or something to connect to my database"

def select(query,*args):
#    cnx = mysql.connector.connect(user='root', database='test')
    cnx =MDB.connect(user='root', database='test')
    cursor = cnx.cursor()

    cursor.execute(query, args)
    for result in cursor:
        yield result
    cursor.close()
    cnx.close()

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
