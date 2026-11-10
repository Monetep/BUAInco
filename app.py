"""Nova BUAInco. Ejecutar: pip install flask scikit-learn; python app.py."""
import json
import os
import re
import secrets
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from flask import Flask, jsonify, render_template, request, session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
# 1. DATOS DE ENTRENAMIENTO
# Cada frase tiene una intención conocida: con ellas se entrena el clasificador.
EJEMPLOS = {'saldo': ['cuanto dinero tengo',
           'quiero ver mi saldo',
           'plata disponible en mi cuenta',
           'mostrame mi caja de ahorro',
           'que saldo tengo',
           'consulta de cuenta',
           'cuanto hay en la caja',
           'necesito saber mi disponible',
           'ver mis fondos',
           'tengo plata en el banco',
           'mi balance de cuenta',
           'saldo de caja de ahorro',
           'cuanto me queda',
           'quiero saber cuanto tengo',
           'consulta de saldo',
           'dinero que tengo disponible',
           'como esta mi cuenta',
           'mi ca',
           'cuanta guita me queda',
           'cuanto dinero queda en mi cuenta',
           'me decis mi saldo disponible',
           'tengo dinero para gastar',
           'ver saldo actual',
           'cuanta plata tengo disponible'],
 'tc': ['cuanto debo en mi tarjeta de credito',
        'ver el resumen de la tc',
        'cuando vence la tarjeta',
        'quiero consultar consumos de credito',
        'fecha de vencimiento de mi tc',
        'monto del resumen',
        'mi tarjeta visa de credito',
        'cuanto viene de tarjeta este mes',
        'pago de la tarjeta de credito',
        'resumen de credito',
        'vencimiento del plastico de credito',
        'necesito ver la tarjeta de credito',
        'quiero saber lo que debo en la tc',
        'consultar mi tc',
        'mi tarjeta de credito',
        'deuda en tarjeta',
        'cuanto es el resumen de mi tarjeta',
        'importe a pagar de la tc',
        'cual es mi limite de tarjeta',
        'disponible para comprar con tc',
        'limite de mi tarjeta de credito',
        'cuanto puedo gastar con la tc',
        'ver limite disponible',
        'cuanto credito me queda',
        'limite de compras de mi tarjeta',
        'consultar limite tc',
        'disponible de mi tarjeta de credito',
        'cuanto puedo comprar con credito',
        'mi cupo de tarjeta',
        'limite total de mi tc',
        'cuanto disponible queda en la tarjeta',
        'que limite tengo para compras',
        'disponible de credito',
        'saldo disponible en la tc',
        'mi limite de credito',
        'limite para consumos'],
 'td': ['mi tarjeta de debito',
        'quiero consultar mi td',
        'como esta la tarjeta de debito',
        'tarjeta asociada a mi caja de ahorro',
        'informacion de mi debito',
        'esta activa mi tarjeta de debito',
        'ver el estado de la td',
        'consulta por tarjeta de debito',
        'mi plastico de debito',
        'puedo usar la tarjeta de debito',
        'datos de la td',
        'quiero saber sobre mi td',
        'la tarjeta vinculada a mi cuenta',
        'estado de mi debito',
        'ver tarjeta de debito',
        'tarjeta para extraer de cajero',
        'consultar debito',
        'tengo una td'],
 'prestamo': ['quiero pedir un prestamo',
              'necesito un credito personal',
              'me ofrecen un prestamo personal',
              'cotizar cuotas de un prestamo',
              'cuanto me prestan',
              'simular un credito',
              'financiacion personal',
              'quiero un pp',
              'monto disponible para pedir prestado',
              'me gustaria sacar un prestamo',
              'cuanto pagaria por mes',
              'quiero plata en cuotas',
              'opciones de prestamo',
              'oferta de credito personal',
              'pedir dinero prestado',
              'consultar mi pp',
              'tasa de un prestamo',
              'necesito financiar una compra',
              'quiero 300 mil en 12 cuotas',
              'necesito 500000 en 24 meses',
              'me prestan 200 mil',
              'quiero sacar plata prestada',
              'puedo cotizar sin ser cliente',
              'quiero simular 400 mil pesos'],
 'transferencia': ['quiero ver una transferencia',
                   'que paso con el dinero que envie',
                   'estado de mi transferencia',
                   'encontre el comprobante',
                   'hice una transferencia ayer',
                   'consulta por envio de dinero',
                   'se acredito la transferencia',
                   'rastrear un giro bancario',
                   'mi ultima transferencia',
                   'transferi plata',
                   'necesito un comprobante',
                   'movimiento enviado a otro cbu',
                   'quiero saber si llego el dinero',
                   'envie plata a otra cuenta',
                   'consultar una transferencia',
                   'pago por cbu',
                   'se completo mi envio',
                   'estado del giro'],
 'asesor': ['quiero hablar con un asesor',
            'necesito una persona',
            'me atiende alguien',
            'quiero un representante',
            'atencion al cliente',
            'pasame con un humano',
            'hablar con operador',
            'contactar soporte',
            'necesito ayuda de un empleado',
            'derivame a un asesor',
            'quiero hablar con alguien real',
            'comunicarme con el banco',
            'pedir asistencia personal',
            'contacto con un agente humano',
            'hablar con servicio al cliente',
            'necesito un operador',
            'quiero atencion humana',
            'derivacion a una persona'],
 'tarjeta_perdida': ['perdi mi tarjeta',
                     'me robaron la tarjeta de credito',
                     'quiero bloquear mi debito',
                     'no encuentro el plastico',
                     'extravie la tarjeta',
                     'me desaparecio mi tc',
                     'denunciar robo de tarjeta',
                     'me robaron la td',
                     'necesito bloquear una tarjeta',
                     'perdida de tarjeta de credito',
                     'no tengo mi tarjeta de debito',
                     'se llevaron mi tarjeta',
                     'bloquear por robo',
                     'tarjeta extraviada',
                     'no encuentro mi tc',
                     'perdi la td',
                     'me hurtaron el plastico',
                     'anular tarjeta por perdida',
                     'se me perdio el plastico',
                     'me afanaron la tarjeta',
                     'no se donde deje mi debito',
                     'se me extravio la tarjeta',
                     'quiero dar de baja la tarjeta robada',
                     'necesito anular mi tarjeta robada'],
 'productos': ['que productos tienen',
               'que ofrecen',
               'ver productos',
               'conocer el banco',
               'que servicios ofrecen',
               'informacion del banco',
               'quiero conocer sus productos',
               'que puedo contratar',
               'que tiene buainco',
               'que opciones bancarias hay',
               'cuentas tarjetas y prestamos',
               'catalogo de productos',
               'quiero ver sus servicios',
               'que ofrecen para nuevos clientes',
               'mostrame los productos',
               'que servicios tienen',
               'informacion de sus productos',
               'que opciones tienen para mi'],
 'alias': ['cual es mi alias',
           'pasame mi cbu',
           'datos para recibir transferencias',
           'mi numero de cbu',
           'ver alias de mi cuenta',
           'necesito mis datos bancarios',
           'consultar mi alias',
           'cual es el cbu de mi cuenta',
           'compartir mi alias',
           'quiero mi cbu',
           'datos de mi caja para recibir plata',
           'dame el alias de la cuenta',
           'mi clave bancaria uniforme',
           'copiar mi cbu',
           'mi alias bancario',
           'mostrar mis datos para transferir',
           'dame mi numero de cuenta',
           'datos para que me manden plata']}

# 2. CONFIGURACIÓN Y DATOS DE PRUEBA
app = Flask(__name__)
app.secret_key = os.environ.get('BUAINCO_SECRET_KEY') or secrets.token_hex(32)
CLIENTES = json.loads(Path(__file__).with_name('clientes.json').read_text(encoding='utf-8'))
TNA = 0.79  # Tasa ilustrativa; no es una oferta financiera.
PLAZOS = (6, 12, 24)
LIMITE_VISITANTE = 1000000
INICIO = '¡Hola! Soy Nova. Puedo contarte sobre nuestras cuentas y tarjetas, cotizar un préstamo o ayudarte con tus productos. No necesitás ser cliente para consultar. ¿En qué te ayudo?'
MENU = ['Ver productos', 'Cotizar un préstamo', 'Soy cliente', 'Hablar con un asesor']
PERSONALES = {'saldo', 'tc', 'td', 'alias', 'transferencia', 'tarjeta_perdida', 'score'}


# 3. INTELIGENCIA ARTIFICIAL: TEXTO, ENTRENAMIENTO Y CLASIFICACIÓN
def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto.lower())
    return ''.join(c for c in texto if unicodedata.category(c) != 'Mn')


def contiene(texto, frase):
    return bool(re.search(r'(?<!\w)' + re.escape(frase) + r'(?!\w)', texto))


def entrenar_modelo(ejemplos=EJEMPLOS):
    frases = [frase for lista in ejemplos.values() for frase in lista]
    etiquetas = [intencion for intencion, lista in ejemplos.items() for _ in lista]
    return make_pipeline(
        TfidfVectorizer(strip_accents='unicode', analyzer='char_wb', ngram_range=(2, 5)),
        LogisticRegression(C=10, max_iter=1000),
    ).fit(frases, etiquetas)


MODELO = entrenar_modelo()


def detectar_intencion(mensaje):
    """Reglas prioritarias para expresiones claras; RL para el resto."""
    t = normalizar(mensaje)
    if any(contiene(t, x) for x in ['perdi', 'perdida', 'robaron', 'bloquear', 'extravie', 'no encuentro']):
        return 'tarjeta_perdida'
    if re.search(r'limite|disponible para comprar', t) and re.search(r'tarjeta|credito|\btc\b', t):
        return 'tc'
    if re.search(r'alias|\bcbu\b|datos para (recibir|transferir)', t):
        return 'alias'
    if re.search(r'\bscore\b|scoring|calificacion crediticia|central de deudores|historial crediticio|mis deudas', t):
        return 'score'
    if re.search(r'productos|que (ofrecen|tienen)|que tarjetas ofrecen|que cuentas ofrecen|conocer el banco|que es.*(cuenta|caja|tarjeta)|como funciona.*(cuenta|caja|tarjeta)', t):
        return 'productos'
    for sigla, intencion in [('pp', 'prestamo'), ('tc', 'tc'), ('td', 'td')]:
        if contiene(t, sigla):
            return intencion
    probabilidades = MODELO.predict_proba([mensaje])[0]
    mejor = probabilidades.argmax()
    return MODELO.classes_[mejor] if probabilidades[mejor] >= 0.45 else None


# 4. UTILIDADES: ESTADO, PERFILES Y CÁLCULOS
def base_estado(estado):
    """Conserva identidad y bloqueos; descarta el paso de la consulta."""
    return {k: estado[k] for k in ('dni', 'bloqueadas') if k in estado}


def perfil_de_prueba(dni):
    """Genera datos reproducibles para cualquier DNI de prueba de 8 dígitos."""
    n = int(dni)
    return {'nombre': 'Cliente', 'saldo': 180000 + n % 73 * 13500,
            'tc': 42000 + n % 59 * 6200, 'limite': 1000000 + n % 5 * 500000,
            'limite_tc': 600000 + n % 5 * 200000, 'transferencia': 12000 + n % 17 * 3100,
            'dia': 10 + n % 12}


def perfil(estado):
    dni = estado.get('dni')
    return (CLIENTES.get(dni) or perfil_de_prueba(dni)) if dni else None


def dinero(numero):
    return f'${numero:,.0f}'.replace(',', '.')


def puntaje(estado):
    """Puntaje reproducible: situación ficticia del DNI y uso de la TC."""
    p = perfil(estado)
    return round(650 + 2 * int(estado['dni'][-2:]) - 120 * p['tc'] / p['limite_tc'])


def evaluacion(estado):
    """Recrea una consulta crediticia con datos del perfil, sin servicios externos."""
    p = perfil(estado)
    score = puntaje(estado)
    riesgo = 'bajo' if score >= 740 else 'moderado' if score >= 650 else 'alto'
    return (f'Evaluación crediticia · Central de Deudores\n'
            f'Score BUAInco: {score}/900 · Riesgo {riesgo}\n'
            f'Límite de préstamo personal del perfil: {dinero(p["limite"])}\n'
            'Consulta recreada con datos ficticios del perfil; no se accede a una central externa. '
            'El DNI de prueba se mantiene durante la sesión y se elimina al cerrarla. No se guarda en una base de datos.')


def respuesta(texto, estado, opciones=None):
    p = perfil(estado)
    return {'texto': texto, 'estado': estado, 'opciones': opciones or [],
            'cliente': p['nombre'] if p else None,
            'perfil': {'saldo': p['saldo'], 'tc': p['tc']} if p else None}


def cuota_francesa(monto, cuotas, tna=TNA):
    r = tna / 12
    return round(monto * r / (1 - (1 + r) ** -cuotas))


def evaluar_prestamo(estado, ingreso):
    """Reglas de decisión transparentes, solo para perfiles de prueba."""
    p = perfil(estado)
    score = puntaje(estado)
    tna = .69 if score >= 760 else .79 if score >= 700 else .95 if score >= 650 else 1.15
    monto, plazo = estado['ultimo_prestamo'], estado['ultimas_cuotas']
    cuota = cuota_francesa(monto, plazo, tna)
    esfuerzo = cuota / ingreso
    motivos = []
    if score < 700:
        motivos.append('score inferior a 700')
    if monto > p['limite']:
        motivos.append('monto superior al límite del perfil')
    if esfuerzo > .30:
        motivos.append('la cuota supera el 30% del ingreso declarado')
    resultado = 'No preaprobado: ' + '; '.join(motivos) if motivos else 'Preaprobado según las reglas del ejercicio'
    texto = (f'Evaluación de préstamo personal\nMonto: {dinero(monto)} · {plazo} cuotas\n'
             f'Score: {score}/900 · TNA del perfil: {tna:.0%}\n'
             f'Cuota calculada: {dinero(cuota)} · Total: {dinero(cuota * plazo)}\n'
             f'Ingreso mensual declarado: {dinero(ingreso)} · Relación cuota/ingreso: {esfuerzo:.1%}\n'
             f'Resultado: {resultado}.\n'
             'Criterios: score mínimo 700, cuota hasta el 30% del ingreso y monto dentro del límite. '
             'Resultado académico con datos de prueba; no genera una solicitud ni desembolso.')
    return respuesta(texto, base_estado(estado), ['Cotizar otro monto', 'Mi score'])


def cotizacion(monto, cuotas, estado):
    cuota = cuota_francesa(monto, cuotas)
    texto = (f'Préstamo personal de {dinero(monto)}\n{cuotas} cuotas estimadas de {dinero(cuota)}\n'
             f'Total estimado: {dinero(cuota * cuotas)}\nTNA: 79% · Sistema francés\n'
             'Cotización orientativa, sin impuestos ni otros cargos (CFT). No implica aprobación.')
    return respuesta(texto, {**base_estado(estado), 'ultimo_prestamo': monto, 'ultimas_cuotas': cuotas},
                     ['Evaluar mi préstamo', 'Mejor en 6 cuotas', 'Mejor en 12 cuotas', 'Mejor en 24 cuotas'])


def extraer_prestamo(mensaje, paso=None):
    """Separa el plazo antes de leer el monto: evita juntar 300000 y 12."""
    t = normalizar(mensaje)
    plazo = re.search(r'\b(\d+)\s*(?:cuotas?|meses?)\b', t)
    cuotas = int(plazo.group(1)) if plazo else None
    if plazo:
        t = t[:plazo.start()] + t[plazo.end():]
    if paso == 'cuotas' and re.fullmatch(r'\s*\d+\s*', t):
        return None, int(t)
    numero = re.search(r'(?<!\w)(\d{1,3}(?:\.\d{3})+|\d+(?:[.,]\d+)?)(?:\s*(millones?|millon|mil|k))?\b', t)
    monto = None
    if numero:
        valor = numero.group(1)
        if re.fullmatch(r'\d{1,3}(?:\.\d{3})+', valor):
            valor = valor.replace('.', '')
        valor = float(valor.replace(',', '.'))
        unidad = numero.group(2)
        monto = round(valor * (1000000 if unidad in ('millon', 'millones') else 1000 if unidad in ('mil', 'k') else 1))
        if re.search(r'-\s*\d', mensaje):
            monto = -abs(monto)
    return monto, cuotas


# 5. DIÁLOGO: PRÉSTAMOS Y RESPUESTAS SEGÚN EL ESTADO
def avanzar_prestamo(mensaje, estado):
    monto, cuotas = extraer_prestamo(mensaje, estado.get('paso'))
    limite = perfil(estado)['limite'] if perfil(estado) else LIMITE_VISITANTE
    monto = monto if monto is not None else estado.get('monto')
    cuotas = cuotas if cuotas is not None else estado.get('cuotas')
    nuevo = base_estado(estado)
    if monto is not None and not 100000 <= monto <= limite:
        return respuesta(f'El monto debe estar entre $100.000 y {dinero(limite)}. ¿Qué monto querés cotizar?',
                         {**nuevo, 'paso': 'monto'}, ['300 mil', '500 mil', 'Cancelar'])
    if monto is not None:
        nuevo['monto'] = monto
    if cuotas is not None and cuotas not in PLAZOS:
        return respuesta('Los plazos disponibles son 6, 12 o 24 cuotas. ¿Cuál elegís?',
                         {**nuevo, 'paso': 'cuotas' if monto else 'monto'}, ['6 cuotas', '12 cuotas', '24 cuotas'])
    if cuotas:
        nuevo['cuotas'] = cuotas
    if not monto:
        return respuesta(f'Podés cotizar entre $100.000 y {dinero(limite)}, en 6, 12 o 24 cuotas. ¿Qué monto necesitás?',
                         {**nuevo, 'paso': 'monto'}, ['300 mil en 12 cuotas', '500 mil en 24 cuotas'])
    if not cuotas:
        return respuesta(f'Para {dinero(monto)}, ¿preferís 6, 12 o 24 cuotas?',
                         {**nuevo, 'paso': 'cuotas'}, ['6 cuotas', '12 cuotas', '24 cuotas'])
    return cotizacion(monto, cuotas, estado)


def vencimiento(dia):
    hoy = date.today()
    fecha = hoy.replace(day=dia)
    if fecha < hoy:
        fecha = (hoy.replace(day=28) + timedelta(days=4)).replace(day=dia)
    return fecha


def responder(mensaje, estado):
    t = normalizar(mensaje.strip())
    social = re.sub(r'[¿?¡!.,]+', '', t).strip()
    p = perfil(estado)
    base = base_estado(estado)
    paso = estado.get('paso')
    if social in ('chau', 'chau nova', 'adios', 'hasta luego', 'hasta pronto', 'nos vemos', 'me voy', 'cerrar sesion', 'salir'):
        return {**respuesta('¡Hasta luego! Tu sesión quedó cerrada.', {}), 'cerrar_sesion': True}
    if social in ('cancelar', 'cancela', 'dejalo', 'olvidalo', 'no quiero seguir'):
        return respuesta('Listo, cancelé esta consulta. ¿En qué más puedo ayudarte?', base, MENU)
    if social in ('hola', 'hola nova', 'buen dia', 'buenas', 'buenas tardes', 'buenas noches', 'hey'):
        saludo = f'¡Hola, {p["nombre"]}!' if p else '¡Hola! Soy Nova.'
        return respuesta(saludo + (' Seguimos con tu consulta; también podés escribir cancelar.' if paso else ' Podés consultar productos o cotizar un préstamo, aunque no seas cliente.'), estado, MENU if not paso else [])
    if social in ('gracias', 'muchas gracias', 'genial', 'perfecto', 'joya', 'buenisimo'):
        return respuesta('¡De nada! Acá estoy si necesitás algo más.', estado)
    if social in ('ayuda', 'que podes hacer', 'como funciona', 'en que me ayudas'):
        return respuesta('Puedo contarte sobre cuentas y tarjetas, cotizar un PP y consultar saldo, alias, TC, TD y transferencias con un DNI de prueba. Escribí cancelar para dejar una consulta.', estado, MENU)
    if social in ('no soy cliente', 'soy visitante', 'continuar como visitante', 'seguir como visitante', 'no tengo cuenta'):
        if paso in ('monto', 'cuotas'):
            visita = {k: estado[k] for k in ('paso', 'monto', 'cuotas') if k in estado}
            return avanzar_prestamo('', visita)
        return respuesta('¡Podés consultar igual! Conocé nuestros productos o cotizá un préstamo sin ingresar un DNI.', {}, MENU[:3])
    if social in ('clientes de prueba', 'ver clientes de prueba', 'mostrar clientes de prueba'):
        listado = '\n'.join(f'{dni} · {CLIENTES[dni]["nombre"]}' for dni in sorted(CLIENTES))
        return respuesta('Elegí uno de estos perfiles ficticios:\n' + listado, estado, sorted(CLIENTES))
    if social in ('soy cliente', 'entrar a mi cuenta', 'iniciar sesion', 'cambiar cliente'):
        return respuesta('Ingresá un DNI de prueba de 8 dígitos. Voy a mostrarte la evaluación crediticia del perfil con datos ficticios. No se consulta ninguna central externa ni se guarda la información en una base de datos; se elimina al cerrar la sesión.', {'paso': 'identificar'}, ['Ver clientes de prueba', 'Continuar como visitante'])

    # Cualquier DNI de prueba de 8 dígitos activa un perfil temporal, sin alta.
    if re.fullmatch(r'\d{8}', mensaje.strip()) and paso not in ('monto', 'cuotas', 'ingreso'):
        dni = mensaje.strip()
        nuevo = {'dni': dni}
        nombre = perfil(nuevo)['nombre']
        informe = evaluacion(nuevo)
        if paso == 'evaluacion_dni':
            nuevo.update(paso='ingreso', ultimo_prestamo=estado['ultimo_prestamo'], ultimas_cuotas=estado['ultimas_cuotas'])
            return respuesta(f'¡Hola, {nombre}!\n{informe}\n\nPara evaluar el préstamo de {dinero(estado["ultimo_prestamo"])}, ¿cuál es tu ingreso mensual neto de prueba?', nuevo, ['Cancelar'])
        if estado.get('pendiente'):
            r = responder(estado['pendiente'], nuevo)
            r['texto'] = f'¡Hola, {nombre}!\n{informe}\n\n' + r['texto']
            return r
        return respuesta(f'¡Hola, {nombre}!\n{informe}\n\n¿Qué querés consultar?', nuevo,
                         ['Consultar saldo', 'Mi score', 'Mi TC', 'Cotizar un préstamo'])

    if social in ('evaluar mi prestamo', 'solicitar prestamo', 'pedir este prestamo') and estado.get('ultimo_prestamo'):
        solicitud = {**base, 'ultimo_prestamo': estado['ultimo_prestamo'], 'ultimas_cuotas': estado['ultimas_cuotas']}
        if p:
            return respuesta('Para calcular la tasa de tu perfil y evaluar la solicitud, ¿cuál es tu ingreso mensual neto de prueba?', {**solicitud, 'paso': 'ingreso'}, ['Cancelar'])
        return respuesta('Para calcular tu tasa y evaluar el préstamo, ingresá un DNI de prueba de 8 dígitos o elegí un perfil. No consultamos centrales externas ni guardamos el DNI en una base de datos.',
                         {**solicitud, 'paso': 'evaluacion_dni'}, ['Ver clientes de prueba', 'Cancelar'])

    if paso == 'ingreso':
        ingreso, _ = extraer_prestamo(mensaje)
        if ingreso is None or not 100000 <= ingreso <= 50000000:
            return respuesta('Ingresá un ingreso mensual neto de prueba entre $100.000 y $50.000.000. Por ejemplo, “800 mil”.', estado, ['Cancelar'])
        return evaluar_prestamo(estado, ingreso)
    if paso == 'evaluacion_dni':
        return respuesta('Para evaluar el préstamo necesito un DNI de prueba de 8 dígitos. También podés elegir uno de la lista.', estado, ['Ver clientes de prueba', 'Cancelar'])

    intencion = detectar_intencion(mensaje)
    # Las consultas públicas pueden interrumpir un trámite sin exigir un DNI.
    publicas = {
        'productos': 'En BUAInco podés conocer la caja de ahorro, tarjetas de débito y crédito, y préstamos personales. También podés cotizar sin ser cliente. ¿Qué te interesa?',
        'asesor': 'Podés comunicarte con un asesor desde el número 0800-000-2824 de BUAInco - opción 2',
    }
    if intencion in publicas:
        return respuesta(publicas[intencion], estado if paso in ('monto', 'cuotas') else base,
                         ['Cotizar un préstamo', 'Ver clientes de prueba'])

    if estado.get('ultimo_prestamo') and re.search(r'mejor|cambiar|eran|equivoque|\by en\b', t):
        monto, cuotas = extraer_prestamo(mensaje)
        if cuotas is None and re.search(r'\ben\s+(6|12|24)\b', t):
            cuotas = int(re.search(r'\ben\s+(6|12|24)\b', t).group(1)); monto = None
        return avanzar_prestamo(mensaje if cuotas is None or monto else f'{cuotas} cuotas',
                                {**base, 'paso': 'cuotas', 'monto': estado['ultimo_prestamo'], 'cuotas': estado['ultimas_cuotas']})
    if paso in ('monto', 'cuotas'):
        # Una consulta bancaria explícita cambia de tema; una respuesta numérica sigue el préstamo.
        if intencion not in PERSONALES:
            return avanzar_prestamo(mensaje, estado)
    if intencion == 'prestamo':
        return avanzar_prestamo(mensaje, base)

    if paso == 'tipo_tarjeta':
        tipo = 'td' if contiene(t, 'td') or contiene(t, 'debito') else 'tc' if contiene(t, 'tc') or contiene(t, 'credito') else None
        if tipo:
            bloqueadas = list(dict.fromkeys([*base.get('bloqueadas', []), tipo]))
            return respuesta(f'Tu tarjeta de {"débito" if tipo == "td" else "crédito"} quedó bloqueada en este perfil. Gestión NX-2048.', {**base, 'bloqueadas': bloqueadas})
        if intencion not in PERSONALES:
            return respuesta('¿Querés bloquear la tarjeta de débito (TD) o crédito (TC)?', estado, ['Débito (TD)', 'Crédito (TC)', 'Cancelar'])
    if intencion in PERSONALES and not p:
        return respuesta('Para consultar tus productos necesito identificar un perfil. Ingresá un DNI de prueba o elegí uno de la lista. La evaluación crediticia usa datos ficticios, sin consultar una central externa. El DNI se mantiene solo durante la sesión y no se guarda en una base de datos.',
                         {'paso': 'identificar', 'pendiente': mensaje}, ['Ver clientes de prueba', 'Continuar como visitante', 'Soy cliente'])
    if intencion == 'tarjeta_perdida':
        return respuesta('Te ayudo a bloquearla. ¿Es de débito (TD) o crédito (TC)?', {**base, 'paso': 'tipo_tarjeta'}, ['Débito (TD)', 'Crédito (TC)', 'Cancelar'])
    if p:
        vence = vencimiento(p['dia']); cierre = vence - timedelta(days=10)
        fecha = (date.today() - timedelta(days=1)).strftime('%d/%m/%Y')
        estado_td = 'bloqueada' if 'td' in base.get('bloqueadas', []) else 'activa'
        estado_tc = 'bloqueada' if 'tc' in base.get('bloqueadas', []) else 'activa'
        textos = {
            'score': evaluacion(estado),
            'saldo': f'Tu caja de ahorro tiene {dinero(p["saldo"])} disponibles.',
            'tc': f'Tu tarjeta de crédito está {estado_tc}.\nLímite total: {dinero(p["limite_tc"])}\nConsumos del resumen: {dinero(p["tc"])}\nCierre: {cierre:%d/%m/%Y}\nVencimiento: {vence:%d/%m/%Y}\nDisponible para compras: {dinero(p["limite_tc"] - p["tc"])}.',
            'td': f'Tu tarjeta de débito está {estado_td} y usa el saldo de tu caja de ahorro: {dinero(p["saldo"])}.',
            'alias': f'Alias de prueba: buainco.{estado["dni"]}\nCBU ficticio: 00000000{estado["dni"]}000000\nTitular del perfil: {p["nombre"]}.',
            'transferencia': f'Última transferencia\nDestinatario: Alex Ríos\nImporte: {dinero(p["transferencia"])}\nFecha: {fecha}\nEstado: completada\nComprobante: BUA-{estado["dni"][-4:]}-01.',
        }
        if intencion in textos:
            return respuesta(textos[intencion], base)
    if paso == 'identificar':
        return respuesta('Necesito un DNI de prueba de 8 dígitos para esta consulta personal. Si preferís, seguimos como visitante.', estado, ['Ver clientes de prueba', 'Continuar como visitante'])
    return respuesta('No llegué a entender. Podés preguntarme por cuentas, tarjetas, préstamos o asesores. Por ejemplo: “¿qué productos tienen?” o “quiero 300 mil en 12 cuotas”.', base, MENU)


# 6. INTERFAZ WEB: FLASK RECIBE MENSAJES Y CONSERVA LA SESIÓN
@app.get('/')
def inicio():
    return render_template('index.html', modo='flask')


@app.post('/api/chat')
def chat():
    datos = request.get_json(silent=True)
    mensaje = str(datos.get('mensaje', ''))[:500] if isinstance(datos, dict) else ''
    if not mensaje.strip():
        return jsonify({'error': 'Escribí un mensaje.'}), 400
    resultado = responder(mensaje, session.get('conversacion', {}))
    if resultado.get('cerrar_sesion'):
        session.clear()
    else:
        session['conversacion'] = resultado['estado']
    return jsonify(resultado)


@app.post('/api/reiniciar')
def reiniciar():
    session.clear()
    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=True)
