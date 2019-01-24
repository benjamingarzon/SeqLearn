
# SeqLearn

A program for practicing discrete sequence production.

The main script is SeqLearn.py. To get help:


```
usage: SeqLearn.py [-h] [--schedule_file SCHEDULE_FILE]
                   [--config_file CONFIG_FILE] [--restart] [--demo]
                   [--session SESSION] [--run RUN] [--fmri] [--no_upload]

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
  --ignore_misses       Ignore misses, don't repeat trial.  
```


# Installation

## Dependencies 

Anaconda3 (https://www.anaconda.com/download/).
Python packages: psychopy, sqlachemy, sshtunnel, wxpython, pandas.

## Linux manual installation

Install Anaconda3 and make sure it is in the PATH.

Download and unzip (or clone) the files into a directory INSTALLPATH. To create an environment with the necessary python packages:

```
mv $INSTALLPATH\SeqLearn-master $INSTALLPATH\SeqLearn
cd $INSTALLPATH\SeqLearn
conda create -y -n psychopyenv
source activate psychopyenv
conda install -y python=2.7.13
conda install -y -c anaconda pandas mysql-python-connector sqlalchemy
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
"SCHEDULE_GROUP": 0
}
```


To create a wrapper 'SequencePractice.sh' to run the program assign the correct variables to these variables: 

``` 
SEQDIR=/full/path/to/SeqLearn/folder
ANACONDAPATH=/full/path/to/anaconda3
``` 

and then copy-paste to the terminal:

``` 
echo "SEQDIR=$SEQDIR" > SequencePractice.sh
echo "PATH=$ANACONDAPATH/Scripts:$ANACONDAPATH:$PATH" >> SequencePractice.sh
echo "source activate psychopyenv" >> SequencePractice.sh
echo "cd $SEQDIR" >> SequencePractice.sh
echo "python SeqLearn.py" > /dev/null >> SequencePractice.sh
echo "echo Starting program. This may take a few seconds..." >> SequencePractice.sh 
echo "source deactivate" >> SequencePractice.sh
chmod a+x SequencePractice.sh
```

Similarly, to create a wrapper for the demo:
``` 
echo "SEQDIR=$SEQDIR" > SequencePracticeDemo.sh
echo "PATH=$ANACONDAPATH/Scripts:$ANACONDAPATH:$PATH" >> SequencePracticeDemo.sh
echo "source activate psychopyenv" >> SequencePracticeDemo.sh
echo "cd $SEQDIR" >> SequencePracticeDemo.sh
echo "echo Starting program. This may take a few seconds..." >> SequencePracticeDemo.sh 
echo "python SeqLearn.py --demo" > /dev/null >> SequencePracticeDemo.sh
echo "source deactivate" >> SequencePracticeDemo.sh
chmod a+x SequencePracticeDemo.sh
```

Now you can move the wrappers wherever you want. 

To clean unnecessary files:
``` 
rm -r $SEQDIR/stats
``` 

## Windows
Run the script Installation.bat and follow the instructions. 
It will create shortcuts called SequencePractice.bat and SequencePracticeDemo.bat in your desktop directory that will run the program and a demo, respectively.  

# Database connections
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

# Configuring the database

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
alter table keys_table add column global_clock double after clock_feedback;


alter table memo_table add column run int after "global_clock";
alter table trials_table add column run int after paced;
alter table keys_table add column run int after paced;

```

# Preparing a study

- Create a database and users.

- Create sequences that will be used (use SequenceStructure.Rmd).

- Create a schedule (use SeqGen.py).

- Adjust options in config/config.json.

- Configure database.

- Install software on training devices.

- In each device:
    
    - Copy private key to folder ./db/id_rsa
    - Copy db_config.json file to db/

# Schedule tables and groups
It is possible to use several schedules, so that different subjects are required to perform different sequences. 
Use flag  --schedule_file with the prefix of the file (e. g. scheduling/schedules/schedule000)
The schedule table is a file that assigns very subject to a schedule file, allowing training different 
sequences or schedules across subjects. The schedule group can be 0 or 1 and allows to counterbalance sequences across subjects 
(trained sequences for schedule group are untrained for group 1 and viceversa). 

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
Ver 1.3
# schedule group added automatically, needs files sequences_grouped_001_lund1_0.json and sequences_grouped_001_lund1_1.json
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_grouped_001_lund1 --schedule_file=./scheduling/schedules/lup0schedule1 --type_file=./scheduling/seq_types_lu0.csv

Older versions

python SeqGen.py --sequence_file=./scheduling/sequences/sequences_001.json --schedule_file=./scheduling/schedules/kip0schedule1 --type_file=./scheduling/seq_types.csv
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_demo.json --schedule_file=./scheduling/schedules/schedule_simple --type_file=./scheduling/seq_types_simple.csv --split

python SeqGen.py --sequence_file=./scheduling/sequences/sequences_001.json --schedule_file=./scheduling/schedules/kip1schedule1 --type_file=./scheduling/seq_types_ki1.csv
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_002.json --schedule_file=./scheduling/schedules/kip1schedule2 --type_file=./scheduling/seq_types_ki1.csv

python SeqGen.py --sequence_file=./scheduling/sequences/sequences_001.json --sequence_file2=./scheduling/sequences/sequences_002.json --schedule_file=./scheduling/schedules/kip1schedule1 --type_file=./scheduling/seq_types_ki1.csv
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_002.json --sequence_file2=./scheduling/sequences/sequences_001.json --schedule_file=./scheduling/schedules/kip1schedule2 --type_file=./scheduling/seq_types_ki1.csv


python SeqGen.py --sequence_file=./scheduling/sequences/sequences_lup2_001 --schedule_file=./scheduling/schedules/lup2schedule1 --type_file=./scheduling/seq_types_lup2.csv
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_lup2_002 --schedule_file=./scheduling/schedules/lup2schedule2 --type_file=./scheduling/seq_types_lup2.csv

```

Add a second type of sequences (unseen - DEPRECATED)
```
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_001.json --sequence_file2=./scheduling/sequences/sequences_002.json --schedule_file=./scheduling/schedules/kip0schedule1 --type_file=./scheduling/seq_types.csv
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_001.json --sequence_file2=./scheduling/sequences/sequences_002.json --schedule_file=./scheduling/schedules/kip1schedule1 --type_file=./scheduling/seq_types.csv
python SeqGen.py --sequence_file=./scheduling/sequences/sequences_002.json --sequence_file2=./scheduling/sequences/sequences_001.json --schedule_file=./scheduling/schedules/kip1schedule2 --type_file=./scheduling/seq_types.csv
```


# Function modes
## Home training
In the config.json file, set:
"MODE":"home"
"PRESHOW":1
"TEST_MEM":1

## fMRI experiment
In the config.json file, set:
"MODE":"fmri"
This will also set automatically:
"PRESHOW":0
"TEST_MEM":0
In the schedule file, set only paced trials (optional).

# Exporting the environment
```
conda env export -n psychopyenv > psychopyenv.yml
conda env export -n psychopyenv --no-builds > psychopyenv_nb.yml

```