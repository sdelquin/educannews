# `edu|can|news`

El objetivo de este proyecto es notificar las novedades que se van produciendo en la web de la **Consejería de Educación y Universidades** del Gobierno de Canarias.

Para ello se hace un _scrapping_ de la url http://www.gobiernodecanarias.org/educacion/web/ en la que se publican periódicamente las novedades de la Consejería de Educación y Universidades.

Se utiliza el lenguaje de programación _Python_ y notificaciones mediante un _bot de Telegram_.

## Modo de uso

Para poder beneficiarse de este bot hay que **unirse al siguiente canal de Telegram**:

https://t.me/educannews

## Desarrolladores

Clonar el repositorio:

```console
$ git clone git@github.com:sdelquin/educannews.git
```

Crear el _entorno virtual_ e instalar las dependencias:

```console
$ pip install requirements.txt
```

Crear la _base de datos_:

```console
$ python educannews.py createdb
```

> `news.db` will appear in current directory

Establecer configuraciones personales:

```console
$ vi .env
```

> Esto sobreescribirá variables del fichero `config.py`

### Notify

Para lanzar el notificador:

```console
$ python educannews.py notify -v
```
