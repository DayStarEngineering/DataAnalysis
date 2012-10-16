__author__ = 'zachdischner'

# Might want to get rid of EXECUTE_STATEMENT, SELECT with Pandas seems to work much better

import MySQLdb as MDB
import numpy as NP
import datetime
import sys
import pandas.io.sql as psql

class DatabaseConnect:
    def __init__(self, environment='stock_test',default_table='stock_test',debug=1,):
        self.env = environment
        self.debug=debug
        self.default_table=default_table


    # Gotta import sys
    # sys.path.append('./db/')
    # import DB_testing as db
    # testdb=db.DatabaseConnect)()

    #con = None
    #print "Now trying to test out a script or something to connect to my database"
    #env='stock_test'
    #print "You are using the  >>", env,"<< environment"



    #from collections import namedtuple
    #>>> xx=namedtuple("xx",x[0].keys())

    #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* class_info *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    #
    #   Purpose: Print out all class attributes. Gives insight into current class defaults
    #
    #   Inputs:  {} None
    #
    #   Outputs: {} No variable return. Just print statements in the python window
    #
    #   Usage  : >>> import DayStarDB as DayStar
    #            >>> db = Daystar.DatabaseConnect({optional specs})
    #            >>> db.class_info()
    #
    #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>


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
    #   Usage  : >>> import DayStarDB as DayStar
    #            >>> db = Daystar.DatabaseConnect({optional specs})
    #            >>> my_connection=db.connect('my_environment')
    #
    #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
    def MySQLconnect(self,env=None):
        if env is None:
            env = self.env
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


    def show_databases(self,to_list=0):
        show_sql="SHOW DATABASES"
        databases = self.select(show_sql)
        if to_list:
            return databases.Database.tolist()
        else:
            return databases

    def show_tables(self,to_list=0):
        show_sql="SHOW TABLES"
        tables = self.select(show_sql)
        if to_list:
            return tables.Tables_in_test.tolist()
        else:
            return tables

    def execute_statement(self,query):
        if self.debug > 0:
            print query
        con = self.MySQLconnect(self.env)
        cur = con.cursor()
        cur.execute(query)
        cur.close()
        con.close()



    def create_database(self,DBname):

        create_sql = 'CREATE DATABASE IF NOT EXISTS %s' % DBname
        self.execute_statement(create_sql)

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
            self.execute_statement(drop_sql)

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




    def create_table(self,TableName):
        if TableName.__class__ is not str:
            print "Single string input to DayStarDB.create_table. Reconsider your arguments"
            return -1
        print "You are about to (delete and re)create Table   [%s]   " % TableName

        TableName=TableName.lower()

        create_keys ={
            'rawdata':'CREATE TABLE rawdata ('+
                      'id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,'    # Identifier
                      'raw_fn VARCHAR(100) NOT NULL,'                      # Raw, unprocessed filename
                      'seconds INT(10),'                                   # Seconds since 1970. 6 digit
                      'usec INT(6),'                                       # usec since last second
                      'burst_num INT(4),'                                  # Burst number in sequence
                      'image_num INT(5),'                                  # Image number in burst
                      'gain boolean,'                                      # Gain. 1=high, low=0
                      'exposure INT(4),'
                      'time TIME,'                                          #(hours, minutes, seconds)-insert into foo (time) values("4:54:32");, must round to nearest second
                      'PRIMARY KEY(id))'
        }

        if TableName not in create_keys.keys():
            print 'Table definition for   [%s]   has not been defined. ' % TableName
            print 'Update DayStarDB.create_table, or create it yourself'
            return -1

        drop_table_sql = 'DROP TABLE IF EXISTS %s ;' % TableName
        self.execute_statement(drop_table_sql)
        # Verify The Drop
        convert_to_list = 1
        if TableName in self.show_tables(convert_to_list):
            print "Uh oh, table   [%s]   was not dropped correctly. It still exists" % TableName
        else:
            print "Table   [%s]   was dropped successfully " % TableName

        create_table_sql = create_keys[TableName]
        self.execute_statement(create_table_sql)

        # Verify Table Existence
        convert_to_list = 1
        if TableName in self.show_tables(convert_to_list):
            print "Table  [%s]  Was created successfully!" % TableName
        else:
            print "Table   [%s]   was dropped successfully " % TableName


