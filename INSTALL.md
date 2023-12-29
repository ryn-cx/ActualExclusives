python -m venv .venv

<!-- For mac -->

source .venv/bin/activate

<!-- For linux -->

source .venv/lib/activate

poetry install

source .venv/bin/virtualenvwrapper.sh

<!-- Assuming in subfolder named ActualExclusives root of project folder -->

add2virtualenv .



sudo apt update
sudo apt upgrade

curl -sSL https://repos.insights.digitalocean.com/install.sh | sudo bash


adduser ybr

usermod -aG sudo ybr

rsync --archive --chown=ybr:ybr ~/.ssh /home/ybr

sudo reboot

sudo apt install python3-pip python-is-python3 python3-venv unzip nginx python3-poetry

git clone https://github.com/ryn-cx/ActualExclusives.git

<!-- Manually add API key, downloaded_files, and db.sql -->

cd ActualExclusives

python -m venv .venv

source .venv/bin/activate

poetry install

source .venv/bin/virtualenvwrapper.sh

add2virtualenv ActualExclusives/

pip install gunicorn

cd ActualExclusives
gunicorn --bind 0.0.0.0:9021 wsgi




sudo nano /etc/systemd/system/gunicorn.socket

[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target


sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=ybr
Group=www-data
WorkingDirectory=/home/ybr/ActualExclusives
ExecStart=/home/ybr/ActualExclusives/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          ActualExclusives.wsgi:application

[Install]
WantedBy=multi-user.target



sudo nano /etc/nginx/sites-available/ActualExclusives

server {
    listen 80;
    server_name ActualExclusives.Com;

    access_log off;
    location = /favicon.ico { access_log off; log_not_found off; }
    location /static {
        alias /home/ybr/ActualExclusives/ActualExclusives/static;
    }
    location / {
        proxy_pass http://127.0.0.1:9021;
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Real-IP $remote_addr;
        add_header P3P 'CP="ALL DSP COR PSAa PSDa OUR NOR ONL UNI COM NAV"';
     }
}


server {
    listen 80;
    server_name ActualExclusives.Com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ybr/ActualExclusives/ActualExclusives/static;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
    }
}


sudo ln -s /etc/nginx/sites-available/ActualExclusives /etc/nginx/sites-enabled

sudo systemctl restart nginx


screen -S scraper

cd ~/ActualExclusives
source .venv/bin/activate
cd ActualExclusives/scrape
python platform_games.py
