# Read Me File 

This project is written and based in Python. The front-end consist of HTML, JavaScript, CSS, and Twitter Boostrapt. It is a website that hold catalog items for a Sport shop. Back-end technologies implemented in this project are:  Flask Framework, JinJa Templates, SqlAlchemy, and Python 2.7  Users can login through Facebook and/or Google, and add catalog item's to their favorite extreme sport catalogs.  

## Version
This is the first release of the website.
Goal of this release:  Grading from Udacity Instructors

## Table of Contents
- [Introduction](#introduction)
- [Technologies](#technologies)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Contents](#contents)
- [References](#references)

---
#### Introduction

This project is designed to: teach how to create and use persistent databases through the implementation of Object Relational Mapping of SqlAlchemy, and how to manipulate the data inside the database and in the context of a framework.  It also serves on how implement OAuthentication and filtering CRUD action based on user's state in the website session.

 This project has two parts: defining the database schema (SQL table definitions) in ORM, and writing code that will use it serve a website with OAuth implementation of Google and Facebook.

---
#### Technologies
-  SqlAlchemy - Database
-  Flask Version 10.0
-  Facebook OAuth 2.4
-  Google OAuth
-  Boostrap
-  Python 2.7 - Scripting Language
-  Vagrant - Virtualization Environment
-  Virtual Box - Virtual Machine

---
#### System Requirements
For the following software, choose the installation appropiate to your Operative System.
- [Virtual Box Version 5.0](https://www.virtualbox.org/wiki/Downloads)
- [Python Version 2.7](https://www.python.org/downloads/)
- [Vagrant Version 1.8.1](https://www.vagrantup.com/downloads.html)
- [Python IDE - IDLE](https://docs.python.org/3/library/idle.html)
- Command Line or Terminal.

---
#### Installation
1. First, fork the [fullstack-nanodegree-vm repository](#https://www.google.com/url?q=http://github.com/udacity/fullstack-nanodegree-vm&sa=D&ust=1458487900160000&usg=AFQjCNHBQhACq_wS9zRVL9hdU0GzvSaU2w) so that you have a version of your own within your Github account.

2. Next, clone your fullstack-nanodegree-vm repo to your local machine.

3. Open your Git terminal, and type 'python application.py'

4. Go to your webbrowser and type in the address bar:  http://localhost:8000/

5. Enjoy the website!

##### Using the Vagrant Virtual Machine

The Vagrant VM has SqlAlchemy installed and configured.

To use the Vagrant virtual machine, navigate to the `full-stack-nanodegree-vm/Catalog directory in the terminal`, then:
- Use the command `vagrant up` (powers on the virtual machine).
- Use the command `vagrant ssh` (logs into the virtual machine). 
- Use the command `cd /vagrant` to change directory to the synced folders in order to work on your project.
- And finally use the command `ls` on the command line, you'll see your tournament folder.

##### To run the script

In the command line (and while inside the directory `/vagrant/Catalog`) type `python application.py`.

---
### Contents

File | Description | Contains
--- | --- | ---
**application.py**| Contains Python modules with execution of main modules.| Contains:  <ul> <li>routing</li><li> login session management</li><li> validation</li><li> user filtering to create and edit catalog items</li><li> webserver</li><li> service</li><li> JSON API service</li><li>server configuration.</li>
**static folder**| Resources handling for Flask Framework | Contain website images, and style.css files.
**templates folder** | Resources handling for Flask Framework. |  HTML files with Flask information handling syntax.
**database_catalog_setup.py**| When runned, this file creates classes: User, Item, and Category that are populated by lotsofitems.py, and used in 'applicaiton.py' main file| Object Relational Mapper classes from SqlAlchemy. Is runned through the terminal with the command: 'python database_catalog_setup.py'
**lotsofitems.py**| Json formatted data to populate the datbase. | Data to populate the database in order to have dummy data presented when initially accessing the Catalog website. It contains 2 users, and also several Categories in the Catalog with several Items in each category.

---
### References

Udacity FSDN forums.
Ride BMX Wallpapers 2013
http://bikeandtrike.com/about/why-should-you-race-bmx-pg369.htm

## Future Development
- Integrate user picture on each item within categories.
- Integrate Google and Facebook Sign In buttons in a better user interface.
- Improve look and feel of website.
