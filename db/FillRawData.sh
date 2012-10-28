#!/bin/bash

source ./DataAnalysis_env.sh

#mysql -u root -e "LOAD DATA LOCAL INFILE '/Users/zachdischner/Desktop/imgdb.csv' INTO TABLE rawdata FIELDS TERMINATED BY ','" test
mysql --local_infile=1 -u root -e "LOAD DATA LOCAL INFILE '$DataAnalysis/db/img_db.csv' INTO TABLE rawdata FIELDS TERMINATED BY ','" DayStar
