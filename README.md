# URL-Shortening-API

![](https://img.shields.io/badge/Microverse-blueviolet)

# Project Name
Scissors or Snipe, yet to decide

> This is an API for a school portal, to manage student registration, student information, courses and grades.


## Summary of this API

> This is an API built with Flask RestX. This URL is a shortening API, makes long links short, creates custom links, provides QR code for short links, provides analytics for the short links created.

# IMPORTANT
> Change the config_dict in the `__init__.py` and the `runserver.py` file to production and set up your production database and other settings.
>
## Built With

- Major languages - `Python`
- Frameworks - `Flask`, `RestX`
- Technologies used - `SQLAlchemy`, `Sqlite3`

 
## To get a local copy up and running follow these simple example steps. 

In your cmd or git bash, enter  `git clone https://github.com/Veektaw/Url-Shortening-app.git` to clone this repository.

### Prerequisites
Must have `Python3.11` or newer, with pip installed.

### Setup
Clone this repo to your local directory, and open in your local intepreter.

### Install
Open your terminal in your interpreter, use `pip install -r requirements.txt` to install everything in the requirements.txt file. This repository does not come with a database, please install your own databse. When you install, the first user you register is `ADMIN` the rest are students. To install a database, use `export FLASK_APP=api` then enter `flask shell` then enter `db` press enter and use `db.create_all()`. Please go to the `__init__.py` file and change the config_dict to `dev`, then go to the runserver.py file and change the config_dict to `dev` to run this on your local server.

### Usage