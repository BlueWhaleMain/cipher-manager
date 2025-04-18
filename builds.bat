@rem Copyright by BlueWhale. All Rights Reserved. Python构建脚本
@rem Encoding:GBK
@echo off
set name=%1
set ver=%2
set archive_type=%3
if not %archive_type%==release (
    rem 此处在零点时无法正常工作
    set ver=%ver%-%archive_type%-build_%date:~0,4%_%date:~5,2%_%date:~8,2%-%time:~0,2%_%time:~3,2%_%time:~6,2%
)
set before=%time%
if not "%2"=="" (
	echo 准备中...
	if not exist %~dp0dist (
		md %~dp0dist
	)
	if exist %~dp0dist\%name%\*.* (
		echo 删除dist文件
		rd /s /q %~dp0dist\%name%\.
	)
    echo build对象：%~dp0%1
    .\.venv\Scripts\pyinstaller %name%.spec
    echo %errorlevel%
    if %errorlevel% GTR 0 goto end
    rem echo 删除不兼容的运行时库
    rem del /f /q %~dp0dist\%name%\VCRUNTIME140.dll
    if not exist %~dp0dist\Publish (
        echo 创建发布文件夹
        md %~dp0dist\Publish
    )
	if exist %~dp0dist\Publish\%name%\*.* (
		echo 删除旧文件
		rd /s /q %~dp0dist\Publish\%name%\.
	)
	if exist %~dp0dist\Publish\%name%-%ver%-win32.zip (
		echo 删除%~dp0dist\Publish\%name%-%ver%-win32.zip
		del /f /q %~dp0dist\Publish\%name%-%ver%-win32.zip
	)
	echo 压缩文件...
	zip.py -i %~dp0dist\%name% -o %~dp0dist\Publish -n %name%-%ver%-win32.zip && attrib +r %~dp0dist\Publish\%name%-%ver%-win32.zip
	echo 清理临时文件...
	rd /s /q %~dp0dist\%name%\.
) else (
	echo 缺少参数！
	set errorlevel=2
	goto end
)
set after=%time%
if "%after:~,2%" lss "%before:~,2%" set "add=+24"
set /a times=(%after:~,2%-%before:~,2%%add%)*360000+(1%after:~3,2%%%100-1%before:~3,2%%%100)*6000+(1%after:~6,2%%%100-1%before:~6,2%%%100)*100+(1%after:~-2%%%100-1%before:~-2%%%100)
echo build完成！耗时：%times%0毫秒

:end
