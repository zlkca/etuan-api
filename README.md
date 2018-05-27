# ehetuan-api
ehetuan-api is a django backend for angular 5 website

## Requirement
python 3.6.2
django 2.0

## Set up with python3 virtual environment

### create virtual environment folder

Open a command line window, cd to rdshop-api folder, and create a py3 virtual environment folder:
```
> cd ehetuan-api
> python -m venv py3
```
If you have both python2.7 and python3.6 in your machine, use python3
```
> cd ehetuan-api
> python3 -m venv py3
```

### use virtual environment

When you are going to install python libraries, you need to activate virtual env first.

For Windows:

activate virtual env (Windows):
```
> cd rdshop-api
> py3/Scripts/activate.bat
```
Deactivate virtual env (Windows):
```
> py3/Scripts/deactivate.bat
```

For Linux/Mac:

activate virtual env (Linux/Mac):
```
> cd py3
> . py3/bin/activate
```

Deactivate virtual env (Linux/Mac):
```
> . py3/bin/deactivate
```

### Download and Install python plugins

Before this step make sure you have install the mysql mysql, connector and mysql-dev.

#### Install mysql:

For Linux:
```
> yum install mysql-server mysql-client mysql-dev
```
#### Install mysql python connector
Go to mysql official and download connector and install, you must install this connector before install mysqlclient

#### Install python plugins
```
> export PATH=$PATH:/usr/local/mysql/bin
> pip install -r requirements.txt
```
or 
```
> pip3 install -r requirements.txt
```
Note: If you cannot install mysqlclient with pip install, Install mysqlclient with python wheel file.
You should be able to google and find suitable wheel file.



### Create mysql datase

To create database, open mysql shell and issue command:
```
mysql -u <your mysql username> -p
```
```
mysql> CREATE DATABASE ehetuan CHARACTER SET utf8 COLLATE utf8_general_ci;
```

### Create mysql account 'mydbuser'/mypasswd:
```
mysql> CREATE USER 'mydbuser'@'localhost' IDENTIFIED BY 'mypasswd';
mysql> GRANT ALL PRIVILEGES ON * . * TO 'mydbuser'@'localhost';
mysql> FLUSH PRIVILEGES;
```

### Add a rdshop.config.json with your mysql credential
Create a .config.json file, change username and password of your mysql and place under the rdshop-api's parent folder with following content:
```
{
    "APP_DOMAIN":"127.0.0.1",
    "API_DOMAIN":"127.0.0.1",
    "API_PORT":8000,
    "ENV":"production",
	"DATABASE":{
		"NAME":"mydb",
		"USERNAME":"mydbuser",
		"PASSWORD":"mydbpass"
	},
	"SENDGRID":{
		"API_KEY":"my_api_key"
	}
}
```



### Migrate Django tables
```
> cd ehetuan-api
> python3 manage.py makemigrations account commerce
> python3 manage.py migrate
```

### Run srcipt to add cities and provinces
In mysql workbench run the scripts under sql-scripts/location.sql

### Create Django admin superuser 'admin'
```
> python3 manage.py createsuperuser --username admin
```

### Start
```
> cd rdshop-api
> python3 manage.py runserver
```

Open a browser, type http://localhost:8000/admin in address bar, and use admin credential you just created to login admin page.




