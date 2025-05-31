# Izu Kampus Bilgi Sistemi Botu
A python application which automatically logins to student infofrmation system of IZU (Kampüs Bilgi Sistemi) with personal student mail and password.
Once logged in, the service checks the "grades" table under "Exam Results" section for any updates.
In case of new grade input by any lecturer, service sends a notification to students through a simple telegram bot including the grade, relaetd lecture and the time stamp of the change.
For web-scraping and browser automation, the service uses "selenium". 
For parsing the raw HTML's and data extraction, the service uses "beatifulsoup4".
As now, the service is working on GitHub Actions by executing "main.py" file every 10 minutes. 
Considering this project was established using GitHub Free plan, delays on workflows are inevitable.
Upcoming implementations are: Deploying the service on a web service providing less dilation times and upgrading the both service & bot for personal use for every student.
