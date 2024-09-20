@if (@CodeSection == @Batch) @then

call ..\env_GMAP_new\Scripts\activate
call set JUPYTER_PLATFORM_DIRS=1
call jupyter --paths
call cd ..\GMAP
echo %cd%
echo "hello"

@echo off

rem Use %SendKeys% to send keys to the keyboard buffer
set SendKeys=CScript //nologo //E:JScript "%~F0"

rem Send to the keyboard buffer the desired line
%SendKeys% "pytest --cov-report term-missing:skip-covered --cov=src -x tests{ENTER}"

rem Read it, so it is inserted in the command-line history
set /P "variable="

goto :EOF


@end

// JScript section

var WshShell = WScript.CreateObject("WScript.Shell");
WshShell.SendKeys(WScript.Arguments(0));