# polymarker-webui

A web interface for polymarker.

---

## Build

To be able to build polymarker-webui you first need the build module installd:

```bash
pip install build
```

Then running make build in the root of the repo will produce a wheel file in the dist directory, which can be copied and installed.

```bash
make build
```

## Install

### polymarker

First we need to follow the instructions for installing [polymarker](https://github.com/Informatics-John-Innes-Centre/bio-polymarker).

### mariadb

The web interaface uses mariadb so we need to install that and create a user for the service to use. Here we assume that the mariadb repos have been setup.

```bash
sudo dnf install -y MariaDB MariaDB-devel
sudo systemctl enable mariadb
sudo systemctl start mariadb
sudo mariadb-secure-installation 
sudo mariadb -u root -p
```

```sql
CREATE USER polymarker;
GRANT ALL ON *.* TO 'polymarker';
```

### python

Make sure we have the python dev libs.

```bash
sudo dnf install -y python python3-devel
```

### nginx

We use nginx as our proxy, so install, configure and enable that.

```bash
sudo dnf install -y nginx
```

Edit /etc/nginx/nginx.conf to add:
```
location / {
  proxy_pass http://127.0.0.1:5000;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}

add_header Content-Security-Policy "frame-ancestors 'none';";

```

Then enable and start the service

```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
sudo systemctl enable nginx.service 
sudo systemctl start nginx.service 
```

### polymarker-webui

First we copy our systemd unit file on to our server so once things are installed we can run them:

```bash
sudo scp goz24vof@N119983:~/polymarker/src/polymarker-webui/etc/polymarker-webui.service /etc/systemd/system/
```

We create a user to run things and log in as this user:

```bash
sudo luseradd polymarker
sudo -i
su --login polymarker
```

As this user we create a virtual enviroment, copy across our polymarker-webui wheel file and install it:

```bash
python -m venv venv
source venv/bin/activate
scp goz24vof@N119983:~/polymarker/src/polymarker-webui/dist/pmwui-1.0.1-py2.py3-none-any.whl .
pip install pmwui-1.0.2-py2.py3-none-any.whl 
```

Finally we need to create a database for the app to use and 

```bash
mariadb
```

```sql
CREATE DATABASE polymarker_webui;
```

#### Configuration

Here we must take a brief interlude to quickly cover configuration.


```bash
mkdir -p venv/var/pmwui-instance/
vim venv/var/pmwui-instance/config.py 
```

```python
# Our standard Flask app secret key
SECRET_KEY='SOME SECRET KEY'

# A standard selection of Flask-Mail settings
MAIL_SERVER = 'OUR MAIL SERVER'
MAIL_PORT = 587 # This is probably the port we want
MAIL_USERNAME = 'OUR USERNAME'
MAIL_PASSWORD = 'OUR PASSWORD'
# Some more settings we probably want
MAIL_USE_TLS = True
MAIL_USE_SSL = False

# url for our sever (used for some links)
SERVER_NAME = 'polymarker.jic.ac.uk'

# name of our database
DATABASE_NAME='polymarker_webui'
```









```bash
flask --app pmwui init
```










scp -r goz24vof@N119983:~/polymarker/src/polymarker-webui/genome_descriptions .
scp -r goz24vof@N119983:/home/polymarker/data/genomes .


(venv) [polymarker@localhost ~]$ flask --app pmwui import genome_descriptions/chinese_spring_refseq_pseudomolecules-1.0.toml 
(venv) [polymarker@localhost ~]$ flask --app pmwui import genome_descriptions/svevo-2.toml 


flask --app pmwui import data/genome_descriptions/bol-1.0.toml 
flask --app pmwui import data/genome_descriptions/brapa-1.0.toml 
flask --app pmwui import data/genome_descriptions/cadenza-1.1.toml 


exit
exit



sudo systemctl enable polymarker-webui
sudo systemctl start polymarker-webui





flask --app pmwui gc 1
venv/var/pmwui-instance/uploads/
venv/var/pmwui-instance/results/
pip install --upgrade pmwui-1.0.1-py2.py3-none-any.whl 






## Add genomes

---


sudo journalctl -u polymarker-webui -f
