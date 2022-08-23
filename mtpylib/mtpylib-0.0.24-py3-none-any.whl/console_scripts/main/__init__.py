from subprocess import CompletedProcess
import sys
from mtlibs import process_helper
from dotenv import load_dotenv, find_dotenv
from mtlibs.docker_helper import isInContainer
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# 入口
def console_script_entry():
    print("命令行参数", sys.argv)
    if not isInContainer():
        print("本部署脚本仅在docker 容器内有效")
    else:        
        start_django()
        start_nginx()
        
        start_wordpress()

        print("启动php-fpm")
        startup_phpfpm()

        # print("启动django 应用")
        # django_dev_cp = process_helper.exec("./manage.py runserver 0.0.0.0:8000 &")
        # if django_dev_cp.returncode == 0:
        #     print("django （开发板）启动成功")
        

        print("安装mtxlib")
        npm_install_mtxlib_cp = process_helper.exec("npm i -g mtxlib")
        if npm_install_mtxlib_cp.returncode == 0:
            print("安装mtxlib 安装")

        print("启动sm")
        sm_cp = process_helper.exec("sm")
        if sm_cp.returncode == 0:
            print("sm_cp 运行结果")


def startup_phpfpm():
    fpmconf = """;;;;;;;;;;;;;;;;;;;;;
  
; FPM Configuration ;
;;;;;;;;;;;;;;;;;;;;;

; All relative paths in this configuration file are relative to PHP's install
; prefix (/usr). This prefix can be dynamically changed by using the
; '-p' argument from the command line.

;;;;;;;;;;;;;;;;;;
; Global Options ;
;;;;;;;;;;;;;;;;;;

[global]
; Pid file
; Note: the default prefix is /var
; Default Value: none
; Warning: if you change the value here, you need to modify systemd
; service PIDFile= setting to match the value here.
pid = /run/php7.4-fpm.pid

; Error log file
; If it's set to "syslog", log is sent to syslogd instead of being written
; into a local file.
; Note: the default prefix is /var
; Default Value: log/php-fpm.log
error_log = /var/log/php7.4-fpm.log

; syslog_facility is used to specify what type of program is logging the
; message. This lets syslogd specify that messages from different facilities
; will be handled differently.
; See syslog(3) for possible values (ex daemon equiv LOG_DAEMON)
; Default Value: daemon
;syslog.facility = daemon

; syslog_ident is prepended to every message. If you have multiple FPM
; instances running on the same server, you can change the default value
; which must suit common needs.
; Default Value: php-fpm
;syslog.ident = php-fpm

; Log level
; Possible Values: alert, error, warning, notice, debug
; Default Value: notice
;log_level = notice

; Log limit on number of characters in the single line (log entry). If the
; line is over the limit, it is wrapped on multiple lines. The limit is for
; all logged characters including message prefix and suffix if present. However
; the new line character does not count into it as it is present only when
; logging to a file descriptor. It means the new line character is not present
; when logging to syslog.
; Default Value: 1024
;log_limit = 4096

; Log buffering specifies if the log line is buffered which means that the
; line is written in a single write operation. If the value is false, then the
; data is written directly into the file descriptor. It is an experimental
; option that can potentionaly improve logging performance and memory usage
; for some heavy logging scenarios. This option is ignored if logging to syslog
; as it has to be always buffered.
; Default value: yes
;log_buffering = no

; If this number of child processes exit with SIGSEGV or SIGBUS within the time
; interval set by emergency_restart_interval then FPM will restart. A value
; of '0' means 'Off'.
; Default Value: 0
;emergency_restart_threshold = 0

; Interval of time used by emergency_restart_interval to determine when
; a graceful restart will be initiated. This can be useful to work around
; accidental corruptions in an accelerator's shared memory.
; Available Units: s(econds), m(inutes), h(ours), or d(ays)
; Default Unit: seconds
; Default Value: 0
;emergency_restart_interval = 0

; Time limit for child processes to wait for a reaction on signals from master.
; Available units: s(econds), m(inutes), h(ours), or d(ays)
; Default Unit: seconds
; Default Value: 0
;process_control_timeout = 0

; The maximum number of processes FPM will fork. This has been designed to control
; the global number of processes when using dynamic PM within a lot of pools.
; Use it with caution.
; Note: A value of 0 indicates no limit
; Default Value: 0
; process.max = 128

; Specify the nice(2) priority to apply to the master process (only if set)
; The value can vary from -19 (highest priority) to 20 (lowest priority)
; Note: - It will only work if the FPM master process is launched as root
; - The pool process will inherit the master process priority
; unless specified otherwise
; Default Value: no set
; process.priority = -19

; Send FPM to background. Set to 'no' to keep FPM in foreground for debugging.
; Default Value: yes
;daemonize = yes

; Set open file descriptor rlimit for the master process.
; Default Value: system defined value
;rlimit_files = 1024

; Set max core size rlimit for the master process.
; Possible Values: 'unlimited' or an integer greater or equal to 0
; Default Value: system defined value
;rlimit_core = 0

; Specify the event mechanism FPM will use. The following is available:
; - select (any POSIX os)
; - poll (any POSIX os)
; - epoll (linux >= 2.5.44)
; - kqueue (FreeBSD >= 4.1, OpenBSD >= 2.9, NetBSD >= 2.0)
; - /dev/poll (Solaris >= 7)
; - port (Solaris >= 10)
; Default Value: not set (auto detection)
;events.mechanism = epoll

; When FPM is built with systemd integration, specify the interval,
; in seconds, between health report notification to systemd.
; Set to 0 to disable.
; Available Units: s(econds), m(inutes), h(ours)
; Default Unit: seconds
; Default value: 10
;systemd_interval = 10

;;;;;;;;;;;;;;;;;;;;
; Pool Definitions ;
;;;;;;;;;;;;;;;;;;;;

; Multiple pools of child processes may be started with different listening
; ports and different management options. The name of the pool will be
; used in logs and stats. There is no limitation on the number of pools which
; FPM can handle. Your system will tell you anyway :)

; Include one or more files. If glob(3) exists, it is used to include a bunch of
; files from a glob(3) pattern. This directive can be used everywhere in the
; file.
; Relative path can also be used. They will be prefixed by:
; - the global prefix if it's been set (-p argument)
; - /usr otherwise
include=/etc/php/7.4/fpm/pool.d/*.conf


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; custom begin
;;;;;;;;;;;;;;
listen = 127.0.0.1:9000
; Clear environment in FPM workers
; Prevents arbitrary environment variables from reaching FPM worker processes
; by clearing the environment in workers before env vars specified in this
; pool configuration are added.
; Setting to "no" will make all environment variables available to PHP code
; via getenv(), $_ENV and $_SERVER.
; Default Value: yes
clear_env = no
"""

    with open("/etc/php/7.4/fpm/php-fpm.conf", "w") as f:
        f.write(fpmconf)

    phpfpm_cp = process_helper.exec("/etc/init.d/php7.4-fpm restart")
    if phpfpm_cp.returncode == 0:
        print("phpfpm 启动成功")
    else:
        print("phpfpm 启动失败")


def start_wordpress():
    print("设置wordpress")
    wp_config = """<?php
/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during the installation.
 * You don't have to use the web site, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * This has been slightly modified (to read environment variables) for use in Docker.
 *
 * @link https://wordpress.org/support/article/editing-wp-config-php/
 *
 * @package WordPress
 */

// IMPORTANT: this file needs to stay in-sync with https://github.com/WordPress/WordPress/blob/master/wp-config-sample.php
// (it gets parsed by the upstream wizard in https://github.com/WordPress/WordPress/blob/f27cb65e1ef25d11b535695a660e7282b98eb742/wp-admin/setup-config.php#L356-L392)

// a helper function to lookup "env_FILE", "env", then fallback
if (!function_exists('getenv_docker')) {
	// https://github.com/docker-library/wordpress/issues/588 (WP-CLI will load this file 2x)
	function getenv_docker($env, $default) {
		if ($fileEnv = getenv($env . '_FILE')) {
			return rtrim(file_get_contents($fileEnv), "\r\n");
		}
		else if (($val = getenv($env)) !== false) {
			return $val;
		}
		else {
			return $default;
		}
	}
}

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', getenv_docker('WORDPRESS_DB_NAME', 'wordpress') );
/** Database username */
define( 'DB_USER', getenv_docker('WORDPRESS_DB_USER', 'example username') );

/** Database password */
define( 'DB_PASSWORD', getenv_docker('WORDPRESS_DB_PASSWORD', 'example password') );

/**
 * Docker image fallback values above are sourced from the official WordPress installation wizard:
 * https://github.com/WordPress/WordPress/blob/f9cc35ebad82753e9c86de322ea5c76a9001c7e2/wp-admin/setup-config.php#L216-L230
 * (However, using "example username" and "example password" in your database is strongly discouraged.  Please use strong, random credentials!)
 */

/** Database hostname */
define( 'DB_HOST', getenv_docker('WORDPRESS_DB_HOST', 'mysql') );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', getenv_docker('WORDPRESS_DB_CHARSET', 'utf8') );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', getenv_docker('WORDPRESS_DB_COLLATE', '') );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         getenv_docker('WORDPRESS_AUTH_KEY',         '036f69e6cac545dc67b76f90181a2a5ff3ac8539') );
define( 'SECURE_AUTH_KEY',  getenv_docker('WORDPRESS_SECURE_AUTH_KEY',  '6b2e93cec23dded77bc79eeb4a671dd5b25bb7f6') );
define( 'LOGGED_IN_KEY',    getenv_docker('WORDPRESS_LOGGED_IN_KEY',    '2411beaf33cb1107ac7952ede192850bdfc28c88') );
define( 'NONCE_KEY',        getenv_docker('WORDPRESS_NONCE_KEY',        '18ed695eb63ab0441588403328de9e6088fe3e8e') );
define( 'AUTH_SALT',        getenv_docker('WORDPRESS_AUTH_SALT',        'f06a3ad240a0da3b74e77751746e0504219d03fe') );
define( 'SECURE_AUTH_SALT', getenv_docker('WORDPRESS_SECURE_AUTH_SALT', '4460552c50dab518f39466fe0597091985e13731') );
define( 'LOGGED_IN_SALT',   getenv_docker('WORDPRESS_LOGGED_IN_SALT',   '38403cc0dd102a176f2717aec20951cd20c3b7c3') );
define( 'NONCE_SALT',       getenv_docker('WORDPRESS_NONCE_SALT',       '02a9c9a072b277a31bbcb648459c120a10f2894d') );
// (See also https://wordpress.stackexchange.com/a/152905/199287)

/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = getenv_docker('WORDPRESS_TABLE_PREFIX', 'wp_');

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 *
 * For information on other constants that can be used for debugging,
 * visit the documentation.
 *
 * @link https://wordpress.org/support/article/debugging-in-wordpress/
 */
define( 'WP_DEBUG', !!getenv_docker('WORDPRESS_DEBUG', '') );

/* Add any custom values between this line and the "stop editing" line. */

// If we're behind a proxy server and using HTTPS, we need to alert WordPress of that fact
// see also https://wordpress.org/support/article/administration-over-ssl/#using-a-reverse-proxy
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && strpos($_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false) {
	$_SERVER['HTTPS'] = 'on';
}
// (we include this by default because reverse proxying is extremely common in container environments)

if ($configExtra = getenv_docker('WORDPRESS_CONFIG_EXTRA', '')) {
	eval($configExtra);
}

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
	define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';
"""
    with open("/var/www/html/wp-config.php", "w") as f:
        f.write(wp_config)


def start_nginx():
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
    server 127.0.0.1:3000 weight=150 max_fails=12 fail_timeout=60s;
  }
  upstream mtx {
    server 127.0.0.1:8000 weight=200 max_fails=12 fail_timeout=60s;
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
}
"""
    # print("nginx 配置信息", nginx_conf)
    nginx_default_site = """
server {
  listen 80;
  server_name 127.0.0.1;
  #access_log  /var/log/nginx/host.access.log  main;
  # location / {
  #   root /app/static;
  #   index index.html index.htm;
  # }
  index index.php;
  # access_log /etc/nginx/conf.d/log/access.log;
  # error_log /etc/nginx/conf.d/log/error.log;
  # location / {
  #   add_header X-Powered-By 'PHP';
  #   root /var/www/html;
  #   index index.php index.html index.htm;
  #   # try_files @sm $uri $uri/;
  #   # try_files $uri /index.php?$args $uri/index.html $uri.html @default_backend;
  #   try_files $uri $uri/index.html $uri.html @default_backend;

  #   # # proxy_pass http://default_backend;
  #   # # autoindex on;
  #   # proxy_http_version 1.1;
  #   # index index.html index.htm;
  #   # proxy_set_header Upgrade $http_upgrade;
  #   # proxy_set_header Connection "Upgrade";
  #   # proxy_set_header Host $host;
  #   # proxy_set_header Host $host;
  #   # proxy_set_header X-Real-IP $remote_addr;
  #   # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  # }
  root /var/www/html;
  location / {
    autoindex on;
    index index.php index.html index.htm;
    try_files $uri $uri/ /index.php?$args @mtx default_backend;
    # try_files $uri $uri/ /index.php?$args;
    # proxy_pass http://mtx;
  }

  location ^~ /smirror {
    add_header X-Powered-By 'PHP';
    # root /app/static;
    # try_files @nextfront $uri $uri/;
    proxy_pass http://smirror; 
    # autoindex on;
    # index index.html index.htm;
  }

  location ^~ /mtxcms/ {
    add_header X-Powered-By 'PHP';
    # root /app/static;
    # try_files @nextfront $uri $uri/;
    proxy_pass http://default_backend;
    # autoindex on;
    # index index.html index.htm;
  }
  
  location ^~ /admin/ {
    add_header X-Powered-By 'PHP';
    # root /app/static;
    # try_files @nextfront $uri $uri/;
    proxy_pass http://mtx;
    # autoindex on;
    # index index.html index.htm;
  }

  error_page 500 502 503 504 /50x.html;
  location = /50x.html {
    root /usr/share/nginx/html;
  }

  location /baidu {
    try_files /baidu.html
    $uri $uri/index.html $uri.html
    @fallback1;
  }
  #跳转到百度页面
  location @fallback {
    # rewrite ^/(.*)$ http://www.baidu.com;
    proxy_pass http://smirror;
  }

  location @default_backend {
    proxy_pass http://default_backend;
  }
  location @mtx {
    proxy_pass http://mtx;
  }


  # deny access to .htaccess files, if Apache's document root
  # concurs with nginx's one
  location ~ /\.ht {
    deny all;
  }
  # proxy the PHP scripts to Apache listening on 127.0.0.1:80
  #
  #location ~ \.php$ {
  #    proxy_pass   http://127.0.0.1;
  #}

  # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
  #
  #location ~ \.php$ {
  #    root           html;
  #    fastcgi_pass   127.0.0.1:9000;
  #    fastcgi_index  index.php;
  #    fastcgi_param  SCRIPT_FILENAME  /scripts$fastcgi_script_name;
  #    include        fastcgi_params;
  #}
  location ~ \.php$ {
    root /var/www/html;
    # try_files $uri =404;
    fastcgi_pass 127.0.0.1:9000;
    # fastcgi_pass /run/php/php7.4-fpm.sock;
    # 设置nginx的默认首页文件(上面已经设置过了，可以删除)
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
  }
  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires max;
    log_not_found off;
  }
  # #ignored: “-” thing used or unknown variable in regex/rew
  # rewrite ^/([_0-9a-zA-Z-]+/)?wp-admin$ /$1wp-admin/ permanent;

  # if (-f $request_filename) {
  #   set $rule_2 1;
  # }
  # if (-d $request_filename) {
  #   set $rule_2 1;
  # }
  # if ($rule_2 = "1") {
  #   #ignored: “-” thing used or unknown variable in regex/rew
  # }
  # rewrite ^/([_0-9a-zA-Z-]+/)?(wp-(content|admin|includes).*) /$2 last;
  # rewrite ^/([_0-9a-zA-Z-]+/)?(.*.php)$ /$2 last;
  # rewrite /. /index.php last;

  # deny access to .htaccess files, if Apache's document root
  # concurs with nginx's one
  #
  location ~ /\.ht {
    deny all;
  }
  location ~* \.(xml|yaml|cmd|cfg|yml|tmp|sh|bat|txt|ts|tsx|jsx|lock)$ {
    # 禁用某些后缀名文件访问。
    deny all;
  }
  location ~ (README\.md|ockerfile.*|package.*\.json|.*config.js|.*prisma.*)$ {
    deny all;
  }
  location ^~ /(configs|build|log|logs)/ {
    #禁用某些目录访问
    deny all;
  }
  location ^~ /. {
    # 禁止以.开始的文件访问
    # 匹配任何以 /. 开头的地址，匹配符合以后，停止往下搜索正则，采用这一条。
    deny all;
  }

  location = /some2.html {
    rewrite ^/some2.html$ /test/2.html break;
  }
}


"""
    with open("/etc/nginx/nginx.conf", "w") as f:
        f.write(nginx_conf)

    with open("/etc/nginx/conf.d/default.conf", "w") as f:
        f.write(nginx_default_site)
        
    cp: CompletedProcess = process_helper.exec("nginx -t")
    if cp.returncode != 0:
        print("nginx 配置信息不正确")
        print(cp.stderr + cp.stdout)
        return
    print("启动nginx")
    nginx_cp = process_helper.exec("nginx")
    if nginx_cp.returncode == 0:
        print("nginx 成功启动")

def start_django():
    print("以gunicorn的方式启动django")
    cmd="""gunicorn mtxcms.wsgi --bind=0.0.0.0:8000 --daemon"""
    cp: CompletedProcess = process_helper.exec(cmd)
    if cp.returncode == 0:
        print("gunicorn 成功启动")
    else:
        print("gunicorn启动失败")