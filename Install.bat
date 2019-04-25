@echo off

set /p INSTALLPATH="Enter Installation PATH. Make sure the path does not contain spaces. (Default C:\Users\Public\SeqLearner): " || set INSTALLPATH="C:\Users\Public\SeqLearner"
md %INSTALLPATH%
echo Installation path: %INSTALLPATH%
set /p DOWNLOADPATH="Enter PATH where you unzipped the files. (Default C:%HOMEPATH%\Downloads\SeqLearn-master\SeqLearn-master): " || set DOWNLOADPATH="C:%HOMEPATH%\Downloads\SeqLearn-master\SeqLearn-master"
echo Download path: %DOWNLOADPATH%


echo "Select second copy option (directory)"
xcopy ""%DOWNLOADPATH%"" ""%INSTALLPATH%\SeqLearn"" /E

PowerShell -executionpolicy remotesigned -File "%INSTALLPATH%\SeqLearn\InstallAnaconda.ps1"
echo Downloading Anaconda. This may take a while. Press a key when you have finished installing it.
echo If downloading not working, download anaconda from https://repo.anaconda.com/archive/Anaconda3-5.2.0-Windows-x86_64.exe and install it in %INSTALLPATH%\Anaconda3
pause
del Anaconda.exe
set ANACONDAPATH=%INSTALLPATH%\Anaconda3
set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH%

echo Installing python environment and program. This may take a while.
cd %INSTALLPATH%\SeqLearn
conda create -y -n psychopyenv
call activate psychopyenv
conda install -y python=2.7.13
conda install -y -c anaconda pandas mysql-python sqlalchemy scikit-learn
conda install -y -c conda-forge sshtunnel wxpython=3.0
conda install -y -c cogsci psychopy pygame

echo Done installing python environment and program.

python SetUsername.py
call deactivate

echo set INSTALLPATH=%INSTALLPATH% > SequencePractice.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> SequencePractice.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> SequencePractice.bat
echo call activate psychopyenv >> SequencePractice.bat
echo echo Starting program. This may take a few seconds... >> SequencePractice.bat 
echo cd %INSTALLPATH%\SeqLearn >> SequencePractice.bat
echo python SeqLearn.py ^> NUL >> SequencePractice.bat
echo call deactivate >> SequencePractice.bat

echo set INSTALLPATH=%INSTALLPATH% > SequencePracticeDemo.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> SequencePracticeDemo.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> SequencePracticeDemo.bat
echo call activate psychopyenv >> SequencePracticeDemo.bat
echo cd %INSTALLPATH%\SeqLearn >> SequencePracticeDemo.bat
echo echo Starting program. This may take a few seconds... >> SequencePracticeDemo.bat 
echo python SeqLearn.py --demo ^> NUL >> SequencePracticeDemo.bat
echo call deactivate >> SequencePracticeDemo.bat

echo set INSTALLPATH=%INSTALLPATH% > UploadData.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> UploadData.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> UploadData.bat
echo call activate psychopyenv >> UploadData.bat
echo cd %INSTALLPATH%\SeqLearn >> UploadData.bat
echo echo Uploading data. This may take a few seconds... >> UploadData.bat 
echo python UploadData.py ^> NUL >> UploadData.bat
echo call deactivate >> UploadData.bat

echo set INSTALLPATH=%INSTALLPATH% > SequencePracticeSession.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> SequencePracticeSession.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> SequencePracticeSession.bat
echo call activate psychopyenv >> SequencePracticeSession.bat
echo echo Starting program. This may take a few seconds... >> SequencePracticeSession.bat 
echo cd %INSTALLPATH%\SeqLearn >> SequencePracticeSession.bat
echo set /p SESSNUM="Enter session number: " >> SequencePracticeSession.bat
echo python SeqLearn.py --session ^%SESSNUM^% ^> NUL >> SequencePracticeSession.bat
echo call deactivate >> SequencePracticeSession.bat

mkdir "%HOMEPATH%\Desktop\SeqLearnUtils"
move SequencePractice.bat "%HOMEPATH%\Desktop"
move SequencePracticeDemo.bat "%HOMEPATH%\Desktop"
move UploadData.bat "%HOMEPATH%\Desktop\SeqLearnUtils"
move SequencePracticeSession.bat "%HOMEPATH%\Desktop\SeqLearnUtils"

rm stats/*
rmdir stats

echo Done with installation.
