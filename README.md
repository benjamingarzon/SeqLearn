
# SeqLearn

A program for practicing discrete sequence production.

The main script is SeqLearn.py. To get help:


```
python SeqLearn.py -h

usage: SeqLearn.py [-h] [--schedule_file SCHEDULE_FILE]
                   [--config_file CONFIG_FILE] [--restart] [--demo]

optional arguments:
  -h, --help            show this help message and exit
  --schedule_file SCHEDULE_FILE
                        Enter schedule file.
  --config_file CONFIG_FILE
                        Enter configuration file.
  --restart             Remove previous data and start from session 1.
  --demo                Do a demo, no saving.
```


# Installation

## Dependencies 

Anaconda3.

## Linux manual installation

Install Anaconda3 and make sure it is in the PATH.

```
cd $INSTALLPATH\SeqLearn
conda env create -f psychopyenv.yml --force
conda install python=2.7.13
```


Download and unzip (or clone) the files into a directory INSTALLPATH. To create an environment with the necessary python packages:

```
cd $INSTALLPATH\SeqLearn
conda env create -f psychopyenv.yml --force
conda install python=2.7.13
```

Now run:
```
source activate psychopyenv
python SetUsername.py
```

This will configure the file 'config/user.json' with the user name and the schedule group. 
The schedule group can be 0 or 1 and allows to counterbalance sequences across subjects 
(trained sequences for schedule group are untrained for group 1 and viceversa). 
You can also do this manually.

```
{
"USERNAME": "subjectxxx", 
"SCHEDULE_GROUP": 0
}
```


To create a wrapper 'SequencePractice.sh' to run the program assign the correct variables to these variables: 

``` 
INSTALLPATH=/full/path/to/containing/SeqLearn/folder
ANACONDAPATH=/full/path/to/anaconda3
``` 

and then copy-paste to the terminal:

``` 
echo "INSTALLPATH=$INSTALLPATH" > SequencePractice.sh
echo "SEQDIR=$INSTALLPATH/SeqLearn" >> SequencePractice.sh
echo "PATH=$ANACONDAPATH/Scripts;$ANACONDAPATH;$PATH" >> SequencePractice.sh
echo "source activate psychopyenv" >> SequencePractice.sh
echo "cd $SEQDIR" >> SequencePractice.sh
echo "python SeqLearn.py" > /dev/null >> SequencePractice.sh
echo "source deactivate" >> SequencePractice.sh
chmod a+x SequencePractice.sh
```

Similarly, to create a wrapper for the demo:
``` 
echo "INSTALLPATH=$INSTALLPATH" > SequencePracticeDemo.sh
echo "SEQDIR=$INSTALLPATH/SeqLearn" >> SequencePracticeDemo.sh
echo "PATH=$ANACONDAPATH/Scripts;$ANACONDAPATH;$PATH" >> SequencePracticeDemo.sh
echo "source activate psychopyenv" >> SequencePracticeDemo.sh
echo "cd $SEQDIR" >> SequencePracticeDemo.sh
echo "python SeqLearn.py --demo" > /dev/null >> SequencePracticeDemo.sh
echo "source deactivate" >> SequencePracticeDemo.sh
chmod a+x SequencePracticeDemo.sh
```

Now you can move the wrappers wherever you want. 

# Windows
Run the script Installation.bat and follow the instructions. 
It will create shortcuts called SequencePractice.bat and SequencePracticeDemo.bat in your desktop directory that will run the program and a demo, respectively.  


## Database connections
To allow connections to the remote database, after installation save the private key inside the db directory in a file called 'db/id_rsa'.
Make sure that the subjects are 
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

To create a database and users: 

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

## Preparing a study

- Create a database and users.

- Create sequences that will be used (use SequenceStructure.Rmd).

- Create a schedule (use SeqGen.py).

- Adjust options in config/config.json.
