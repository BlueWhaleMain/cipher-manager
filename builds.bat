@rem Copyright by BlueWhale. All Rights Reserved. Python�����ű�
@rem Encoding:GBK
@echo off
set name=%1
set ver=%2
set archive_type=%3
if not %archive_type%==release (
    rem �˴������ʱ�޷���������
    set ver=%ver%-%archive_type%-build_%date:~0,4%_%date:~5,2%_%date:~8,2%-%time:~0,2%_%time:~3,2%_%time:~6,2%
)
set before=%time%
if not "%2"=="" (
	echo ׼����...
	if not exist %~dp0dist (
		md %~dp0dist
	)
	if exist %~dp0dist\%name%\*.* (
		echo ɾ��dist�ļ�
		rd /s /q %~dp0dist\%name%\.
	)
    echo build����%~dp0%1
    .\.venv\Scripts\pyinstaller %name%.spec
    echo %errorlevel%
    if %errorlevel% GTR 0 goto end
    rem echo ɾ�������ݵ�����ʱ��
    rem del /f /q %~dp0dist\%name%\VCRUNTIME140.dll
    if not exist %~dp0dist\Publish (
        echo ���������ļ���
        md %~dp0dist\Publish
    )
	if exist %~dp0dist\Publish\%name%\*.* (
		echo ɾ�����ļ�
		rd /s /q %~dp0dist\Publish\%name%\.
	)
	if exist %~dp0dist\Publish\%name%-%ver%-win32.zip (
		echo ɾ��%~dp0dist\Publish\%name%-%ver%-win32.zip
		del /f /q %~dp0dist\Publish\%name%-%ver%-win32.zip
	)
	echo ѹ���ļ�...
	zip.py -i %~dp0dist\%name% -o %~dp0dist\Publish -n %name%-%ver%-win32.zip && attrib +r %~dp0dist\Publish\%name%-%ver%-win32.zip
	echo ������ʱ�ļ�...
	rd /s /q %~dp0dist\%name%\.
) else (
	echo ȱ�ٲ�����
	set errorlevel=2
	goto end
)
set after=%time%
if "%after:~,2%" lss "%before:~,2%" set "add=+24"
set /a times=(%after:~,2%-%before:~,2%%add%)*360000+(1%after:~3,2%%%100-1%before:~3,2%%%100)*6000+(1%after:~6,2%%%100-1%before:~6,2%%%100)*100+(1%after:~-2%%%100-1%before:~-2%%%100)
echo build��ɣ���ʱ��%times%0����

:end
