@echo off

set /p INSTALLPATH="Enter Installation PATH. Make sure the path does not contain spaces. (Default C:\Users\Public\SeqLearner): " || set INSTALLPATH="C:\Users\Public\SeqLearner"
md %INSTALLPATH%
echo Installation path: %INSTALLPATH%
xcopy "%HOMEPATH%\Downloads\SeqLearn-Master\SeqLearn-master" "%INSTALLPATH%\SeqLearn" /E

PowerShell -executionpolicy remotesigned -File "%HOMEPATH%\SeqLearn\InstallAnaconda.ps1"
echo Downloading Anaconda. This may take a while. Press a key when you have finished installing it.
pause
del Anaconda.exe
set ANACONDAPATH=%INSTALLPATH%\Anaconda3
set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH%

cd %INSTALLPATH%\SeqLearn
echo Installing python environment and program. This may take a while.
conda env create -f psychopyenv.yml --force
conda install python=2.7.13
echo Done installing python environment and program.

call activate psychopyenv
python SetUsername.py
call deactivate

echo set INSTALLPATH=%INSTALLPATH% > SequencePractice.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> SequencePractice.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> SequencePractice.bat
echo call activate psychopyenv >> SequencePractice.bat
echo cd %SEQDIR% >> SequencePractice.bat
echo python SeqLearn.py ^> NUL >> SequencePractice.bat
echo call deactivate" >> SequencePractice.bat

echo set INSTALLPATH=%INSTALLPATH% > SequencePracticeDemo.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> SequencePracticeDemo.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> SequencePracticeDemo.bat
echo call activate psychopyenv >> SequencePracticeDemo.bat
echo cd %SEQDIR% >> SequencePracticeDemo.bat
echo python SeqLearn.py --demo ^> NUL >> SequencePracticeDemo.bat
echo call deactivate" >> SequencePracticeDemo.bat

move SequencePractice.bat %HOMEPATH%\Desktop
move SequencePracticeDemo.bat %HOMEPATH%\Desktop
rmdir stats

echo Done with installation.
