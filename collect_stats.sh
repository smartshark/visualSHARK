#!/bin/bash

# helper script for daily cron
# path may have to be adjusted
cd /srv/www/django-visualSHARK
./bin/python manage.py create_project_stats
