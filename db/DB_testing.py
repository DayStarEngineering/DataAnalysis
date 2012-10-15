__author__ = 'zachdischner'


#import mysql.connector
import MySQLdb as MDB
import numpy as NP
import datetime
import sys
import pandas.io.sql as psql

class DatabaseConn:
    def __init__(self, environment='stock_test',default_table='stock_test',debug=1,):
        self.env = environment
        self.debug=debug
        self.default_table=default_table


    # Gotta import sys
    # sys.path.append('./db/')
    # import DB_testing as db
    # testdb=db.DatabaseConn)()

    #con = None
    #print "Now trying to test out a script or something to connect to my database"
    #env='stock_test'
    #print "You are using the  >>", env,"<< environment"



    #from collections import namedtuple
    #>>> xx=namedtuple("xx",x[0].keys())


    #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* MySQLconnect *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    #
    #   Purpose: Simple function, provide a mysql connection to the caller
    #
    #   Inputs: {none} May want to make 'env' an input.
    #
    #   Outputs: {con} - A database connection object(?). With it, connect to, update, and retrive
    #                    data from the database, as specified by the 'env' variable.
    #
    #   Usage  : >>> import DB_testing as db
    #            >>> my_connection=db.connect()
    #
    #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
    def MySQLconnect(self,env):
    # Homemade 'switch' statement. Connect automagically to the database environment of choice
        con = {
                  'stock_test': MDB.connect(host='localhost', user='root', passwd='', db='test'),
                  'development': 2,
                  'production': 3
                  }
        if env in con:
            connection= con[env]
        else:
            print 'invalid connection environment, returning stock_test connection'
            connection = con['stock_test']
        return connection



    def panda_select(self):
        con = self.MySQLconnect(self.env)
        value = psql.frame_query('select * from stock_test', con=con)
        return value

    def select(self,query):
        con = self.MySQLconnect(self.env)
        if self.debug:
            print query
        value = psql.frame_query(query,con=con)
        return value


    def find(self,what,where,table=None):
        if table is None:
            table = self.default_table
        if where.__class__ == list:
            where = ' AND '.join(where)
        select_sql = 'SELECT %s FROM %s WHERE (%s)' % (what,table, where)
        return self.select(select_sql)


    def select_full_table(self,table=None):
        if table is None:
            table = self.default_table
        select_sql = 'SELECT * FROM %s' % table
        return self.select(select_sql)




    def create_table(key):

        def switcher(key):
            return{
                ''

            }


#    def select(query, *args):
#
#        try:
#            cnx = self.MySQLconnect()
#            cursor = cnx.cursor(MDB.cursors.DictCursor)
#            cursor.execute(query, args)
#            result = cursor.fetchallDict()
#            cursor.close()
#            cnx.close()
#            return result
#
#        except MDB.Error, e:
#            print "Error %d: %s" % (e.args[0], e.args[1])
#            sys.exit(1)
#
#        finally:
#            if cnx.open:
#                cnx.close()


                # result[0]['volume']   => 10000. Yay!!!

