from sqlalchemy import create_engine, exc
import sshtunnel
import os, json, datetime, sys
from argparse import ArgumentParser
import pandas as pd
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
from lib.utils import update_table
#import logging

sshtunnel.SSH_TIMEOUT = 20.0
sshtunnel.TUNNEL_TIMEOUT = 20.0

def upload_data():

    try:
                
        user_json = open("./config/user.json", "r")
        json_obj = json.load(user_json)
        username = json_obj["USERNAME"]

        keysfilename = "./data/keysfile-{}.csv".format(username)
        trialsfilename = "./data/trialsfile-{}.csv".format(username) 

        mykeys = pd.read_table(keysfilename, sep = ";")
        mytrials = pd.read_table(trialsfilename, sep = ";")
        
        db_config_json = open("./db/db_config.json", "r")
        db_config = json.load(db_config_json)
        db_config_json.close()
        #print(db_config)

        with sshtunnel.SSHTunnelForwarder(
                (db_config["REMOTEHOST"], 
                int(db_config["REMOTEPORT"])),
                ssh_username = db_config["SSH_USER"],
                ssh_password = db_config["SSH_PASS"],
                ssh_pkey = os.path.abspath(db_config["KEY"]),
                remote_bind_address = (db_config["LOCALHOST"], 
                                       int(db_config["LOCALPORT"]))
            ) as server:
                port = server.local_bind_port
                try:
                    engine_string = "mysql://%s:%s@%s:%d/%s"%(username, 
                                                   db_config["DB_PASS"], 
                                                   db_config["LOCALHOST"],
                                                   port,
                                                   db_config["DATABASE"])
    
                    engine = create_engine(engine_string)
    
                    update_table(engine, "keys_table", mykeys, 
                                 username) 
                    update_table(engine, "trials_table", mytrials, 
                                 username)
                    engine.dispose()
                    print("Synced with database.")
                except exc.SQLAlchemyError as e:
                    print("Error:", e)

    except:
        print("Could not connect to database!")
 

if __name__ == '__main__':

    upload_data()
