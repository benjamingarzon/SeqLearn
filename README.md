
# SeqLearn

A program for practicing discrete sequence production.

The main script is SeqLearn.py. To get help:


```
usage: SeqLearn.py [-h] [--schedule_file SCHEDULE_FILE]
                   [--config_file CONFIG_FILE] [--restart] [--demo]
                   [--session SESSION] [--run RUN] [--fmri] [--no_upload]
                   [--automate]

optional arguments:
  -h, --help            show this help message and exit
  --schedule_file SCHEDULE_FILE
                        Enter schedule file (with extension).
  --config_file CONFIG_FILE
                        Enter configuration file.
  --restart             Remove previous data and start from session 1.
  --demo                Do a demo, no saving.
  --session SESSION     Run only this session. Incompatible with --restart
  --run RUN             Run only this run. Incompatible with --restart
  --fmri                Run in fMRI mode.
  --no_upload           Do not upload the data to the database.
  --automate            Run automatically for testing.
```


# Installation

## Dependencies 

Anaconda3 (https://www.anaconda.com/download/).
Python packages: psychopy, cogsci, pygame, pandas, mysql-python, sqlalchemy, scikit-learn, sshtunnel, wxpython 3.0.


## Linux manual installation

Install Anaconda3 and make sure it is in the PATH.

To avoid errors install also AVBIN: https://github.com/downloads/AVbin/AVbin/AVbin10-win64.exe

Download and unzip (or clone) the files into a directory INSTALLPATH. To create an environment with the necessary python packages:

```
mv $INSTALLPATH\SeqLearn-master $INSTALLPATH\SeqLearn
cd $INSTALLPATH\SeqLearn
conda create -y -n psychopyenv
call activate psychopyenv
conda install -y python=2.7.13
conda install -y -c anaconda pandas mysql-python sqlalchemy scikit-learn
conda install -y -c conda-forge sshtunnel wxpython=3.0
conda install -y -c cogsci psychopy pygame

```

Now run:
```
python SetUsername.py
```

This will configure the file 'config/user.json' with the user name and the schedule table. You can also do this manually.

```
{
"USERNAME": "subjectxxx", 
"SCHEDULE_TABLE": "xxx_schedule_table"
}
```


To create wrappers to run the program and demo, see Install.bat. 

To clean unnecessary files:
``` 
rm -r $SEQDIR/stats
``` 

## Windows
Run the script Install.bat and follow the instructions. 
It will create shortcuts in your desktop directory:

SequencePractice.bat: runs the program
SeqLearnUtils\SequencePracticeDemo.bat: runs the demo
SeqLearnUtils\UploadData.bat: synchronizes with the database, in case the practice was done off line.
SeqLearnUtils\SequencePracticeSession.bat: runs the program, asking for the session first

# Database
## Database connections
To allow connections to the remote database, after installation save the private key inside the db directory in a file called 'db/id_rsa'.
Make sure that the subject has been created in the database. 
Configure database parameters in a file 'db/db_config.json':

```
{
"REMOTEHOST": "xxx.xxx.xxx.xxx",
"REMOTEPORT": 22,
"LOCALHOST": "127.0.0.1",
"LOCALPORT": 3306,
"SSH_USER": "xxx",
"SSH_PASS": "xxx",
"DATABASE": "xxx",
"DB_PASS": "xxx",
"KEY": "./db/id_rsa"
}
```

## Configuring the database

To create a database and users, from mysql: 

```
CREATE DATABASE zzzdb;
USE zzzdb;

CREATE USER 'subjectxxx'@'localhost' IDENTIFIED BY 'password';
GRANT INSERT,SELECT,CREATE,INDEX ON zzzdb.* TO 'subjectxxx'@'localhost';
```

To create several users:
```
for x in `seq 9`; do 
echo "CREATE USER 'subject00$x'@'localhost' IDENTIFIED BY 'password';"
echo "GRANT INSERT,SELECT,CREATE,INDEX ON zzzdb.* TO 'subject00$x'@'localhost';"
done
```

To check existing users and grants:
```
select user from mysql.user;
show grants for 'subject001'@'localhost';
```

To remove a user:
```
drop user 'subject001'@'localhost';
```

To add a column:
```
alter table keys_table add column stretch double after clock_feedback;


alter table memo_table add column run int after "global_clock";
alter table trials_table add column run int after paced;
alter table keys_table add column run int after paced;
alter table trials_table add column stretch int after block;
alter table keys_table add column stretch int after block;

```

For linux
```
sudo useradd -m -d /home/researcher researcher
sudo passwd

```

# Preparing a study

- Create a database and users (see GenerateWave.py).

- Create sequences that will be used (you can use SequenceStructure.Rmd).

- Create schedules and schedule_tables (use SeqGen.py and GenerateWave.py).

- Adjust options in config/config.json.

- Install software on training devices.

- In each device:
    
    - Copy private key to folder ./db/id_rsa
    - Copy db_config.json file to db/

# Schedule tables and groups

The schedule table is a file that assigns each subject to a schedule file, allowing training different groups of sequences and randomization. 

Configuration: a set of sequences.
Schedule group: indicates a particular randomization. 

# Generating a new wave
Use the script GenerateWave.py.
It will generate a number of subject IDs:
subject ID: prefix + wave (1 digit) + group (1 digit) + subjectID (2 digits), e.g. lue1101

```
python GenerateWave.py --nsubjects 20 --wave x --ssh_username xxx --sql_pass xxxx --sql_username xxx  --prefix lue --create_db 
```
This will generate new databases (for behaviour and fMRI) and a local schedule table, and create the subjects in the database. You need to specify first the database names in db_config.json.

# Generating sequences
Use the script called SeqGen.py. 
```
usage: SeqGen.py [-h] [--sequence_file SEQ_FILE] [--sequence_file2 SEQ_FILE2]
                 [--unseen UNSEEN] [--schedule_file SCHEDULE_FILE]
                 [--type_file TYPE_FILE] [--split] [--no_untrained]

optional arguments:
  -h, --help            show this help message and exit
  --sequence_file SEQ_FILE
                        Enter sequence file.
  --sequence_file2 SEQ_FILE2
                        Enter additional sequence file. It can be used for
                        non-memorized sequences or to vary untrained
                        sequences.
  --unseen UNSEEN       Add non-memorized sequences to test.
  --schedule_file SCHEDULE_FILE
                        Enter schedule file.
  --type_file TYPE_FILE
                        Enter sequence type file.
  --split               Returns separate files for training and testing
                        (_fMRI).
  --no_untrained        Ignore untrained sequences.
```
Example: 

```
# schedule group added automatically, needs files sequences_grouped_001_lund1_0.json and sequences_grouped_001_lund1_1.json
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_grouped_001_lund1 --schedule_file=./scheduling/schedules/lup0schedule1 --type_file=./scheduling/seq_types_lu0.csv

```

# Function modes
## Home training
In the config.json file, set:
"MODE":"home"
"ASK_USER":0

## Laptop with multiple users (e.g. different controls using the same laptop)
"MODE":"home"
"ASK_USER":1

## fMRI experiment
In the config.json file, set:
"MODE":"fmri"
"ASK_USER":1
In the schedule file, set only paced trials (optional).

# Exporting the environment
```
conda env export -n psychopyenv > psychopyenv.yml
conda env export -n psychopyenv --no-builds > psychopyenv_nb.yml

```


