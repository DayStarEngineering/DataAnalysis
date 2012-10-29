__author__ = 'zachdischner'

# Notes/todos
# * Test out the INSERT and UPDATE scripts.
# * Migrate table creation specs out of this, move into the specific table classes
# * Remove anything specific to this database setup. Make it "Database.py" maybe. Then a "DayStar" wrapper. Then individual table wrappers.
# * Provision in 'FIND' for array of 'what' inputs


import MySQLdb as MDB           # MySQL wrapper for the _mysql module. Needed for other libraries and most interaction
import numpy as NP              # NumPY library for numbers and stuff
import datetime                 # Datetime utils
import sys                      # System utils
import pandas.io.sql as psql    # AWESOME wrapper for MySQL. Builds on MySQLdb, and makes SELECTing and sorting data easy.




class DatabaseConnect:
    """
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
    """
    def __init__(self, environment='stock_test',default_table='stock_test',debug=1):
        self.env = environment
        self.debug=debug
        self.default_table=default_table



    def class_info(self):
        """
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
        """
        atts=self.__dict__
        keys=atts.keys()
        print "Class Attributes Are:"
        for key in keys:
            print key," ==> ",atts[key]


    def MySQLconnect(self,env=None,info=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* MySQLconnect *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Simple function, provide a mysql connection to the caller
        #
        #   Inputs: {env}  -string-  The environment to connect to. I.E. 'test','development', ect
        #           {info} -logical- Set if you just want the configuration information
        #
        #   Outputs: {con} -obj-    A database connection object(?). With it, connect to, update, and retrive
        #                           data from the database, as specified by the 'env' variable.
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> my_connection=db.connect('my_environment')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """

        if env is None:
            env = self.env

        config = {
            'base': {'host':'localhost', 'user':'root', 'passwd':'','db':'test'},
            'stock_test': {'host':'localhost', 'user':'root', 'passwd':'', 'db':'test'},
            'rawdata': {'host':'localhost', 'user':'root', 'passwd':'', 'db':'DayStar'},
            'production': 3
                }
        if info is not None:
            return config[env]

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



    def select(self,query):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* select *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Executes SQL 'SELECT' statement, returns value as a PANDAS frame
        #
        #   Inputs:  {query} - String- The SQL select query to be performed
        #
        #   Outputs: {value} - Pandas Frame- Results of select query in the form of a Pandas Frame
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.select('SELECT * FROM test_table LIMIT 1')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        con = self.MySQLconnect(self.env)
        if self.debug:
            print query
        value = psql.frame_query(query,con=con)
        con.close()
        return value


    def insert(self,values,what=None,table=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* insert *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Insert values into a table. Must parse input array into SQL statement. Right now,
        #            only works for single row insert.
        #
        #   Inputs: {values} -Array- Values to insert into a row. String types use (') single quotes
        #           {what}   -String (optional)- Array of column names the 'values' array corresponds to
        #                      Used if not inserting a full new row, but only certain columns
        #           {table}  -String (optional)- Name of database table you are inserting into. If not
        #                     passed, 'table' is assumed to be class default. I.E.  DayStarDB.default_table()
        #
        #   Outputs: {none}
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.insert([1,2,3,4,5,6,7,8])
        #            or
        #            >>> db.insert(['zd',34,'2012-01-01'],what=['name','age','birth'])
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        if table is None:
            table=self.default_table
        #parse VALUES into a comma separated string list
        if values.__class__ == list:
            values = str(values)
            values = values.replace('[','')
            values = values.replace(']','')
            values = values.replace('"',"'") #Make sure correct string format
        if what is None:    #insert full row. I.E. values is an array, 1 value per table column
            insert_sql="INSERT INTO %s VALUES(%s)" % (table,values)
        else:           # Gotta specify the columns you are inserting.
            what=','.join(what)
            insert_sql="INSERT INTO %s (%s) VALUES (%s)" %(table,what,values)
        self.execute_statement(insert_sql)


    def update(self,what,where,value,table=None): #"update WHAT, set it equal to VALUE where(WHERE)"
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* update *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Update a single row in an SQL table
        #
        #   Inputs: {what}  -String- Column name we wish to update
        #           {value} -flexible- Numerical values to update into a row
        #           {where} -Array String- SQL "WHERE" condition. Used to identify the row you wish to update
        #           {table} -String (optional)- Name of database table you are inserting into. If not
        #                    passed, 'table' is assumed to be class default. I.E.  DayStarDB.default_table()
        #   Outputs: {none}
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.update('FirstName',['date>"2012-01-01"','LastName="foo"','gender="M"'], 'Ryan',table="MyTable")
        #            turns into:
        #               mysql >>> UPDATE MyTable SET FirstName='Ryan' WHERE(date>"2012-01-01" AND LastName="foo" AND gender="M")
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>-
        """
        if table is None:
            table=self.default_table
        if where.__class__ == list:
            where = ' AND '.join(where)
        update_sql="UPDATE %s SET %s=%s WHERE(%s)" % (table,what,value,where)
        self.execute_statement(update_sql)


    def find(self,what,where,table=None,limit=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* find *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Insert values into a table. Must parse input array into SQL statement. Right now,
        #            only works for single row insert.
        #
        #   Inputs: {what}      -String- String of 'What' you want to find. Can be multiple outputs in this
        #                        string, provided as a string with commas between values.
        #           {where}     -Array- Specs on how to filter table and return 'WHAT'. SQL arguments of WHERE
        #                        clauses
        #
        #           {table}     -String (optional)- Name of database table you are inserting into. If not
        #                        passed, 'table' is assumed to be class default. I.E.  DayStarDB.default_table()
        #
        #   Outputs: {result}  -Pandas Frame- Data structure mapped to database columns resulting from the
        #                       find statement.
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.find('FirstName','LastName="bar")
        #            or
        #            >>> db.find('FirstName',['LastName="bar",'age>37','gender="M")
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        if table is None:
            table = self.default_table
        if where.__class__ == list:
            where = ' AND '.join(where)
        select_sql = 'SELECT %s FROM %s WHERE (%s)' % (what,table, where)
        if limit is not None:
            select_sql += ' LIMIT %s' % limit
        return self.select(select_sql)


    def select_full_table(self,table=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* select_full_table *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Quickly load full table into Python for analysis
        #
        #   Inputs:  {table}  -String (optional)- Name of database table you are inserting into. If not
        #                      passed, 'table' is assumed to be class default. I.E.  DayStarDB.default_table()
        #
        #   Outputs: {result} -Pandas Frame- Data structure mapped to database columns resulting from the
        #                      find statement.
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> tabledata=db.select_full_table()
        #            or
        #            >>> tabledata=db.select_full_table(table="different_table")
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>-
        """
        if table is None:
            table = self.default_table
        select_sql = 'SELECT * FROM %s' % table
        return self.select(select_sql)


    def show_databases(self,to_list=0):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* show_databases *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Show all databases available using the current connection
        #
        #   Inputs:  {to_list}  -Logical (optional- Set if you want output converted to "list" type
        #
        #   Outputs: {databases} -Pandas Frame- Data structure that contains all databases found
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> databases=db.show_databases()
        #            or
        #            >>> databases=db.show_databases(to_list=1)
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>-
        """
        show_sql="SHOW DATABASES"
        databases = self.select(show_sql)
        if to_list:
            return databases.Database.tolist()
        else:
            return databases

    def show_tables(self,to_list=0):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* show_tables *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Show all tables available using the current connection, under the current database
        #
        #   Inputs:  {to_list}  -Logical (optional- Set if you want output converted to "list" type
        #
        #   Outputs: {tables} -Pandas Frame- Data structure that contains all tables found
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> tables=db.show_tables()
        #            or
        #            >>> tables=db.show_tables(to_list=1)
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        show_sql="SHOW TABLES"
        tables = self.select(show_sql)
        key=tables.keys()[0]                  #dynamically created. Its "tables.tables_in_test", or "tables.tables_in_daystar"
        if to_list:
            return eval('tables.'+key+'.tolist()')
        else:
            return tables

    def execute_statement(self,query):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* execute_statement *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Execute any SQL statement
        #
        #   Inputs:  {query}  -SQL String- SQL query you wish to execute. Typically its something outside
        #                      of usual SELECT, UPDATE, INSERT statements
        #
        #   Outputs: {None}   -Use 'select' or 'find' methods if you want to return things
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.execute_statement('USE new_database') #Switches databases.
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        try:
            if self.debug > 0:
                print "Your Query is '" + query +"'"
            con = self.MySQLconnect(self.env)
            cur = con.cursor()
            cur.execute(query)
            cur.close()
            con.close()
        except:
            print "Error in either SQL or environment setup"
            print self.MySQLconnect(info=1)



    def create_database(self,DBname):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* create_database *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Create a new database
        #
        #   Inputs:  {DBname}  -String- Name of the database you wish to create
        #
        #   Outputs: {None}
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.create_database('New_Database')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        create_sql = 'CREATE DATABASE IF NOT EXISTS %s' % DBname
        self.execute_statement(create_sql)

        # Verify that the database was created
        convert_to_list = 1
        if DBname in self.show_databases(convert_to_list):
            print "Hooray! Database   [%s]   was created successfully" % DBname
        else:
            print "Boo, Database   [%s]   was not created successfully" % DBname


    def drop_database(self,DBname):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* drop_database *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Drop a database, and all tables inside. Failsafe prompts are built in.
        #
        #   Inputs:  {DBname}  -String- Name of the database you wish to destroy
        #
        #   Outputs: {None}
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.drop_database('New_Database')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
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


    def describe_table(self,table=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* describe_table *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Output a description of a table. Handy for verifying column names and types.
        #
        #   Inputs:  {table}      -String (optional)- Name of the table you want to describe. By default
        #                          'table' is set to DayStarDB.default_table
        #
        #   Outputs: {description} -Pandas Frame- Containing the description of the table in question
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.describe_table()
        #            or
        #            >>> db.describe_table(table='different_table')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        if table is None:
            table = self.default_table

        if table not in self.show_tables(1):
            print "Table  >>" + table + "    is not in this database. Can't describe"
            return -1

        desc_query = 'DESCRIBE ' + table
        description = self.select(desc_query)
        return description



    def drop_table(self,table=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* drop_table *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Drop/Delete a table from the database
        #
        #   Inputs:  {table} -String (optional)- Name of table you wish to drop. If nothing is
        #                     specified, "DayStarDB.default_table()" will be used
        #
        #   Outputs: {None}  -Some printing and status statements outputted. No returns.
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.drop_table('Some Table')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        if table is None:
            table = self.default_table
        if table not in self.show_tables(1):
            print "Table named   %s   has not been defined for the database   %s   " % (table,self.env)
            return -1

        drop_table_sql = 'DROP TABLE IF EXISTS %s ;' % table
        self.execute_statement(drop_table_sql)

        # Verify The Drop
        convert_to_list = 1
        if table in self.show_tables(convert_to_list):
            print "Uh oh, table   [%s]   was not dropped correctly. It still exists" % table
        else:
            print "Table   [%s]   was dropped successfully " % table


    def create_table(self,table):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* create_table *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Add a new table to the database, with correct definitions
        #
        #   Inputs:  {table} -String- Table name and key for table definition specs. All provided here.
        #                     Eventually move to wrapper classes
        #
        #   Outputs: {None}  -Some printing and status statements outputted. No returns.
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.create_table('Some Table')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        if table.__class__ is not str:
            print "Single string input to DayStarDB.create_table. Reconsider your arguments"
            return -1
        print "You are about to (delete and re)create Table   [%s]   " % table

        table=table.lower()

        create_keys ={
            'rawdata':'CREATE TABLE rawdata ('+
                      'id BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,'    # Identifier
                      'drive VARCHAR(30),'                                 # Original Drive Location (/data1,/data2...)
                      'raw_fn VARCHAR(100) NOT NULL,'                      # Raw, unprocessed filename and path, excluding local DayStarDir
                      'seconds INT(10),'                                   # Seconds since 1970. 6 digit
                      'usec INT(6),'                                       # usec since last second
                      'hours DECIMAL(10,5),'
                      'time TIME,'                                         #(hours, minutes, seconds)-insert into foo (time) values("4:54:32");, must round to nearest second
                      'burst_num INT(4),'                                  # Burst number in sequence
                      'image_num INT(5),'                                  # Image number in burst
                      'gain boolean,'                                      # Gain. 1=high, low=0
                      'exposure INT(4),'                                   # Exposure time in [ms]
                      'PRIMARY KEY(id))'
        }

        if table not in create_keys.keys():
            print 'Table definition for   [%s]   has not been defined. ' % table
            print 'Update DayStarDB.create_table, or create it yourself'
            return -1

        # Drop the table
        self.drop_table(table)

        create_table_sql = create_keys[table]
        self.execute_statement(create_table_sql)

        # Verify Table Existence
        convert_to_list = 1
        if table in self.show_tables(convert_to_list):
            print "Table  [%s]  Was created successfully!" % table
        else:
            print "Table   [%s]   was not created successfully " % table



    def create_index(self,col,table=None):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* create_index *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Create a BTREE index on one of your table columns. (Its a SQL thing)
        #
        #   Inputs: {col} -String- The column you want to create the BTREE index on
        #           {table} -String (optional)- Name of table you are using to create an index under
        #                    If not specified "DayStarDB.default_table()" will be used
        #
        #   Outputs: {None}  -Some printing and status statements outputted. No returns.
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> db.create_index('age',table='people_table')
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        if table is None:
            table = self.default_table
        index_sql = "CREATE INDEX %s_index ON %s (%s) USING BTREE" % (col,table,col)
        if self.debug > 0:
            print "Creating BTREE index on     %s.%s" % (table,col)
        self.execute_statement(index_sql)



    def verify(self,prompt):
        """
        #*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^* verify *^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*^*
        #
        #   Purpose: Command line verification utility. Used in a lot of calls to make sure user
        #            does not destroy tables and databases on accident
        #
        #   Inputs:  {prompt}  -String- The question you wish the user to answer, in 'yes' or 'no' terms
        #
        #   Outputs: {choice}  -T/F- The user's decision based on the prompt
        #
        #   Usage  : >>> import DayStarDB as DayStar
        #            >>> db = Daystar.DatabaseConnect({optional specs})
        #            >>> ans = db.verify('Should I erase your hard drive after publishing your passwords to the inuternet? [yes/no]')
        #            >>> if ans then:
        #                    ...
        #
        #<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>---<*>
        """
        yes = set(['yes','y', 'ye'])
        no  = set(['no','n'])

        choice = raw_input(prompt).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            sys.stdout.write(prompt)


