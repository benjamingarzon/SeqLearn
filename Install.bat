@echo off

set /p INSTALLPATH="Enter Installation PATH. Make sure the path does not contain spaces. (Default C:\Users\Public\SeqLearner): " || set INSTALLPATH="C:\Users\Public\SeqLearner"
md %INSTALLPATH%
echo Installation path: %INSTALLPATH%
xcopy "%HOMEPATH%\Downloads\SeqLearn-Master\SeqLearn-master" "%INSTALLPATH%\SeqLearn" /E

PowerShell -executionpolicy remotesigned -File "%INSTALLPATH%\SeqLearn\InstallAnaconda.ps1"
echo Downloading Anaconda. This may take a while. Press a key when you have finished installing it.
pause
del Anaconda.exe
set ANACONDAPATH=%INSTALLPATH%\Anaconda3
set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH%

echo Installing python environment and program. This may take a while.
cd %INSTALLPATH%\SeqLearn
conda create -y -n psychopyenv
call activate psychopyenv
conda install -y python=2.7.13
conda install -y -c anaconda pandas mysql-python sqlalchemy
conda install -y -c conda-forge sshtunnel wxpython=3.0
conda install -y -c cogsci psychopy pygame

conda install -y -c numpy scipy matplotlib pandas pyopengl pillow lxml openpyxl xlrd configobj pyyaml gevent greenlet msgpack-python psutil pytables requests[security] cffi seaborn wxpython cython future pyzmq pyserial
conda install -y -c conda-forge pyglet pysoundfile python-bidi moviepy pyosf
pip install -y zmq json-tricks pyparallel sounddevice pygame pysoundcard psychopy_ext psychopy
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
echo call deactivate" >> SequencePractice.bat

echo set INSTALLPATH=%INSTALLPATH% > SequencePracticeDemo.bat
echo set SEQDIR=%INSTALLPATH%\SeqLearn >> SequencePracticeDemo.bat
echo set PATH=%ANACONDAPATH%\Scripts;%ANACONDAPATH%\;%PATH% >> SequencePracticeDemo.bat
echo call activate psychopyenv >> SequencePracticeDemo.bat
echo cd %INSTALLPATH%\SeqLearn >> SequencePracticeDemo.bat
echo echo Starting program. This may take a few seconds... >> SequencePracticeDemo.bat 
echo python SeqLearn.py --demo ^> NUL >> SequencePracticeDemo.bat
echo call deactivate" >> SequencePracticeDemo.bat

move SequencePractice.bat %HOMEPATH%\Desktop
move SequencePracticeDemo.bat %HOMEPATH%\Desktop
rm stats/*
rmdir stats

echo Done with installation.
