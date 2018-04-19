from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
 
# define queries
key_query = "CREATE TABLE keys_table (\
    key_id INT(6) NOT NULL AUTO_INCREMENT,\
    subject_id VARCHAR(20),\
    sess_num INT(3),\
    sess_date DATE,\
    sess_time TIME,\
    seq_type VARCHAR(10),\
    sess_type VARCHAR(10),\
    seq_train VARCHAR(10),\
    true_sequence VARCHAR(200),\
    obs_sequence VARCHAR(200),\
    accuracy DECIMAL(4, 3),\
    score DECIMAL(4, 3),\
    cumulative_trial INT(5),\
    trial INT(5),\
    trial_type INT(5),\
    keystroke INT(2),\
    key_from VARCHAR(10),\
    key_to VARCHAR(10),\
    RT DECIMAL(4, 3),\
    PRIMARY KEY (key_id)) ENGINE=InnoDB;"

trial_query = "CREATE TABLE trials_table (\
    trial_id INT(6) NOT NULL AUTO_INCREMENT,\
    subject_id VARCHAR(20),\
    sess_num INT(3),\
    sess_date DATE,\
    sess_time TIME,\
    seq_type VARCHAR(10),\
    sess_type VARCHAR(10),\
    seq_train VARCHAR(10),\
    cumulative_trial INT(5),\
    trial INT(5),\
    trial_type INT(5),\
    true_sequence VARCHAR(200),\
    obs_sequence VARCHAR(200),\
    RT DECIMAL(4, 3),\
    MT DECIMAL(4, 3),\
    accuracy DECIMAL(4, 3),\
    score DECIMAL(4, 3),\
    PRIMARY KEY (key_id)) ENGINE=InnoDB;"

# 19 fields
insert_key_query = "INSERT INTO keys_table(trial_id, subject_id, sess_num, \
sess_date, sess_time, seq_type, sess_type, seq_train, true_sequence, \
obs_sequence, accuracy, score, cumulative_trial, trial, trial_type, \
keystroke, key_from, key_to, RT) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\
%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

# 17 fields
insert_trial_query = "INSERT INTO trials_table(trial_id, subject_id, sess_num, \
sess_date, sess_time, seq_type, sess_type, seq_train, cumulative_trial, \
trial, trial_type, true_sequence, obs_sequence, RT, MT, accuracy, score) \
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

def create_tables():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor() 
        cursor.execute(key_query)
        cursor.execute(trial_query)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()

 
def query_with_fetchone():
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keys_table")
 
        row = cursor.fetchone()
 
        while row is not None:
            print(row)
            row = cursor.fetchone()
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()
 
 
def insert_data(keys_list, trials_list):
    try:
        db_config = read_db_config()
        conn = MySQLConnection(**db_config)
 
        cursor = conn.cursor()
        cursor.executemany(insert_key_query, keys_list)
        cursor.executemany(insert_trial_query, trials_list)
 
        conn.commit()
    except Error as e:
        print('Error:', e)
 
    finally:
        cursor.close()
        conn.close()
 
def main():
#    books = [('Harry Potter And The Order Of The Phoenix', '9780439358071'),
#             ('Gone with the Wind', '9780446675536'),
#             ('Pride and Prejudice (Modern Library Classics)', '9780679783268')]
#   insert_books(books)
#    query_with_fetchone() 
    create_tables()
    
if __name__ == '__main__':
    main()
 
