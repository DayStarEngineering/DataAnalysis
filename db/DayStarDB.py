__author__ = 'zachdischner'

# Notes/todos




#mysql -u root -e "LOAD DATA LOCAL INFILE '/Users/zachdischner/Desktop/imgdb.csv' INTO TABLE rawdata FIELDS TERMINATED BY ','" test

import MySQLdb as MDB           # MySQL wrapper for the _mysql module. Needed for other libraries and most interaction
import numpy as NP              # NumPY library for numbers and stuff
import datetime                 # Datetime utils
import sys                      # System utils
import pandas.io.sql as psql    # AWESOME wrapper for MySQL. Builds on MySQLdb, and makes SELECTing and sorting data easy.


#*^*^*^*^*^*^*^*^ Class ^*^*^*^*^*^*^*^* DatabaseConnect *^*^*^*^*^*^* Class *^*^*^*^*^*^*^*^*
#
#   Purpose: This class contains all database connectivity and interaction functionality.
#            For now, it is a mix of general utils and code specific to DayStar
#
#   Inputs: {env} -string (optional)- The environment to use. This is set at the class level, as
#                   many subroutines will rely on this class attribute. Default is set to the
#                   most used envitonment
#           {default_table} -string (optional)- The default table to perform all queries on. Methods
#                   will make use this attribute when no table input is provided. Useful for work with
#                   only a single table.
#           {debug} -int (optional)- Set to higher values to enable more print/debugging statements.
#
#   Outputs: {} -obj- an object instantiation of this class
#
#   Usage  : >>> import DayStarDB as DayStar
#            >>> db = Daystar.DatabaseConnect(test=2,environment='rawdata')
#
#<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>

class DatabaseConnect:
    def __init__(self, environment='stock_test',default_table='stock_test',debug=1):
        self.env = environment
        self.debug=debug
        self.default_table=default_table


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
    #   Inputs: {env} -string- The environment to connect to. I.E. 'test','development', ect
    #
    #   Outputs: {con} -obj- A database connection object(?). With it, connect to, update, and retrive
    #                       data from the database, as specified by the 'env' variable.
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

            #Redo with a TRY-EXCEPT statement
#
#            try:
#    ...     con=MDB.connect(host='localhost', user='root', passwd='', db='DayStar2')
#    ... except:
#    ...     con=MDB.connect(host='localhost', user='root', passwd='')

        config = {
            'base': {'host':'localhost', 'user':'root', 'passwd':'','db':'test'},
            'stock_test': {'host':'localhost', 'user':'root', 'passwd':'', 'db':'test'},
            'rawdata': {'host':'localhost', 'user':'root', 'passwd':'', 'db':'DayStar'},
            'production': 3
                }

        try:
            if env in config:                           # If we have defined the connection information

                my_config= config[env]
                if self.debug > 0:
                    print "Connecting using    >>" + env + "    environment"
                    print "Using configuration "
                    print my_config
                connection=MDB.connect(**my_config)     # Connect
            else:                                       # If we have NOT defined the connection information
                print 'invalid connection environment, returning generic connection'
                connection = MDB.connect(host='localhost', user='root')


        except:                                         # If the connection failed, probably DB was not defined yet
            print 'Error connecting to your environment. Possibly, the database has not been created.'
            print 'Generic Connection returning.'
            my_config = {'host':'localhost', 'user':'root', 'passwd':'','db':'test'}
            print my_config
            connection = MDB.connect(**my_config)

        # Return
        return connection

    # fast test method. Get rid of eventually
    def panda_select(self):
        con = self.MySQLconnect(self.env)
        value = psql.frame_query('select * from stock_test', con=con)
        return value


    #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* select *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
    #
    #   Purpose: Executes SQL 'SELECT' statement, returns value as a PANDAS frame
    #
    #   Inputs:  {query} -String- The SQL select query to be performed
    #
    #   Outputs: {value} -Pandas Frame- Results of select query in the form of a Pandas Frame
    #
    #   Usage  : >>> import DayStarDB as DayStar
    #            >>> db = Daystar.DatabaseConnect({optional specs})
    #            >>> db.select('SELECT * FROM test_table LIMIT 1')
    #
    #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
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
        key=tables.keys()[0]                  #dynamically created. Its "tables.tables_in_test", or "tables.tables_in_daystar"
        if to_list:
            return eval('tables.'+key+'.tolist()')
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


    def describe_table(self,TableName=0):
        if TableName is 0:
            TableName = self.default_table

        if TableName not in self.show_tables(1):
            print "Table  >>" + TableName + "    is not in this database. Can't describe"
            return -1

        desc_query = 'DESCRIBE ' + TableName
        description = self.select(desc_query)
        return description



    def drop_table(self,TableName):
        if TableName not in self.show_tables(1):
            print "Table named   %s   has not been defined for the database   %s   " % (TableName,self.env)
            return -1
#            sys.exit()

        drop_table_sql = 'DROP TABLE IF EXISTS %s ;' % TableName
        self.execute_statement(drop_table_sql)
        # Verify The Drop
        convert_to_list = 1
        if TableName in self.show_tables(convert_to_list):
            print "Uh oh, table   [%s]   was not dropped correctly. It still exists" % TableName
        else:
            print "Table   [%s]   was dropped successfully " % TableName

    def create_table(self,TableName):
        if TableName.__class__ is not str:
            print "Single string input to DayStarDB.create_table. Reconsider your arguments"
            return -1
        print "You are about to (delete and re)create Table   [%s]   " % TableName

        TableName=TableName.lower()

        create_keys ={
            'rawdata':'CREATE TABLE rawdata ('+
                      'id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,'    # Identifier
                      'drive VARCHAR(30),'                                 # Original Drive Location (/data1,/data2...)
                      'raw_fn VARCHAR(100) NOT NULL,'                      # Raw, unprocessed filename and path, excluding local DayStarDir
                      'seconds INT(10),'                                   # Seconds since 1970. 6 digit
                      'usec INT(6),'                                       # usec since last second
                      'hours float(10,10),'
                      'time TIME,'                                         #(hours, minutes, seconds)-insert into foo (time) values("4:54:32");, must round to nearest second
                      'burst_num INT(4),'                                  # Burst number in sequence
                      'image_num INT(5),'                                  # Image number in burst
                      'gain boolean,'                                      # Gain. 1=high, low=0
                      'exposure INT(4),'                                   # Exposure time in [ms]
                      'PRIMARY KEY(id))'
        }

        if TableName not in create_keys.keys():
            print 'Table definition for   [%s]   has not been defined. ' % TableName
            print 'Update DayStarDB.create_table, or create it yourself'
            return -1

        # Drop the table
        self.drop_table(TableName)

        create_table_sql = create_keys[TableName]
        self.execute_statement(create_table_sql)

        # Verify Table Existence
        convert_to_list = 1
        if TableName in self.show_tables(convert_to_list):
            print "Table  [%s]  Was created successfully!" % TableName
        else:
            print "Table   [%s]   was not created successfully " % TableName


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


