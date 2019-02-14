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

def connect(opts):
    """ Connect to MySQL database and delete tables."""
 
    username = opts.username
    password = opts.password
    
    db_config_json = open("./db/db_config.json", "r")
    db_config = json.load(db_config_json)
    db_config_json.close()
    database = opts.database if opts.database else db_config['DATABASE'] 
    
    if username == 'researcher':
        sql_name = 'researcher'
    else:
        sql_name = 'root'
        
    if opts.upload:
        mypath, mysuffix = opts.upload.split(",")
        sql_name = mysuffix
        
#    print db_config
    with sshtunnel.SSHTunnelForwarder(
            (db_config['REMOTEHOST'], 
            int(db_config['REMOTEPORT'])),
            ssh_username = username,
            ssh_password = db_config['SSH_PASS'],
            ssh_pkey = os.path.abspath(db_config['KEY']),
            remote_bind_address = (db_config['LOCALHOST'], 
                                   int(db_config['LOCALPORT']))
        ) as server:
            port = server.local_bind_port
            try:
                engine_string = 'mysql://%s:%s@%s:%d/%s'%(sql_name, 
                                               password, 
                                               db_config['LOCALHOST'],
                                               port,
                                               database)

                engine = create_engine(engine_string)
                
                if opts.delete:
 
                    if raw_input("Are you sure? (y/n): ").lower().strip()[:1] \
                    == "y": 
                    
                        engine.execute("drop table keys_table;")
                        engine.execute("drop table trials_table;")
                        engine.execute("drop table memo_table;")                    
                        print('Deleted all database tables!')

                if opts.upload:
                    
                    mymemo = pd.read_table(os.path.join(
                            mypath, 
                            "memofile-" + mysuffix + ".csv"), sep = ";")
                    mykeys = pd.read_table(os.path.join(
                            mypath, 
                            "keysfile-" + mysuffix + ".csv"), sep = ";")
                    mytrials = pd.read_table(os.path.join(
                            mypath, 
                            "trialsfile-" + mysuffix + ".csv"), sep = ";")

                    update_table(engine, "memo_table", mymemo, sql_name) 
                    update_table(engine, "trials_table", mytrials, sql_name)
                    update_table(engine, "keys_table", mykeys, sql_name) 
                 
                    print('Uploaded the data!')
                    
                if opts.download:
                    
                    now = datetime.datetime.now()    
                    print(now.strftime("Time stamp: %Y%m%d_%H%M")) 
                    if engine.dialect.has_table(engine, 'memo_table'):
                        mymemo = pd.read_sql_table('memo_table', engine)
                        mymemo.to_csv(now.strftime(
                                "./data/memo_table-%Y%m%d_%H%M-" + 
                                database + ".csv"), 
                                sep =";", index=False)
                        
                    if engine.dialect.has_table(engine, 'keys_table'):
                        mykeys = pd.read_sql_table('keys_table', engine)
                        mykeys.to_csv(now.strftime(
                                "./data/keys_table-%Y%m%d_%H%M-" + 
                                database + ".csv"), 
                                sep =";", index=False)
                    if engine.dialect.has_table(engine, 'trials_table'):
                        mytrials = pd.read_sql_table('trials_table', engine)
                        mytrials.to_csv(now.strftime(
                                "./data/trials_table-%Y%m%d_%H%M-" + 
                                database + ".csv"), 
                                sep =";", index=False)
                        
                    print('Downloaded the data!')
                    
                engine.dispose()

            except exc.SQLAlchemyError as e:
                print('Error:', e)

 
def build_parser():
    parser = ArgumentParser()

    parser.add_argument("--delete", 
                        dest = "delete", 
                        help = "Drop all tables.",
                        action="store_true",
                        required = False)

    parser.add_argument("--download", 
                        dest = "download", 
                        help = "Download the data.",
                        action="store_true",
                        required = False)


    parser.add_argument("--upload", 
                        type = str, 
                        dest = "upload", 
                        help = "Upload subject files to database. " + 
                        "UPLOAD = <Path, participant>",
                        required = False)

    parser.add_argument("--u", 
                        type = str, 
                        dest = "username", 
                        help = "Username.",
                        required = True)

    parser.add_argument("--p", 
                        type = str, 
                        dest = "password", 
                        help = "Password.",
                        required = True)

    parser.add_argument("--database", 
                        type = str, 
                        dest = "database", 
                        help = "Database.",
                        required = True)


    return(parser)

if __name__ == '__main__':

    parser = build_parser()
    opts = parser.parse_args()
    
    connect(opts)