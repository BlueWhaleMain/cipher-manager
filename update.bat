@rem Copyright by BlueWhale. All Rights Reserved. Python���½ű�
@echo off
py -m pip install --upgrade pip
FOR /F "" %%i in (requirements.txt) do py -m pip install --upgrade %%i
echo ������������Ҫ���µİ�
py -m pip list --outdate
