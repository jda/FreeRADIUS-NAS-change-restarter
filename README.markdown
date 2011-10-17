# FreeRADIUS NAS change restarter
Yes, the name is a mouthful.

## What is this?
A MySQL table definition, triggers, and a python program to track changes to the NAS table and restart FreeRADIUS after ensuring that other RADIUS servers are running (to avoid creating downtime).

## Why would I use it?
* You run FreeRADIUS with a MySQL backend. 
* You have a web interface to add or change NAS definitions.
* You don't want to manually restart FreeRADIUS on each server every time you change a NAS with your web interface.
* Yes, FreeRADIUS only reads the NAS table once at startup: http://lists.cistron.nl/pipermail/freeradius-users/2005-June/msg00113.html

## What does it need to run? 
* Python 2
* pyrad 2: http://pypi.python.org/pypi/pyrad/2.0
* MySQL for Python

## How do I use this?
* Create the NAS updates table by loading sql/table.sql into MySQL.
* Load triggers from sql/triggers.sql
* Customize reloader.json for your environment. Save reloader.json to /etc/reloader.json
* Make sure /var/lib/reloader exists and the user that will run reloader has read and write permissions to it.
* Run reloader.py from cron every 5 minutes or so.

