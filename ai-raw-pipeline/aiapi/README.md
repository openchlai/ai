# Parliament of Kenya

IP - 192.168.150.207
10.10.23.70
USER - jimmy
PASS - Orcus@123456#!

## SYSTEM OVERVIEW

OS: Ubuntu 24.04 LTS
Processor: 2-4 vCPUS
Memory: 4-8 GB RAM
Storage: 50-100 GB HDD

## Directory Structure
Assuming a user `bunge` with `$HOME` directory as `/home/bunge`
The Analytics Application `$COREAPP` will be deployed in `$HOME/coreapp`

# Basic Apps

```sh
sudo apt install tree python3-virtualenv python3-pip

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/home/jimmy/.local/bin/virtualenv
source /home/jimmy/.local/bin/virtualenvwrapper.sh

# Virtual Environment
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv
source /usr/local/bin/virtualenvwrapper.sh
export WORKON_HOME=$HOME/.virtualenvs
export PROJECT_HOME=$HOME/jimmy
source /usr/local/bin/virtualenvwrapper.sh

```

## NGINX Config
After installing `nginx` issue the following to check it's running and enable service for automatic start

```sh
sudo apt install nginx
sudo systemctl status nginx
sudo systemctl enable nginx
```

## Install MongoDB
The `$COREAPP` backend uses `MongoDB` as storage engine. It's a NoSQL type of database

curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg --dearmor

```sh
sudo apt install nginx
```

# Install PHP
This is required to run the `frontend`. The web interface will be located in `$HOME/bunge/www`.
The default folder is however `/var/html/www`. Whichever option make sure to configure `nginx`

## Install Node Version Manager (NVM)

## CONFIGURE VIRTUALENV
Create a `virtualenv` using `workon` from `virtualenvwrapper`

```sh
mkvirtualenv bunge
workon bunge
```

# Install Python Libraries
The reequired libraries are listed in the `requirements.txt` file found in `$COREAPP`

```sh
cd /home/bunge/coreapp
pip install -r requirements.txt 
```
Verify all libraries successfully installed and the application can execute

```sh
python run.py
```

## Application Start Script

Installed as `systemd` *service*

```bash
nano /etc/systemd/system/bunge.service
```

```bash
[Unit]
Description=Sentiment Analytics Services
After=multi-user.target

[Service]
Type=idle
User=bunge
WorkingDirectory=/home/jimmy/coreapp
ExecStart=/home/jimmy/.virtualenvs/senti/bin/python /home/jimmy/coreapp/run.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

nano senti.sh

```sh
#!/bin/bash
source /home/jimmy/dash/bin/python
cd /home/jimmy/coreapp
python run.py &
```

```sh
chmod +x senti.sh
```

crontab

```sh
@reboot /home/jimmy/coreapp/senti.sh
```

```bash
systemctl daemon-reload
systemctl start bunge.service
systemctl enable bunge.service
```

## Update & Upgrade

After completing above processes:
```sh
sudo apt update
sudo apt dist-upgrade
sudo reboot
```

# DASHBOARD LINKS
All requests must be `POST`

## View `Dashboard Metrics` = `/dashboard/stats/calcdash`
## View `Dashboard Reach` = `/dashboard/stats/calcreach`
## View `Frequent Sources` = `/dashboard/data/calcreach`
## View `Latest Mentions` Texts = `/dashboard/data/metadata`
## View `Service Users` = `/dashboard/data/usersdash`
## Create `Search Keywords` = `/dashboard/create/keywords`
## View `Search Keywords` = `/dashboard/data/keywords`


## STREAMLIT DASH
Embedded tool to monitor `data & tasks` pipelines and system
