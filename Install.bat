@echo off

set /p MYPATH="Enter Installation PATH (Default C:\Users\Public\SeqLearner): " || set MYPATH="C:\Users\Public\SeqLearner"
md %MYPATH%
echo Installation path: %MYPATH%
xcopy "%HOMEPATH%\Downloads\SeqLearn-Master\SeqLearn-master" "%MYPATH%\SeqLearn" /E

PowerShell -executionpolicy remotesigned -File "%HOMEPATH%\SeqLearn\InstallAnaconda.ps1"
echo Downloading Anaconda. This may take a while. Press a key when you have finished installing it.
pause
del Anaconda.exe
set PATH=%MYPATH%\Anaconda3\Scripts;%MYPATH%\Anaconda3\;%PATH%

cd %MYPATH%\SeqLearn
echo Installing python environment and program. This may take a while.
conda env create -f psychopyenv.yml --force
conda install python=2.7.13
echo Done installing python environment and program.

call activate psychopyenv
python SetUsername.py
call deactivate

echo set MYPATH=%MYPATH% > SequencePractice.bat
echo set SEQDIR=%MYPATH%\SeqLearn >> SequencePractice.bat
echo set PATH=%MYPATH%\Anaconda3\Scripts;%MYPATH%\Anaconda3\;%PATH% >> SequencePractice.bat
echo call activate psychopyenv >> SequencePractice.bat
echo cd %SEQDIR% >> SequencePractice.bat
echo python SeqLearn.py >> SequencePractice.bat
echo call deactivate >> SequencePractice.bat

move SequencePractice.bat %HOMEPATH%\Desktop
echo Done with Installation.
