__author__ = 'zachdischner'


import DayStarDB
import sys
import subprocess

# To use the raw database, do somethign like:
#   >>> raw=RawData.Connect()
#   >>> raw.find(stuff)
#   >>> raw.insert(stuff)
#
# See all method descriptions and documentation in "DayStarDB"


class Connect(DayStarDB.DatabaseConnect):
    def __init__(self,debug=0):
        self.debug=debug
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
        if debug > 0:
            print "You are now connected to and using the DayStar RAW database   >>('DayStar')"
            print "The table you are using is    >>('rawdata')"
            self.describe_table()
            print "Search data with things like: "
            print "                                 >>raw.find('what','where')"
            print "                                 >>raw.select('sql query')"
            print "                                 >>raw.select_full_table()"



    def initialize_raw_db(self):
        self.create_database('DayStar')

    def initialize_raw_table(self,seed=False):
        self.create_table('rawdata')
        if seed:
            self.seed_raw_table()
        print "Altering Table"
        self.execute_statement("ALTER TABLE rawdata ADD norm_fn VARCHAR(100) DEFAULT 0 AFTER raw_fn")
        self.execute_statement("ALTER TABLE rawdata ADD centroid_list VARCHAR(2000)")
        self.execute_statement("ALTER TABLE rawdata ADD quaternions VARCHAR(200)")



    def seed_raw_table(self):
        subprocess.call(["./db/FillRawData.sh"], shell=True)
        # Create indices on commonly queried columns
        self.create_index('hours')
        self.create_index('id')
        self.create_index('time')
        self.create_index('exposure')
        self.create_index('gain')


    def reset_raw_db(self):
        self.drop_database('DayStar')
        self.initialize_raw_db()
        self.initialize_raw_table()
        self.seed_raw_table()



#     Find quaternions in a database.
#           Returns a list of quats, given a WHERE statement.
#           like:
#               quats=DB.find_quats("burst_num=134")

    def find_quats(self,where):
        quatsDB=self.find('quaternions',where).quaternions
        quats=[]
        for q in quatsDB:
            if q is None:
                print "The quaternion does not exist in the database."
            else:
                quats.append(eval(q))

        return quats


#   Put a quaternion list into a database
#       give it a [quat], and the id where we want to insert it into.
#           *Gotta "select id,raw_fn from...
    def insert_quat(self,quat,id):
        self.update('quaternions','id=%s' % id,'"%s"' % quat)



#         Insert centroid list. Same as above.
#       *centroid_list is a list    [(x,y),(x,y)...]
    def insert_centroids(self,centroid_list,id):
        self.update('centroid_list','id=%s' % id,'"%s"' % centroid_list)


#   Same as above. Get list of centroid arrays based on a SQL where statement
    def find_centroids(self,where):
        centroidsDB=self.find('centroid_list',where).centroid_list
        centroids=[]
        for cent in centroidsDB:
            if cent is None:
                print "The centroid list does not exist in the database."
            else:
                centroids.append(eval(cent))

        return centroids