FrackBar
========

The Consumption sales tracker for Hackerspace Frack. This tool is used as a cash
register and helps to track which products are the most popular and which can be
removed from the inventory.

Tools
=====

The Tools folder contains some usefull tools to generate barcodes from the db.
Before using this tool, you have to make sure you have a filled and initialized
SQLite database.

Running
=======

On first run of 'frackbar.py' it will create all required files in ~/.frackbar/
including the SQLite database. It uses the file 'frackbar.schema' to create the
database and then uses 'frackbar.data' to fill the database with products.

Usage of the application is based on trust, it can be abused easily and is only
intended for situations where a trust-based system works.
