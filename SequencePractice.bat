set MYPATH=C:\Users\Public\SeqLearner
set SEQDIR=%MYPATH%\SeqLearn
set PATH=%MYPATH%\Anaconda3\Scripts;%MYPATH%\Anaconda3\;%PATH%
call activate psychopyenv
cd %SEQDIR%
python SeqLearn.py
call deactivate

 