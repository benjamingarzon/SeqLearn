@echo off
set HOME=C:\Users\benjamin
set SEQDIR=%HOME%\Documents\projects\SeqLearn

set PATH=%HOME%\Anaconda3\;%PATH%
cd %HOME%\Anaconda3
call activate envs\psychopyenv

cd %SEQDIR%
ls
python SeqLearn.py
call deactivate
pause
