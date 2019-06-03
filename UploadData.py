from sqlalchemy import create_engine, exc
import sshtunnel
import os, json, sys
from argparse import ArgumentParser
import pandas as pd
sys.path.append(os.path.join( os.path.dirname( __file__ ), '..' ))
from lib.utils import update_table
#import logging

sshtunnel.SSH_TIMEOUT = 20.0
sshtunnel.TUNNEL_TIMEOUT = 20.0

def upload_data(opts):
    
    if opts.users_file:
        usernames = list(pd.read_csv(opts.users_file, sep = ";", header=None)[0].values)        
    else:
        user_json = open("./config/user.json", "r")
        json_obj = json.load(user_json)
        username = json_obj["USERNAME"]
        usernames = [username]
    
    for username in usernames:

        db_config_json = open("./db/db_config.json", "r")
        db_config = json.load(db_config_json)
        db_config_json.close()

        if opts.fmri:
            database = db_config["DATABASE_FMRI"]
            keysfilename = "./data/keysfile-{}_fmri.csv".format(username)
            trialsfilename = "./data/trialsfile-{}_fmri.csv".format(username) 
            
        else:
            database = db_config["DATABASE"]
            keysfilename = "./data/keysfile-{}.csv".format(username)
            trialsfilename = "./data/trialsfile-{}.csv".format(username) 

        try:

            mykeys = pd.read_csv(keysfilename, sep = ";")
            mytrials = pd.read_csv(trialsfilename, sep = ";")
            print(username)

        except IOError: 
            continue
        

        try:    
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
                                                       database)
        
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

def build_parser():
    parser = ArgumentParser()

    parser.add_argument("--subjects", 
                        dest = "users_file", 
                        help = "Upload these subjects (list in a file).")

    parser.add_argument("--fmri", 
                        dest = "fmri", 
                        help = "Upload to fmri database.",
                        action="store_true",
                        required = False)
    return(parser)

def main():
    
    parser = build_parser()
    opts = parser.parse_args()
    upload_data(opts)    
    
if __name__ == '__main__':
 
    main()
