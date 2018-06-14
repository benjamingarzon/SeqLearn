set MYPATH=C:\Users\Public\SeqLearner
md %MYPATH%
xcopy "%HOMEPATH%\Downloads\SeqLearn-Master\SeqLearn-master" "%MYPATH%\SeqLearn" /E

PowerShell -executionpolicy remotesigned -File "%HOMEPATH%\SeqLearn\InstallAnaconda.ps1"
pause
del Anaconda.exe
set PATH=%MYPATH%\Anaconda3\Scripts;%MYPATH%\Anaconda3\;%PATH%

cd %MYPATH%\SeqLearn
conda env create -f psychopyenv.yml