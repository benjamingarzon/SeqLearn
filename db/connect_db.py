from sqlalchemy import create_engine, exc
import sshtunnel
import os, json, datetime
from argparse import ArgumentParser
sshtunnel.SSH_TIMEOUT = 5.0
sshtunnel.TUNNEL_TIMEOUT = 5.0
#import logging
import pandas as pd

def connect(opts):
    """ Connect to MySQL database and delete tables."""
 
    username = opts.username
    password = opts.password
    
    db_config_json = open("./db/db_config.json", "r")
    db_config = json.load(db_config_json)
    db_config_json.close()
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
                engine_string = 'mysql://%s:%s@%s:%d/%s'%('root', 
                                               password, 
                                               db_config['LOCALHOST'],
                                               port,
                                               db_config['DATABASE'])

                engine = create_engine(engine_string)
                
                if opts.delete:
                    engine.execute("drop table keys_table;")
                    engine.execute("drop table trials_table;")
                    engine.execute("drop table memo_table;")                    
                    print('Deleted all database tables!')

                if opts.download:
                    
                    now = datetime.datetime.now()

    
                    if engine.dialect.has_table(engine, 'memo_table'):
                        mymemo = pd.read_sql_table('memo_table', engine)
                        mymemo.to_csv(now.strftime(
                                "./data/memo_table-%Y%m%d_%H%M-" + 
                                db_config['DATABASE'] + ".csv"), 
                                sep =";", index=False)
                        
                    if engine.dialect.has_table(engine, 'keys_table'):
                        mykeys = pd.read_sql_table('keys_table', engine)
                        mykeys.to_csv(now.strftime(
                                "./data/keys_table-%Y%m%d_%H%M-" + 
                                db_config['DATABASE'] + ".csv"), 
                                sep =";", index=False)
                    if engine.dialect.has_table(engine, 'trials_table'):
                        mytrials = pd.read_sql_table('trials_table', engine)
                        mytrials.to_csv(now.strftime(
                                "./data/trials_table-%Y%m%d_%H%M-" + 
                                db_config['DATABASE'] + ".csv"), 
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

    return(parser)

if __name__ == '__main__':

    parser = build_parser()
    opts = parser.parse_args()
    
    connect(opts)