@echo off

Invoke-WebRequest https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe
Anaconda3-5.2.0-Windows-x86_64.exe
Invoke-WebRequest https://github.com/benjamingarzon/SeqLearn/archive/master.zip -OutFile SeqLearn.zip
unzip SeqLearn
set HOME=C:\Users\benjamin
set SEQDIR=%HOME%\Documents\SeqLearn

set PATH=%HOME%\Anaconda3\;%PATH%
cd %HOME%\Anaconda3
call activate envs\psychopyenv

cd %SEQDIR%
ls
python SeqLearn.py
call deactivate
pause
