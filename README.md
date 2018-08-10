# `edu|can|news`

El objetivo de este proyecto es notificar las novedades que se van produciendo en la web de la **Consejería de Educación y Universidades** del Gobierno de Canarias.

Para ello se hace un *scrapping* de la url http://www.gobiernodecanarias.org/educacion/web/ en la que se publican periódicamente las novedades de la Consejería de Educación y Universidades.

Se utiliza el lenguaje de programación *Python* y notificaciones mediante un *bot de Telegram*.

## Modo de uso

Para poder beneficiarse de este bot hay que **unirse al siguiente canal de Telegram**:

https://t.me/educannews

## Desarrolladores

Clonar el repositorio:

~~~console
$ git clone git@github.com:sdelquin/educannews.git
~~~

Crear el *entorno virtual* e instalar las dependencias:

~~~console
$ pipenv install
~~~

Crear la *base de datos*:

~~~console
$ pipenv run python create_db.py
~~~
> `news.db` will appear in current directory

Establecer configuraciones personales:

~~~console
$ vi .env
~~~

> Esto sobreescribirá variables del fichero `config.py`

### Bot

Para lanzar el bot:

~~~console
$ pipenv run python bot.py
~~~

### Notify

Para lanzar el notificador:

~~~console
$ pipenv run python notify.py
~~~
