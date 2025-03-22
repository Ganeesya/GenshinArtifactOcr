@echo off
powershell -Command "Start-Process cmd -Verb RunAs -ArgumentList '/c cd /d %cd% && %cd%\\.venv\\Scripts\\python.exe main.py & pause'"
