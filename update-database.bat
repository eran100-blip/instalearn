@echo off
rem Re-runs all database setup files (safe to run any time). Does not start the app.
call "%~dp0start-app.bat" --db-only --force-db
