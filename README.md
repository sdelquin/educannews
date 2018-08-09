# `edu|can|news`

El objetivo de este proyecto es notificar las novedades que se van produciendo en la web de la **Consejería de Educación y Universidades** del Gobierno de Canarias.

Para ello se hará un *scrapping* de la url http://www.gobiernodecanarias.org/educacion/web/ en la que se publican periódicamente las novedades de la Consejería de Educación y Universidades.

Se utilizará el lenguaje de programación *Python* y, en un principio, las notificaciones se realizarán mediante un *bot de Telegram*.

## Usage

Clone this repo:

~~~console
$ git clone git@github.com:sdelquin/educannews.git
~~~

Create the *virtualenv* and install dependencies:

~~~console
$ pipenv install
~~~

Create the database:

~~~console
$ pipenv run python create_db.py
~~~
> `news.db` will appear in current directory

Set your own settings:

~~~console
$ vi .env
~~~

> Override the needed variables of `config.py`

Now you can launch the main script:

~~~console
$ pipenv run python main.py
~~~
