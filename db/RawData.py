__author__ = 'zachdischner'


import DayStarDB
import sys
import subprocess


class RawDb(DayStarDB.DatabaseConnect):
    def __init__(self):
        debug = 1
        default_table = "rawdata"
        DayStarDB.DatabaseConnect.__init__(self,environment='rawdata',debug=debug,default_table=default_table) # Instantiate the class

        # Check to see if the 'DayStar' database exists
        if 'DayStar' not in self.show_databases(1):
            print "You don't appear to have a database set up for raw processing."
            prompt = "Do you want to create it now? [y/n]"
            if self.verify(prompt):
                self.initialize_raw_db()
        else:
            if debug > 0:
                print "You have successfully connected to the DayStar database system!"
                print "Query away with   {find}   or   {select}   statements."

        # Now Database exists, check for table existance
        if 'rawdata' not in self.show_tables(1):
            self.initialize_raw_table()
            self.seed_raw_table()
        print "You are now connected to and using the DayStar RAW database   >>('DayStar')"
        print "The table you are using is    >>('rawdata')"
        print "Search data with things like: "
        print "                                 >>raw.find('what','where')"
        print "                                 >>raw.select('sql query')"
        print "                                 >>raw.select_full_table()"



    def initialize_raw_db(self):
        self.create_database('DayStar')

    def initialize_raw_table(self):
        self.create_table('rawdata')

    def seed_raw_table(self):
        subprocess.call(["./db/FillRawData.sh"], shell=True)


    def reset_raw_db(self):
        self.drop_database('DayStar')
        self.initialize_raw_db(self)
        self.initialize_raw_table(self)
        self.seed_raw_table(self)

