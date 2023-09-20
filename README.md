![Lenguaje Python](https://img.shields.io/badge/Lenguaje-Python-green)
![Versión de Python 3.11](https://img.shields.io/badge/Versión%20de%20Python-3.11-green)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)


# App Gestión de Fondos de inversión
## Descripción
Aplicación que se encarga de comprobar, vía web _scraping_ o raspado web, el valor liquidativo de una serie de fondos que son leídos directamente de dos archivos CVS. Obviamente los cálculos los realiza sobre cada aportación y muestra un sumatorio de estas aportaciones.

La aplicación recupera una serie de datos como la rentabilidad, valores como Alpha y Beta y calcula otras variables como la:
- Rentabilidad de la inversión,
- El % de cada fondo en la bolsa de fondos o
- La distancia en días del máximo y del mínimo.

Muestra un resumen de la cesta de fondos de inversión activos para poder tomar las decisiones adecuadas.

También muestra el indice [Fear&Greed](https://edition.cnn.com/markets/fear-and-greed).

## Imagen de ejemplo
![Imagen de ejemplo](https://github.com/JavierPerezManzanaro/app_Fondos_de_Inversion/blob/08068762f5b60aa2ac221b6ff68fd6123d672bd4/Datos%20de%20ejemplo/Captura.png)

## Caraterísticas

### Obtención de datos del usuario
La aplicación lee dos archivos CVS que el usuario debe generar:

#### Listado de fondos-Fondos.csv
De aquí obtenemos los datos de gestión.
Hay varias columnas pero realmente las que importan para esta aplicación son las siguientes (empezando por la fila 0):
- ISBN: fila 4,
- Nombre del fondo: fila 0,
- Moneda: fila 6,
- URL del FT de donde recuperamos los datos del fondo: fila 5,
- Propietario del fondo (por si hay otros interviniente): fila 1.

#### Listado de movimientos-Movimientos.csv
Aquí se almacenan las operaciones que se realizan sobre los fondos.
La aportación (que puede ser negativa si es una retirada) esta pensada para ser usada con el sistema español: puntos "." para separar los miles y comas "," para los decimales. Esta información es transformada después a float.
Las columnas usadas son estas:
- ISBN: fila 0,
- Fecha de la operación: fila 3,
- Aportación en moneda local, (importe_local): fila 1,
- Participaciones de la operación: Fila 2.

Ambos archivos deben estar en una carpeta que se llama "Datos".
Los datos están así creados porque se generan automáticamente al exportar un documento en Numbres (aplicación tipo Excel para Mac).

### Web _scraping_
Esta app obtiene mediante web _scraping_ los siguientes datos de cada fondo de inversión:
- Cambio diario
- Valor
- Fecha
- Alpha
- Beta
- % de rentabilidad de los últimos 12 meses
Los datos son extraídos de la web del *Financial Times*. No he usado APIs porque desde esta web obtengo todos los datos necesarios. Por otra parte, no he encontrado ningún un servidor gratuito mediante APIs que muestre todos estos datos.

### Otra información mostrada
- TAE
No se si es el termino correcto. La idea es comparar distintas rentabilidades que tiene periodos distintos. Para hallar este dato he procedido de la siguiente manera:
1) Se halla el numero de días desde el inicio al día actual
2) El % de rentabilidad se divide entre el valor del punto anterior
3) El dato obtenido se multiplica por 365
- Porcentaje en la bolsa:
Indica el peso o valor de cada fondo en sobre el total del capital invertido.
- Mínimo y Máximo:
Indica el valor de perdida o de ganancia y el número de días transcurridos. Para obtener estos datos se parte del JSON. Si se crea un nuevo fondo hay que meter ese valor de forma manual.

### Concurrencia
Para aumentar la velocidad he implementado tecnología de concurrencia. El resultado ha sido muy satisfactorio. He creado 6 hilos (max_workers=6) pero la cifra puede variar según el procesador del equipo en el que se use. El resultado para 17 fondos:
- Un solo hilo tarda 37 seg
- Tres hilos tardan 13.9 seg y
- Y seis hilos tardan 5.9 seg

### Moneda
Todos los datos mostrados están en Euros. La conversión se realiza usando el módulo [CurrencyConverter](https://pypi.org/project/CurrencyConverter/).

### Informes
El último paso cuando se ejecuta la aplicación es exportar la tabla como TXT para su posterior consulta historica. Estos archivos son almacenados en una carpeta que se llama "Informes".


# Instrucciones de instalación
- Clonar el repositorio en local
- Tener instalado Python 3.11.
- Ejecutar: 'App Gestión de Fondos de inversión.py'


# Manifiesto de los archivos del repositorio
- README.md
  El archivo que estas leyendo
- App Gestión de Fondos de inversión.py
  Aplicación en Python principal
- Datos
  Hay que crear la carpeta "Datos". Esta carpeta  contiene los dos archivos CVS de donde se obtiene los datos de los fondos y las operaciones hechas:
  - Listado de fondos-Fondos.csv
  - Listado de movimientos-Movimientos.csv
  - Historial.json
    Archivo que almacena el valor y la fecha de la posición mas alta y mas baja desde que se creo este archivo JSON
- Informes
  Carpeta que almacena los informes diarios. Esta carpeta también hay que crearla "Informes".
- Datos de ejemplo:
  En esta carpeta estan los tres documentos necesarios para que la aplicación funcione. Hay que cambiar el nombre de la carpeta de "Datos de ejemplo" a "Datos".
  Los tres documentos son un ejemplo y se pueden usar para generar los nuevos.
  La imagen "Captura.png" muestra la aplicación con estos datos.


# Historial de versiones
## Funciones a implementar
Implementaciones futuras:
- Mostrar aviso si no se han analizado todos los fondos
- Crear los datos de json si el se incorpora un fondo
- Crear app diferente para crear y actualizar el JSON
- Implementar la posibilidad de distintos tipos de tablas: Para invertir, de control, etc
- Crear la requirements.txt

## Versiones desarrolladas

### 1.01
- Crear la columna 'TAE'
- Mejora en la documentación
- Correcciones menores

### 1
- Versión base


# Licencias y derechos de autor
CC (Creative Commons) de Reconocimiento – NoComercial – SinObraDerivada
![CC (Creative Commons) de Reconocimiento – NoComercial – SinObraDerivada](https://raw.githubusercontent.com/JavierPerezManzanaro/Maquetacion-de-masivos-responsive-html-con-noticias/main/Reconocimiento-no-comercial-sin-obra-derivada.png)


# Información de contacto del autor
Javier Pérez
javierperez@perasalvino.es


# Errores conocidos
- Si la conexión a internet es muy mala es mejor bajar el número de la concurrencia porque hay errores y no se llegan a ejecutar todos los procesos simultáneos. Tampoco avisa del error.


# Motivación
Es un trabajo muy laborioso ir fondo a fono actualizando los datos. De esta forma se actualiza toda la cartera en segundos.

# Créditos y agradecimientos
- A toda la comunidad web que me ha permitido ir ampliando mi formación.
- A mi familia por su infinita paciencia.
