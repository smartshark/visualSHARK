About
=====
The visualSHARK is a graphical frontend for the MongoDB of the SmartSHARK project.
It consists of a Django based Backend and a VueJS based Frontend.
Some functionality relies on a worker process which executes background tasks and a Websocket connection.


What Works
==========

The basic views at the top (Commits, Issues, Files, Messages, People) should work with every instance of a SmartSHARK database.
The views under "manual labels" consist of manual data validation approaches used in some of our publications.
They will not fit every use case for manual data validation. 

Everything under "analytics" may or may not work as it contains a lot of views that were used for one time data exploration purposes.



Manual Validations
==================

Currently, there are 3 ways to manually validate data inside the SmartSHARK database via visualSHARK.
All validation views use the currently selected project.


Validations of Commit->Issue Links
----------------------------------
This validation is provided by the Commit->Issue view.
It relies on data from the linkSHARK which writes linked\_issue\_ids to every document of the commit collection which provides a link between issues and commits via a regex search of the commit message.

The view presents the user with a random sample of commits which contain a link. The user can then dismiss erroneous links by removing them from for every commit and then clicking submit.
This writes fixed\_issue\_ids to the commit document in the database which is shown as validated links in the commit view.


Validations of Issue Types
--------------------------
This validation requires that commit->issue links are validated as they are used in the sampling process.

It also requires the execution of a command (python manage.py create\_issue\_validation). The command *clears* the database of previous issue type validation data and creates new data from the SmartSHARK database. It pre-labels the issues by mapping of the issue type from the issue to a pre-defined list of possible types. This works best with Jira.

The view presents the user with the issue, linked commits, type of the issue and a list of possible types. The user can then assign one of the possible types and confirm via a checkbox that this is correct. After submission to the backend this data is persisted in the SmartSHARK database in the issue collection in issue\_type\_manual which contains a dict of the user that assigned the type as the key and the type as the value. If two different users achieve consensus the issue type is written in the issue\_type\_verified field in the issue collection. This is then shown in the issue view as verified type.

If no consensus on a type is reached the issue is listed in the Issue Type Conflicts view. There both users and possible a third as a referee can finally agree on a type, this information is then also persisted in the SmartSHARK database.
The issue document gets a 'committee' user in issue\_types\_manual dict with the type and issue\_type\_verified is set to the agreed upon type.


Validations of Bugfix lines
---------------------------

This validation requires validated commit->issue links and validated issue types.

It samples from issues with a verified type of bug and then collects all commits that are linked to this issue via validated links.
Each user has to perform some training issues first before being presented with the first issue from the sample.
After the training, the view presents the user with the issue, linked commits, and the source code of the files that were changed in that commit. The added and deleted lines are marked and the user has to label them as either bugfix, whitespace, test, documentation, refactoring or unrelated. The whitespace and documentation lines are pre-labeled via a heuristic. The refactoring lines are pre-labeled if refSHARK was previously executed. The user then has to manually label all lines that were changed in the commit.
The results are persisted into the SmartSHARK database under the respective hunks of the files that were changed.
The hunk documents receive a lines\_manual field which is a dict of the user as the key and the value is another dict with the label type being the key and the value is a list of line numbers of the hunk.


Requirements
============

Requirements and how to get them with Ubuntu 16.04 LTS.
RabbitMQ has to be running with activated web_stomp module.

Python 3.6
----------
```bash
add-apt-repository ppa:jonathonf/python-3.6
apt-get update
apt-get install python3.6
apt-get install python3.6-dev
apt-get install python3.6-venv
```

python-3.6 uwsgi module (only for production deployment)
--------------------------------------------------------
```bash
apt-get install python3.6 python3.6-dev uwsgi uwsgi-src uuid-dev libcap-dev libpcre3-dev libssl-dev
cd ~
PYTHON=python3.6 uwsgi --build-plugin "/usr/src/uwsgi/plugins/python python36"
mv python36_plugin.so /usr/lib/uwsgi/plugins/python36_plugin.so
chmod 644 /usr/lib/uwsgi/plugins/python36_plugin.so
```

pygraphviz
----------
```bash
apt-get install graphviz-dev
cd /srv/www/visualSHARK
source bin/activate
pip install pygraphviz --install-option="--include-path=/usr/include/graphviz" --install-option="--library-path=/usr/lib/graphviz/"
```

NPM
---
```bash
cd ~
curl -sL https://deb.nodesource.com/setup_8.x -o nodesource_setup.sh
nano nodesource_setup.sh
bash nodesource_setup.sh
apt-get install nodejs
```

RabbitMQ
--------
```bash
apt-get install rabbitmq-server
systemctl start rabbitmq-server
rabbitmq-plugins enable rabbitmq_web_stomp
rabbitmq-plugins enable rabbitmq_management
```


Installation
============

Install Backend
---------------

The backend assumes that a MySQL database is already existing for visualSHARK (can be empty).
If that is not the case create a database with your favorite tool before running migrate.

```bash
apt-get install libmysqlclient-dev
git clone https://github.com/smartshark/visualSHARK.git

cd /srv/www/visualSHARK
python3.6 -m venv .
source bin/activate
pip install -r requirements.txt

# change database credentials for MySQL DB and Mongo DB
# change secret key and, if ServerSHARK is available, URL to the endpoint and an api key.
cp sntest/settings_dist.py sntest/settings.py
nano sntest/settings.py

# migrate database
python manage.py migrate

# create superuser
python manage.py createsuperuser
```

Install Frontend
----------------

```bash
cd /srv/www/visualSHARK/frontend/app

# install dependencies
npm install

# install patch-package and apply patches for MonacoEditor
npm install patch-package
npx patch-package

# change local production settings, endpoints for RabbitMQ (websocket) and visualSHARK backend
# This is only necessary for a production environment, i.e., not running with npm run serve
cp env.production.local .env.production.local
nano .env.production.local

# run frontend in dev mode
# npm run serve

# build prod version
npm run build
```


Operation
=========

run backend in dev mode
```bash
cd /srv/www/visualSHARK
source bin/activate
python manage runserver
```

run backend worker
```bash
cd /srv/www/visualSHARK
source bin/activate
python manage peon
```

run frontend in dev mode
```bash
cd /srv/www/visualSHARK/frontend/app
npm run serve
```
