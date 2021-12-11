@rem Copyright by BlueWhale. All Rights Reserved. Python更新脚本
@echo off
py -m pip install --upgrade pip
FOR /F "" %%i in (requirements.txt) do py -m pip install --upgrade %%i
echo 下列是其他需要更新的包
py -m pip list --outdate
