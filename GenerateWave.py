# -*- coding: utf-8 -*-
"""
Created on Sat Apr 20 10:32:27 2019

@author: Benjamin.Garzon
"""
import pandas as pd
import json, os
import sshtunnel
from sqlalchemy import create_engine, exc
from lib.utils import get_config
from argparse import ArgumentParser


def GenerateWave(opts):
    config = get_config()
    create_db = opts.create_db
     
    N_SCHEDULE_GROUPS = config["N_SCHEDULE_GROUPS"]
    N_CONFIGURATIONS = config["N_CONFIGURATIONS"]
    
    NEXP = int(opts.nsubjects)#experimental
    NCONT = int(opts.nsubjects)#control 
    WAVE = int(opts.wave)
    OFFSET = int(opts.offset) if opts.offset else 0
    
    prefix = opts.prefix
    schedule_file = prefix + "1schedule"
    schedule_table_file = "./scheduling/tables/%s%d_schedule_table.csv"%(prefix, WAVE)
    # code : 1102 wave (1 digit), group (1 digit), subjectID (2 digits)
    subjects = [prefix + "%d1%0.2d"%(WAVE, i + 1) for i in range(NEXP)] + \
               [prefix + "%d2%0.2d"%(WAVE, i + 1) for i in range(NCONT)]
    group = [1 for i in range(NEXP)] + \
               [2 for i in range(NCONT)]
               
    # Generate schedule table
    schedule_group = 0
    row_list = []
    # add test subjects
    subjects = subjects + [ "%stest%d"%(prefix, i) for i in [1, 2, 3, 4]] 
    group = group + [1, 1, 2, 2]
    
    configuration = OFFSET
    for isub, subject in enumerate(subjects):
        row_list.append({'SUBJECT': subject, 
                               'SCHEDULE_FILE': schedule_file + "_g%d_c%d_s%d"%(group[isub], configuration + 1, schedule_group), 
                               'SCHEDULE_GROUP': schedule_group, 
                               'FMRI_SCHEDULE_FILE': schedule_file + "_g%d_c%d_s%d_fmri"%(group[isub],  configuration + 1, schedule_group),
                               'CONFIGURATION': configuration + 1
                               })
        schedule_group = (schedule_group + 1) % N_SCHEDULE_GROUPS
        configuration = (configuration + 1) % N_CONFIGURATIONS
        
    schedule_table = pd.DataFrame(row_list, columns = ['SUBJECT', 'SCHEDULE_FILE', 'FMRI_SCHEDULE_FILE',  'CONFIGURATION', 'SCHEDULE_GROUP'])
    schedule_table.to_csv(schedule_table_file, sep = ";", index = False)
    print("Subjects: ", subjects)
    print(schedule_table)
    
    # create db and subjects
    if create_db:
        try:
            db_config_json = open("./db/db_config.json", "r")
            db_config = json.load(db_config_json)
            db_config_json.close()
        
            with sshtunnel.SSHTunnelForwarder(
                    (db_config["REMOTEHOST"], 
                    int(db_config["REMOTEPORT"])),
                    ssh_username = opts.ssh_username,
                    ssh_password = db_config["SSH_PASS"],
                    ssh_pkey = os.path.abspath(db_config["KEY"]),
                    remote_bind_address = (db_config["LOCALHOST"], 
                                           int(db_config["LOCALPORT"]))
                ) as server:
                    port = server.local_bind_port
                    try:
                        engine_string = "mysql://%s:%s@%s:%d/%s"%(opts.sql_username, 
                                                       opts.sql_password, 
                                                       db_config["LOCALHOST"],
                                                       port,
                                                       db_config["DATABASE"])
        
                        engine = create_engine(engine_string)
                        
                        engine.execute("DROP DATABASE IF EXISTS %s" %(db_config["DATABASE"]))
                        engine.execute("CREATE DATABASE %s" %(db_config["DATABASE"]))
                        engine.execute("DROP DATABASE IF EXISTS %s" %(db_config["DATABASE_FMRI"]))
                        engine.execute("CREATE DATABASE %s" %(db_config["DATABASE_FMRI"]))
                        for subject in subjects:
                            command = "DROP USER IF EXISTS '%s'@'localhost'; CREATE USER '%s'@'localhost' IDENTIFIED BY '%s'; "%(subject, subject, db_config["SSH_PASS"]) + \
                            "GRANT INSERT,SELECT,CREATE,INDEX ON %s.* TO '%s'@'localhost';"%(db_config["DATABASE"], subject) + \
                            "GRANT INSERT,SELECT,CREATE,INDEX ON %s.* TO '%s'@'localhost';"%(db_config["DATABASE_FMRI"], subject)
                            print(command)
#                            engine.execute(command)
                        engine.dispose()
                        print("Synced with database.")
                    except exc.SQLAlchemyError as e:
                        print("Error:", e)
        
        except:
            print("Could not connect to database!")

def build_parser():
    parser = ArgumentParser()

    parser.add_argument("--ssh_username", 
                        dest = "ssh_username", 
                        help = "Add ssh username.",
                        required = False)

    parser.add_argument("--sql_username", 
                        dest = "sql_username", 
                        help = "Add sql username.",
                        required = False)

    parser.add_argument("--sql_password", 
                        dest = "sql_password", 
                        help = "Add sql password.",
                        required = False)

    parser.add_argument("--nsubjects", 
                        dest = "nsubjects", 
                        help = "Number of subjects.",
                        required = False)

    parser.add_argument("--wave", 
                        dest = "wave", 
                        help = "Wave number.",
                        required = False)

    parser.add_argument("--offset", 
                        dest = "offset", 
                        help = "Add an offset to the configuration, to balance configurations across waves.",
                        required = False)

    parser.add_argument("--create_db", 
                        dest = "create_db", 
                        help = "Create database.",
                        action="store_true",
                        required = False)

    parser.add_argument("--prefix", 
                        dest = "prefix", 
                        help = "Indicate prefix for files and subjects.",
                        required = True)

    return(parser)

def main():
    parser = build_parser()
    
    print("Generating wave...")
    opts = parser.parse_args()
    GenerateWave(opts)
    print("Done...!")
 

if __name__== "__main__":
  main()
