# `edu|can|news`

El objetivo de este proyecto es notificar las novedades que se van produciendo en la web de la **Consejería de Educación y Universidades** del Gobierno de Canarias.

Para ello se hará un *scrapping* de la url http://www.gobiernodecanarias.org/educacion/web/ en la que se publican periódicamente las novedades de la Consejería de Educación y Universidades.

Se utilizará el lenguaje de programación *Python* y, en un principio, las notificaciones se realizarán mediante un *bot de Telegram*.

## Modo de uso

Para usar este bot hay que seguir los siguientes pasos:

1. Buscar el bot en Telegram por `educannews_bot`
2. Darle al botón **Iniciar** (es equivalente a utilizar el comando `/start`)
3. Registrarse para recibir notificaciones con el comando `/register`

Es posible que al principio no hayan notificaciones, pero desde que se publique alguna en la web de la *CEU* aparecerán en Telegram.

> En caso de querer dejar de recibir notificaciones basta con utilizar el comando `/unregister`

### Grupos, Canales y Supergrupos

El bot también se puede añadir a *grupos, canales y supergrupos* de Telegram. Hay que invitarlo utilizando la misma búsqueda de `educannews_bot`. Una vez dentro, basta con utilizar los comandos:
- Recibir notificaciones: `/register@educannews_bot`
- Dejar de recibir notificaciones: `/unregister@educannews_bot`

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
