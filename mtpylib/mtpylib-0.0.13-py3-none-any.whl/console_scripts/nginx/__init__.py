import sys
from mtlibs import process_helper

from dotenv import load_dotenv, find_dotenv

from mtlibs.docker_helper import isInContainer
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


def console_script_entry():
    print("命令行参数", sys.argv)
    print("本命令用于部署nginx")
    
    nginx_conf = """user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;


events {
  worker_connections 1024;
}


http {

  upstream smirror {
    server 127.0.0.1:3456 weight=100 max_fails=12 fail_timeout=60s;
  }
  upstream default_backend {
    server 127.0.0.1:3000 weight=100 max_fails=12 fail_timeout=60s;
  }

  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  log_format main '$remote_addr - $remote_user [$time_local] "$request" '
  '$status $body_bytes_sent "$http_referer" '
  '"$http_user_agent" "$http_x_forwarded_for"';

  access_log /var/log/nginx/access.log main;

  sendfile on;
  #tcp_nopush     on;

  keepalive_timeout 65;

  gzip on;
  types_hash_max_size 2048;

  include /etc/nginx/conf.d/*.conf;

  # #default site
  # server {
  #   sendfile on;
  #   tcp_nopush on;
  #   location / {
  #     root /app/static;
  #     index index.html index.htm;
  #   }
  #   # location / {
  #   #   add_header X-Powered-By 'PHP';
  #   #   root /app/static;
  #   #   try_files @sm $uri $uri/;
  #   #   proxy_pass http://sm;
  #   #   # autoindex on;
  #   #   index index.html index.htm;
  #   # }
  #   # location /api/sm {
  #   #   add_header X-Powered-By 'PHP';

  #   #   root /app/static;
  #   #   # try_files @nextfront $uri $uri/;
  #   #   proxy_pass http://sm;
  #   #   # autoindex on;
  #   #   index index.html index.htm;
  #   # }
  # }
}
"""
    print("nginx 配置信息", nginx_conf)
    
    if isInContainer():
        with open("/etc/nginx/nginx.conf", "w") as f:
            f.write(nginx_conf)
    else:
        print("本nginx 部署脚本仅在docker 容器内有效。")