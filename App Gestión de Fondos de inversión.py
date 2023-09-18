# App Gestión de Fondos de inversión
# entorno: source 'venv_fondos/bin/activate'

#!      CUIDADO
#todo   Por hacer
#?      Aviso
#*      Explicación


from pprint import pprint
import csv
from currency_converter import CurrencyConverter
# https://pypi.org/project/CurrencyConverter/
import json
import logging
from tabulate import tabulate
# https://pypi.org/project/tabulate/
from datetime import datetime
from gazpacho import get, Soup
# https://pypi.org/project/gazpacho/
import os
import time
import concurrent.futures
import fear_and_greed
# https://pypi.org/project/fear-and-greed/
import locale
locale.setlocale(locale.LC_ALL, 'es_ES')
cambio = CurrencyConverter()




# * Configuración de logging
logging.basicConfig(level=logging.WARNING,
                    format='-%(levelname)-8s [Línea: %(lineno)-4s Función: %(funcName)-18s] %(message)s')
# logging.debug('Mensaje de traza')
# logging.info('Mensaje Informativo, algo funcióna como se espera')
# logging.warning('Peligro')
# logging.error('Error')


# * Funciones

def lectura_datos_fondos() -> list:
    """Lee los datos del archivo de CVS exportado por Numbers

    Returns:
        list: Lista de los fondos
    """
    archivo = 'Datos/Listado de fondos-Fondos.csv'
    with open(archivo, newline='') as archivo:
        lector_csv = csv.reader(archivo, delimiter=';', quotechar='"')
        fila_numero = 1
        next(lector_csv) # nos saltamos la cabecera
        for fila in lector_csv:
            logging.debug(f'Leyendo fila de "Fondos": {fila_numero}')
            fondos.append({ 'isbn': fila[4],
                            'fila_numbers': fila_numero,
                            'nombre': fila[0],
                            'moneda': fila[6],
                            'url': fila[5],
                            'propietario': fila[1],})
            fila_numero +=1
        print(f'Se han leido {len(fondos)} fondos')
    return fondos


def lectura_datos_movimientos() -> list:
    """Lee los datos referidos a los movimientos del archivo de CVS exportado por Numbers

    Returns:
        list: Lista con todos los mvomientos que han expimentado los fondos
    """
    archivo = 'Datos/Listado de movimientos-Movimientos.csv'
    with open(archivo, newline='') as archivo:
        lector_csv = csv.reader(archivo, delimiter=';', quotechar='"')
        fila_numero = 1
        next(lector_csv) # nos saltamos la cabecera
        for fila in lector_csv:
            logging.debug(f'Leyendo fila de "Movimientos": {fila_numero}')
            importe_local = fila[1].replace('.', '')
            importe_local = importe_local.replace(',', '.')
            importe_local = float(importe_local)
            participaciones = fila[2].replace('.', '')
            participaciones = participaciones.replace(',', '.')
            participaciones = float(participaciones)
            movimientos.append({    'isbn': fila[0],
                                    'fecha': fila[3].format('YYYY-MM-DD'),
                                    'importe_local': importe_local,
                                    'importe_euros': None,
                                    'participaciones': participaciones,
                                    'fila_numbers': fila_numero,})
            fila_numero +=1
        print(f'Se han leido {len(movimientos)} movimientos')
    return movimientos


def raspado(fondo: dict) -> list:
    """Entra en cada URL del FT de cada fondo para proceder a la extracción de información

    Args:
        fondo (dict): Fondo al que quiere acceder

    Returns:
        fondos_mod -> list: Añade a la lista de fondos_mod el fondo actualizado
    """
    valor = 0
    anual = 0
    cambio_diario = 0
    fecha = None
    try:
        html = get(fondo['url'])
        gazpacho_soup = Soup(html) # type: ignore
        valor = gazpacho_soup.find('span', attrs={'class': 'mod-ui-data-list__value'})[0].text  # type: ignore
        valor = valor.replace(",", "")
        valor = float(valor)
        cambio_diario = gazpacho_soup.find('span', attrs={'class': 'mod-ui-data-list__value'})[1].text # type: ignore
        anual = gazpacho_soup.find('span', attrs={'class': 'mod-ui-data-list__value'})[2].text  # type: ignore
        anual = anual.replace("%", "")
        if anual == '--':
            anual = '0'
        anual = float(anual)
        dia = gazpacho_soup.find('div', attrs={'class': 'mod-disclaimer'})[0].text  # type: ignore
        fecha_texto = dia.split()
        mes = str(fecha_texto)
        match fecha_texto[8]:
            case 'Jan':
                    mes = '1'
            case 'Feb':
                    mes = '2'
            case 'Mar':
                    mes = '3'
            case 'Apr':
                    mes = '4'
            case 'May':
                    mes = '5'
            case 'Jun':
                    mes = '6'
            case 'Jul':
                    mes = '7'
            case 'Aug':
                    mes = '8'
            case 'Sep':
                    mes = '9'
            case 'Oct':
                    mes = '10'
            case 'Nov':
                    mes = '11'
            case 'Dec':
                    mes = '12'
        fecha = fecha_texto[9] + "/" + mes + "/" + fecha_texto[10][0:4]
        fecha = datetime.strptime(fecha, '%d/%m/%Y')
        alpha = gazpacho_soup.find('td')[1].text # type: ignore
        alpha = float(alpha)
        beta = gazpacho_soup.find('td')[4].text # type: ignore
        beta = float(beta)
    except TypeError:  # TypeError: 'NoneType' object is not subscriptable
        #logging.warning(f"Error a la hora de la extracción de datos: TypeError para: {fondo['nombre']}")
        alpha = 0
        beta = 0
    except:
        #logging.warning(f"Error a la hora de la extracción de datos para: {fondo['nombre']}")
        alpha = 0
        beta = 0
    finally:
        fondos_mod.append({     'isbn': fondo['isbn'],
                                'fila_numbers': fondo['fila_numbers'],
                                'nombre': fondo['nombre'],
                                'moneda': fondo['moneda'],
                                'url': fondo['url'],
                                'propietario': fondo['propietario'],
                                'valor': valor,
                                'cambio_diario': cambio_diario,
                                'anual': anual,
                                'fecha': fecha.strftime('%d/%m/%y'), # type: ignore
                                'alpha': alpha,
                                'beta': beta,       } )
    return fondos_mod


def obtención_datos(fondos: list) -> list:
    """Realizar el raspado de todos los fondos

    Returns:
        fondos_mod -> list: La lista de los fondos actualizada
    """
    fondos_mod = []
    for fondo in fondos:
        logging.info(f'Raspando: {fondo["nombre"]}')
        fondos_mod = raspado(fondo)
    fondos = []
    return fondos_mod


def paso_a_EUR(moneda: str, cantidad: float) -> float:
    """Convertimos cualquier moneda a EUR

    Args:
        moneda (str): moneda
        cantidad (float): cantidad a convertir

    Returns:
        float: cantidad convertida
    """
    if moneda == "USD":
        cantidad = cambio.convert(cantidad, 'USD', 'EUR')
    else:
        logging.warning(f'❌ Moneda: {moneda} no convertida')
        cantidad = 0
    return cantidad


def crear_tabla_json(tabla_completa: list, total_saldo: float):
    """Creación del json para resetear contadores de Máximo y de Mínimo

    Args:
        tabla_completa (list): _description_
        total_saldo (float): _description_
    """
    esquema_json = {}
    for fondo in tabla_completa[1:]:
        esquema_json[fondo['isbn']] = []
        esquema_json[fondo['isbn']].append({
                'max_fecha': fondo['fecha'],
                'max_valor': fondo['valor'],
                'min_fecha': fondo['fecha'],
                'min_valor': fondo['valor']})
        esquema_json['total'] = []
        esquema_json['total'].append({
                'total_fecha': fondo['fecha'],
                'total_valor': total_saldo})
    with open('Datos/Historial.json', 'w') as file:
        json.dump(esquema_json, file, indent=4)


def importacion_json() -> dict:
    with open('Datos/Historial.json', 'r') as archivo:
        datos_json = json.load(archivo)
    return datos_json


def exportar_json(datos_json):
    datos_json['total'] = []
    datos_json['total'].append({
        'total_fecha': fondo['fecha'],
        'total_valor': total_saldo})
    with open('Datos/Historial.json', 'w') as archivo:
        json.dump(datos_json, archivo, indent=4)


def fondo_en_bolsa(saldo_actual_EUR: float, total_saldo: float) -> float:
    """Calculamos el % de cada fondo en la bolsa de fondos

    Args:
        saldo_actual_EUR (float): El saldo de ese fondo
        total_saldo (float): El saldo total

    Returns:
        total_saldo_por -> float: Porcetaje de cada fondo en la bolsa
    """
    total_saldo_por = saldo_actual_EUR * 100 / total_saldo
    return total_saldo_por


def completar_tabla(tabla_completa: list, total_saldo: float, datos_json: dict) -> list:
    """Completa la tabla con los valores que no se han recogido antes o que son dependientes

    Args:
        tabla_completa (list): _description_
        total_saldo (float): _description_
        datos_json (dict):

    Returns:
        list: _description_
    """
    rentabilidad_acumulada = 0
    aportaciones_acumuladas = 0
    for fondo in tabla_completa[1:]:
        fondo['isbn_4cifras'] = clickable(fondo['isbn_4cifras'], fondo['url'])
        fondo['total_saldo_por'] = fondo_en_bolsa(fondo['saldo_actual_EUR'], total_saldo)
        # * Calculamos los límites máximos y mínimos
        fondo['maximo'] = maximo(datos_json, fondo)
        fondo['minimo'] = minimo(datos_json, fondo)
        rentabilidad_acumulada = rentabilidad_acumulada + fondo['rentabilidad_euros']
        aportaciones_acumuladas = aportaciones_acumuladas + fondo['aportaciones']
    #todo añadir un SEPARATING_LINE,
    return tabla_completa, rentabilidad_acumulada, aportaciones_acumuladas # type: ignore


def clickable(text: str, target: str) -> str:
    """Crea un texto enlazado en el terminal

    Args:
        text (str): texto del enlace
        target (str): URL de destino

    Returns:
        str: texto con enlace
    """
    return f"\x1b]8;;{target}\x1b\\{text}\x1b]8;;\x1b\\"


def orden(criterio: str, tabla_completa) -> list:
    """Función que cambia el orden de las filas de la tabla

    Args:
        criterio (str): columna por la que debemos ordenar
        tabla_completa (lista de diccionarios): tabla con todos los datos

    Returns:
        (lista de diccioanrios): tabla_general (la que se va a mostar) ordenada
    """
    cabecera = tabla_completa.pop(0)
    tabla_completa = sorted(
        tabla_completa, key=lambda k: k[criterio])
    tabla_completa.insert(0, cabecera)
    return tabla_completa


def mostrar_tabla(tipo_de_tabla: str, tabla_completa: list):
    """Generamos el tipo de tabla con el módulo tabulate. Podemos crear los modelos necesarios mostrando o no las columnas de la tabla

    Args:
        tipo_de_tabla (str): Hay varios tipo de tabla:
            rentabilidad:
            control: para el control de la aportaciones
        tabla_completa (list): Lista de datos a mostrar
    """
    tabla_general = []
    for fila in tabla_completa:
        #todo hacer un case para los dintintos tipos de tablas
        if tipo_de_tabla == 'rentabilidad':
            tabla_general.append([  fila['nombre'],
                                    fila['isbn_4cifras'], fila['moneda'],
                                    fila['cambio_diario'], fila['valor'], fila['fecha'],
                                    fila['saldo_actual_EUR'], fila['rentabilidad_euros'], fila['rentabilidad_porc'],
                                    fila['alpha'], fila['beta'], fila['anual'],
                                    fila['total_saldo_por'],
                                    fila['minimo'], fila['maximo'], ])
    return tabulate(tabla_general, headers="firstrow", tablefmt="rst",
            floatfmt=("", "", "", "", '_.2f', '', '_.2f', '_.2f', '_.1f', '', '', '', '.1f'),)
        # elif tipo_de_tabla == 'control':
        #     tabla_general.append([  fila['nombre'],
        #                             fila['isbn_4cifras'],
        #                             fila['cambio_diario'],
        #                             fila['saldo_actual_EUR'],
        #                             fila['aportaciones'], fila['participaciones_actual'],
        #                             fila['total_saldo_por']],)
        #     return tabulate(tabla_general, headers="firstrow", tablefmt="rst",)


def sentimiento_del_mercado() -> str:
    """Recoge y trata el Sentimiendo del Mercado. Mas infomación en: https://www.rankia.com/blog/bolsa-desde-cero/3806535-que-indice-fear-greed-compone-como-interpretarlo

    Returns:
        str: texto con valor a mostrar
    """
    try:
        valor = str(fear_and_greed.get())
        comienzo = valor.find("=")
        fin = valor.find(",")
        valor = float(valor[comienzo+1:fin])
    except:
        logging.warning(f'Hay un error a la hora de extraer el valor fear-and-greed: {fear_and_greed.get()}')
        valor = 0
        print()
    respuesta = ''
    if valor >= 1 and valor <= 24:
        respuesta = f"El indice {clickable('Fear&Greed', 'https://edition.cnn.com/markets/fear-and-greed')} esta en: {valor:.1f} Miedo extremo (0 a 24)"
    elif valor >= 25 and valor <= 49:
        respuesta = f"El indice {clickable('Fear&Greed', 'https://edition.cnn.com/markets/fear-and-greed')} esta en: {valor:.1f} Miedo (25-49)"
    elif valor >= 50 and valor <= 74:
        respuesta = f"El indice {clickable('Fear&Greed', 'https://edition.cnn.com/markets/fear-and-greed')} esta en: {valor:.1f} Optimismo (50-74)"
    elif valor >= 75 and valor <= 100:
        respuesta = f"El indice {clickable('Fear&Greed', 'https://edition.cnn.com/markets/fear-and-greed')} esta en: {valor:.1f} Optimismo extremo (75-100)"
    else:
        print(f"Valor {clickable('Fear andG reed', 'https://edition.cnn.com/markets/fear-and-greed')} esta fuera de rango")
    return respuesta


def maximo(datos_json: dict, fondo: list):
    """Calcula el máximo para mostar en la tabla

    Args:
        datos_json (dict): json con el dato de max y min
        fondo (list): Tabla con todos los datos

    Returns:
        _type_: un print
    """
    #todo ¿que pasa si no se encuentra, hay que crearlo el json. poner un try
    isbn = fondo['isbn'] # type: ignore
    if datos_json[isbn][0]['max_valor'] <= fondo['valor']: # type: ignore
        datos_json[isbn][0]['max_valor'] = fondo['valor']
        datos_json[isbn][0]['max_fecha'] = fondo['fecha']
        return 'En max'
    else:
        return else_en_maximo_y_minimo(datos_json, fondo, 'max')


def minimo(datos_json: dict, fondo: list):
    """Calcula el mínimo para mostar en la tabla

    Args:
        datos_json (dict): json con el dato de max y min
        fondo (list): Tabla con todos los datos

    Returns:
        _type_: un print
    """
    isbn = fondo['isbn'] # type: ignore
    if datos_json[isbn][0]['min_valor'] >= fondo['valor']: # type: ignore
        datos_json[isbn][0]['min_valor'] = fondo['valor'] # type: ignore
        datos_json[isbn][0]['min_fecha'] = fondo['fecha'] # type: ignore
        return 'En min'
    else:
        return else_en_maximo_y_minimo(datos_json, fondo, 'min')


def else_en_maximo_y_minimo(datos_json: dict, fondo: list, tipo: str):
    """Cálcula el máximo y el mínimo y la diferencia de las fechas

    Args:
        datos_json (dict): json con el dato de max y min
        fondo (list): Tabla con todos los datos
        tipo (str): Tipo de dato: máximo o mínimo

    Returns:
        _type_: un print
    """
    isbn = fondo['isbn'] # type: ignore
    if tipo == 'max':
        cadena_fecha = 'max_fecha'
        cadena_valor = 'max_valor'
    else:
        cadena_fecha = 'min_fecha'
        cadena_valor = 'min_valor'
    periodo = datetime.strptime(fondo['fecha'], '%d/%m/%y') - datetime.strptime(datos_json[isbn][0][cadena_fecha], '%d/%m/%y') 
    periodo = str(periodo)
    periodo = periodo.split()
    periodo = '0' if periodo[0] == '0:00:00' else periodo[0]
    diferencia = round((fondo['valor']* 100) / datos_json[isbn][0][cadena_valor], 1) # type: ignore
    diferencia = round(diferencia - 100, 1)
    return f'{diferencia}% hace {periodo} días'


def informe():
    """Generamos un archivo resumen del tipo TXT que se guarda en la carpeta Informes
    """
    hoy = datetime.now()
    mes = hoy.month if hoy.month >= 10 else str('0')+str(hoy.month)
    archivo = f'{hoy.year}-{mes}-{hoy.day}.txt'
    with open('Informes/'+archivo, 'w', encoding='utf-8') as archivo:
        #? otra foma de hacerlo: print(tabulate(mostrar_tabla('rentabilidad', tabla_completa)), file=archivo)
        archivo.write(mostrar_tabla('rentabilidad', tabla_completa))
        archivo.write('\n')
        archivo.write(f'Saldo total: {total_saldo:_.2f} €. Saldo invertido {aportaciones_acumuladas:_.2f} €, con una rentabilidad de {rentabilidad_acumulada:_.2f}, el {rentabilidad_acumulada_porc}%')
        archivo.write('\n')
        archivo.write(sentimiento_del_mercado_respuesta)


if __name__ == '__main__':
    os.system('clear')
    print('-'*49)
    print('Aplicación para la gestión de Fondos de Inversión')
    print('-'*49)
    print()
    fondos = []
    fondos_mod = []
    movimientos = []
    tabla_completa = [{ 'nombre': 'Nombre',
                    'isbn': 'ISBN',
                    'isbn_4cifras': 'ISBN\nURL',
                    'fila_numbers': 'fila\nnumbers',
                    'moneda': '',
                    'url': 'URL',
                    'propietario': 'Propietario',
                    'valor': 'Valor\nhoy',
                    'cambio_diario': 'Cambio diario',
                    'anual': 'Anual\n%',
                    'fecha': 'Fecha',
                    'alpha': 'Alpha',
                    'beta': 'Beta',
                    'saldo_actual_EUR': 'Saldo\nactual',
                    'participaciones_actual': 'Participaciones\nactual',
                    'rentabilidad_euros': 'Rentab.\neuros',
                    'aportaciones': 'Aportaciones\nen euros',
                    'rentabilidad_porc': 'Rentab.\n%',
                    'total_saldo_por': 'Porcentaje\nen la bolsa',
                    'maximo' : 'Máximo',
                    'minimo': 'Mínimo',
                    }]

    # * Carga de datos
    fondos = lectura_datos_fondos()
    movimientos = lectura_datos_movimientos()

    # * Obtención de datos de la web mediante raspado
    # * En un solo hilo tarda # 37 seg
        # inicio = time.time()
        # fondos_mod = []
        # fondos_mod = obtencion_datos(fondos)
        # fin = time.time()
        # print(f'Tiempo de ejecución en un solo hilo: {fin-inicio}')
    # * En tres hilos tarda # 13.9 seg
    # * En seis hilos tarda # 5.9 seg
    inicio = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        functiones_en_hilos = {}
        for i in range(len(fondos)):
            value = f'fondo {i}'
            functiones_en_hilos[executor.submit(raspado, fondos[i])] = value
        for future in concurrent.futures.as_completed(functiones_en_hilos):
            etiqueta = functiones_en_hilos[future]
    fin = time.time()
    print(f'Tiempo de ejecución en raspado: {fin-inicio} segundos')

    # * Seleción de movimientos por fondo y trabajo con sus datos
    logging.info(f'Seleción de movimientos por fondo y trabajo con sus datos')
    # * Variables para totales
    total_porcentaje = 0
    total_saldo = 0

    """  Tenemos dos listas con diccionarios en su interior
    fondo: alpha, anual, beta, cambio_diario, fecha, fila_numbers, isbn, moneda,
        nombre, propietario, url, valor
    movimiento: fecha, fila_numbers, importe_euros, importe_local, isbn, participaciones
    """

    for fondo in fondos_mod:
        logging.info(f'Analizando el fondo: {fondo["nombre"]} con ISBN: {fondo["isbn"]}')
        # * Variables para fondos
        movimientos_filtrados = []
        saldo = 0
        aportaciones = 0
        saldo_actual = 0
        participaciones_actual = 0
        importe_local = 0
        rentabilidad_fondo_global = 0
        porcentaje_en_cesta = 0
        lista_para_tabla = []

        criterio = lambda movimiento: movimiento["isbn"] == fondo['isbn']
        movimientos_filtrados = list(filter(criterio, movimientos))

        for movimiento in movimientos_filtrados:
            # * Trabajamos cada movimiento por separado
            # * Suma participaciones de todo el fondo para revisión
            # * Valoración actual
            aportaciones = aportaciones + int(movimiento['importe_local'])
            saldo = fondo['valor'] * movimiento['participaciones']
            saldo_actual = saldo_actual + saldo
            participaciones_actual = participaciones_actual + movimiento['participaciones']
        # * Caculo de rentabilidades
        rentabilidad = saldo_actual - aportaciones
        rentabilidad_porc = rentabilidad / aportaciones * 100
        total_saldo = total_saldo + saldo_actual
        # * Pasamos la monedas extanjeras a EUROS
        if fondo['moneda'] != 'EUR':
            fondo['valor'] = paso_a_EUR(fondo['moneda'], fondo['valor'])
            fondo['saldo_actual_EUR'] = paso_a_EUR(fondo['moneda'], saldo_actual)
            fondo['rentabilidad_euros'] = paso_a_EUR(fondo['moneda'], rentabilidad)
        # * Creación de filas de datos de tabla_completa
        tabla_completa.append({ 'nombre': fondo['nombre'][0:25],
                                'isbn': fondo['isbn'],
                                'isbn_4cifras': fondo['isbn'][8:12],
                                'fila_numbers': fondo['fila_numbers'],
                                'moneda': fondo['moneda'],
                                'url': fondo['url'],
                                'propietario': fondo['propietario'],
                                'valor': fondo['valor'],
                                'cambio_diario': fondo['cambio_diario'],
                                'anual': fondo['anual'],
                                'fecha': fondo['fecha'],
                                'alpha': fondo['alpha'],
                                'beta': fondo['beta'],
                                'saldo_actual_EUR': saldo_actual,
                                'participaciones_actual': participaciones_actual,
                                'rentabilidad_euros': rentabilidad,
                                'aportaciones': aportaciones,
                                'rentabilidad_porc': rentabilidad_porc,
                                'total_saldo_por': 0
                                } ) # type: ignore

    # * Ciclo principal, fuera de los for que recorren fondos y movimientos


    # * Completamos y preparamos los datos
    sentimiento_del_mercado_respuesta = sentimiento_del_mercado()
    #? solo usar para crear del json
    #? crear_tabla_json(tabla_completa, total_saldo)
    datos_json = importacion_json()
    tabla_completa, rentabilidad_acumulada, aportaciones_acumuladas = completar_tabla(tabla_completa, total_saldo, datos_json)
    rentabilidad_acumulada_porc = round(100-((aportaciones_acumuladas*100)/total_saldo), 1)
    exportar_json(datos_json)
    tabla_completa = orden('nombre', tabla_completa)
    print(mostrar_tabla('rentabilidad', tabla_completa))
    print(f'Saldo total: {total_saldo:_.2f} €. Saldo invertido {aportaciones_acumuladas:_.2f} €, con una rentabilidad de {rentabilidad_acumulada:_.2f}, el {rentabilidad_acumulada_porc}%')
    print(sentimiento_del_mercado_respuesta)
    print('''
Alpha: Cuando hablamos de un alfa positivo, significa que el gestor está añadiendo valor a la cartera gracias a su eficacia y a la de todo su equipo invirtiendo.
Beta: Indica cuán sensible es un fondo respecto a los movimientos del mercado y cuánto sube o baja cuando lo hace su índice de referencia. Cuanta más baja sea la beta (1 quiere decir que se comporta exactamente igual), mayor será su correlación con su benchmark. Es decir, menos volátil será el fondo frente al índice de referencia.
''')
    print('''
Avisos:
- Debilidad de agosto a octubre y después, subidas
''')
# https://www.bolsamania.com/noticias/mercados/bolsas-debilidad-agosto-octubre-despues-subidas--14425310.html

    informe()

