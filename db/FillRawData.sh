#/bin/bash

pwd
source DataAnalysis_env.sh

#mysql -u root -e "LOAD DATA LOCAL INFILE '/Users/zachdischner/Desktop/imgdb.csv' INTO TABLE rawdata FIELDS TERMINATED BY ','" test
mysql -u root -e "LOAD DATA LOCAL INFILE '$DataAnalysis/db/img_db.csv' INTO TABLE rawdata FIELDS TERMINATED BY ','" DayStar