# Copyright (C) 2019-2021 Estonian Information System Authority.
# See the file 'LICENSE' for copying permission.

import os

from cuckoo.common.storage import cuckoocwd

def make_nginx_base():
    return f"""# This is a basic NGINX configuration generated by Cuckoo. It is
# recommended to review it and change it where needed. This configuration
# is meant to be used together with the generated uWSGI configuration.
upstream _uwsgi_cuckoo_api {{
    server 127.0.0.1:9080;
}}

server {{
    listen 127.0.0.1:8090;

    # It is not recommended to cache paths, this can cause results to be
    # outdated/wrong.
    location / {{
        client_max_body_size 1G;
        proxy_redirect off;
        proxy_set_header X-Forwarded-Proto $scheme;
        include uwsgi_params;
        uwsgi_pass _uwsgi_cuckoo_api;
    }}
}}
"""

def make_uwsgi_base():
    import cuckoo.web
    from cuckoo.common.utils import getuser
    cfg = f"""; This is a basic uWSGI configuration generated by Cuckoo. It is
; recommended to review it and change it where needed. This configuration
; is meant to be used together with the generated NGINX configuration.
[uwsgi]
; To run this, the uwsgi-plugin-python3 system package must be installed or
; it must be run from a Python3 installation that has uwsgi installed.
plugins = python3,logfile
chdir = {cuckoo.web.__path__[0]}
wsgi-file = api/wsgi.py
; The socket for NGINX to talk to. This should not listen on other
; addresses than localhost.
socket = 127.0.0.1:9080

; Verify that the users below are not root users and can read/write to/from 
; the Cuckoo CWD and installation. The configuration generator simply enters
; the user generating the configuration.
uid = {getuser()}
gid = {getuser()}

need-app = true
master = true
env = CUCKOO_APP=api
env = CUCKOO_CWD={cuckoocwd.root}
env = CUCKOO_LOGLEVEL=debug

; Log uWSGI app and Cuckoo web logs to the following file. Change this to
; any path, but be sure the uid/gid user has write permissions to this path. 
logger = file:logfile=/tmp/cuckooapi-uwsgi.log"""

    if os.environ.get("VIRTUAL_ENV"):
        cfg += f"""

; The path of the Python 3 virtualenv Cuckoo is installed in.
virtualenv = {os.environ['VIRTUAL_ENV']}"""

    return cfg