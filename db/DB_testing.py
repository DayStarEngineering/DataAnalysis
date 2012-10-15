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



    def class_info(self):
        atts=self.__dict__
        keys=atts.keys()
        print "Class Attributes Are:"
        for key in keys:
            print key," ==> ",atts[key]

    #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* MySQLconnect *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    #
    #   Purpose: Simple function, provide a mysql connection to the caller
    #
    #   Inputs: {env} The environment to connect to. I.E. 'test','development', ect
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
            print 'invalid connection environment, returning generic connection'
            connection = MDB.connect(host='localhost', user='root')
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
        con.close()
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


    def create_database(self,DBname):
        con = self.MySQLconnect(self.env)
        cur = con.cursor()
        create_sql = 'CREATE DATABASE IF NOT EXISTS %s' % DBname
        cur.execute(create_sql)
        cur.close()
        con.close()
        # Verify that the database was created
        convert_to_list = 1
        if DBname in self.show_databases(convert_to_list):
            print "Hooray! Database   [%s]   was created successfully" %DBname
        else:
            print "Boo, Database   [%s]   was not created successfully" % DBname


    def drop_database(self,DBname):
        # Check for existance first, so as to not waste time
        convert_to_list = 1
        if DBname not in self.show_databases(convert_to_list):
            print "Database   [%s]   does not exist. So yeah, not bothering"
            return 1

        prompt = "You are about to DestroyExplode the database   [:%s]  Are you sure? [Yes/No]" % DBname
        if self.verify(prompt):
            drop_sql = "DROP DATABASE IF EXISTS %s" % DBname
            con = self.MySQLconnect(self.env)
            cur = con.cursor()
            cur.execute(drop_sql)
            cur.close()
            con.close()

            # Verify
            convert_to_list = 1
            if DBname in self.show_databases(convert_to_list):
                print "Uh oh, database   [%s]   was not dropped correctly. It still exists" %DBname
            else:
                print "Database   [%s]   was dropped successfully " % DBname


        else:
            print "Then DON'T WASTE MY TIME BITCH!!!"

        prompt = "Do you want to recreate database   [:%s]?  [Yes/No]" % DBname
        if self.verify(prompt):
            self.create_database(DBname)
        else:
            print "Good plan. Just do it later bro"


    def show_databases(self,to_list=0):
        show_sql="SHOW DATABASES"
        databases = self.select(show_sql)
        if to_list:
            return databases.Database.tolist()
        else:
            return databases






    def verify(self,prompt):
        yes = set(['yes','y', 'ye'])
        no  = set(['no','n'])

        choice = raw_input(prompt).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            sys.stdout.write(prompt)




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

