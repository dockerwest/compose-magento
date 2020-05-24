Magento basic developer environment
====================================

Basic developer environment for Magento2 apps.

Usage
-----

For your convenience the developer environment has some helpers which take away
some difficulties you could experience using docker containers.

If you want this easy helpers to be readily available for you you can use
`environment` before you start. `environment` allows you to start your
environment with an updated `PATH` and allows you to choose between `tmux`,
`screen` or `byobu`. You can also define a default in the .env file. 

explicit setting the window manager:

~~~ sh
$ ./environment [tmux|screen|byobu]
~~~

using default window manager, defined in .env

~~~ sh
$ ./environment
~~~

When you are running in this environment all helpers are available in your path.

You are not required to use the environent, but then you have to call the
helpers with their full path.

To make use of the helpers you should use the `run` wrapper for `docker-compose`.

~~~ sh
$ run up
~~~

Configuration
-------------

There is a sample configuration `.env-sample` which contains the defaults used
in this environment.

If you want to change some of these values, copy `.env-sample` to `.env` and
start editing.

default `.env-sample`

~~~
C_UID=1000
C_GID=1000
PHPVERSION=7.1
NGINXVERSION=stable
MAGENTOVERSION=2
BASEHOST=magento2.dev
MYSQL_ROOT_PASSWORD=toor
APPLICATION=../magento2
DEVELOPMENT=1
WINDOW_MANAGER=tmux
~~~

### C_UID / C_GID

Configure what UID and GID your PHP container must use. This usually should
match your Hosts UID and GID. To find your local UID you can run `id -u` and to
find your local GID you can run `id -g`.

### PHPVERSION

Choose your PHP version. To see which versions are available
[here](https://github.com/dockerwest/php-magento2).

### NGINXVERSION

Choose what version of Nginx you want. To see which versions are available see
[here](https://github.com/dockerwest/nginx-magento2)

### MAGENTOVERSION

Choose the version of magento you are going to use. The nginx configuration is
slightly different between version 1 and version 2.

### BASEHOST

This setting defines what the hostname will be you can browse your magento2 app.
The example configuration will be give you `http://magento2.dev`.

### MYSQL_ROOT_PASSWORD

Choose whatever you want to use as default root password.

### APPLICATION

A relative or absolute path to your magento2 code. this can be a checkout of
  [magento2](https://github.com/magento/magento2).

### DEVELOPMENT

There is the `DEVELOPMENT` environment variable wich will enable xdebug,
composer and enable timestamp checking in opcache. 

When `DEVELOPMENT` is enabled xdebug should work out of the box. When you have
issues - like while running docker for mac - you can set the extra environment
variable `XDEBUG_CONFIG` with your hosts ip in it so xdebug can properly
connect back.

### APPLICATION_FILE_SYNC

Defines which method is to be used to sync files to the application container.

Supported values:
  * none (default): disables integrated scripts, allowing your own method 
   (or mount) to be set up over the `docker-compose.yml`
  * mutagen: highly recommended on Mac and Windows. See [https://mutagen.io/](https://mutagen.io/). Will also result in docker-compose-mutagen.yml being used upon compose.

### WINDOW_MANAGER
Set the default window manager when running the environment.
Available options are: tmux, screen and byobu

Helpers
-------

The helpers are written in python, so you should have python2 or python3
installed on your system to be able to use them. Most Linux distributions and
macOS have python already installed so there should be no issue there. There
are no extra dependencies on python modules.

### composer
Run the [composer](https://getcomposer.org/) command inside the php docker
container.  The working directory will be the current directory you are
executing this command from.  Your $HOME/.ssh and $HOME/.composer folders wil
be mounted inside this container to enable you to make use of your ssh keys and
composer cache.

eg. `$ composer require package_name`

### create_db

Create a new database inside the running mysql container with the name
'magento2' and 'DEFAULT CHARSET utf8'.

eg. `$ create_db magento2`

### mysql

Execute a mysql command inside the running mysql container as the root user.

eg. `$ mysql "SELECT * FROM table_name;"`

### mysqldump

Execute the mysqldump command inside the running mysql container as the root
user.

eg. `$ mysqldump db_name > export_file_name.sql`

### mysqlimport

Import a given mysql file into a given database, inside the running mysql
container as the root user.

eg. `$ mysqlimport db_name import_file_name.sql`

### node

Execute the [node](https://nodejs.org) command inside a node container.  The
working directory will be the current directory you are executing this command
from.

eg. `$ node js_file.js`

### npm

Execute the [npm](https://www.npmjs.com/) command inside a node container.  The
working directory will be the current directory you are executing this command
from.  Your $HOME/.ssh and $HOME/.npm folders wil be mounted inside this
container to enable you to make use of your ssh keys and npm cache.

eg. `$ npm install package_name`

### yarn

Execute the [yarn](https://yarnpkg.com) command inside a node container.  The
working directory will be the current directory you are executing this command
from.  Your $HOME/.ssh and $HOME/.npm folders wil be mounted inside this
container to enable you to make use of your ssh keys and npm cache.

eg. `$ yarn add package_name`

### php

Execute the php command inside the running php container, or inside a
php-pimcore container if none is running.  The working directory will be the
current directory you are executing this command from.

eg. `$ php -v`

### redis-cli

Execute the [redis-cli](https://redis.io/topics/rediscli) command in the
running redis container.

eg. `$ redis-cli flushall`

### run

Run docker-compose for the current project, setting the project name to the
BASEHOST variable from the .env file

eg. `$ run up`

### install-magento

This will run an installation using redis for caches and create a default admin
user. The admin user is `admin` and the password is `DockerWest123!`. The admin
endpoint will be found under `/admin`.

Tricks
------

### macOS

For this environment to work properly you should install gnu coreutils

using homebrew:

~~~ sh
$ brew install coreutils
~~~

On macOS you could just install docker from the docker site and run like this.
But our experience is that the native docker install is fairly slow to use. We
would suggest you to install [dinghy](https://github.com/codekitchen/dinghy).

[install dinghy](https://github.com/codekitchen/dinghy#install) and install the
VM technology you want to use. If you want native xhyve support you can
additionally install 
[xhyve driver for docker machine](https://github.com/zchee/docker-machine-driver-xhyve).

If you have dinghy installed this environment will try to use it.

Currently there is an annoying limitation when we are using dinghy and that is
that the hostnames used must end with `docker`.

#### tmux on macOS

Tmux starts the shells as loginshells, that means that for example bash is
going to load the `profile` files. This sort of behaviour triggers the
path_helper that will move our added PATH to the end. This is not the behaviour
we want.

To fix this you can change the if for the path helper in your `/etc/profile` to
the following:

~~~ sh
if [ -z $TMUX ] && [ -x /usr/libexec/path_helper ]; then
	eval `/usr/libexec/path_helper -s`
fi
~~~


### oh-my-zsh users

[oh-my-zsh](http://ohmyz.sh/) users should check if there is no fixed setting
for `$PATH` in their `~/.zshrc`. If that is the case you can safely comment it
out. If somewhere in your shell startup `$PATH` is forced you lose the features
the `./environment` script brings to you.

License
-------

MIT License (MIT). See [License File](LICENSE.md) for more information.
