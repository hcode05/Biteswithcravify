@echo off
echo Starting Django server...
echo ==============================
cd /d "c:\Users\ADMIN\Desktop\foodproject"
python manage.py runserver 127.0.0.1:8000
echo ==============================
echo Server stopped. Check for errors above.
pause
