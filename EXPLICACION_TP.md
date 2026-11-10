# BUAInco · Explicación del trabajo práctico de IA

## Planteo y desarrollo del proyecto

Lo que quisimos construir fue un **chatbot bancario** que pudiera recibir consultas escritas de manera natural. Queríamos que una persona pudiera preguntar «¿cuánto tengo en mi cuenta?», «perdí la TC» o «quiero un préstamo de 300 mil en 12 cuotas» sin tener que navegar por una lista de opciones. Para eso necesitábamos reconocer qué quería hacer el usuario y, en algunos casos, recordar lo que ya había dicho.

Primero definimos las consultas que el bot debía atender y reunimos ejemplos de distintas maneras de expresarlas. Eso nos llevó a un problema de **procesamiento del lenguaje natural (PLN)**: clasificar cada mensaje según su intención. Usamos TF-IDF para convertir las frases en datos numéricos y probamos tres algoritmos de clasificación supervisada: Naive Bayes, SVM lineal y regresión logística. Los comparamos con las mismas frases y las mismas particiones de validación. SVM logró unos pocos aciertos más, pero nos quedamos con **regresión logística** porque nos permitía estimar la confianza de cada predicción y pedir que reformulen una consulta cuando el resultado era dudoso. No elegimos el modelo solo por el porcentaje de aciertos.

Al probar el chatbot vimos que algunas expresiones necesitaban un tratamiento directo. Por ejemplo, **PP, TC y TD** son siglas concretas, y una pérdida de tarjeta debe tener prioridad sobre otras consultas sobre tarjetas. Por eso combinamos el modelo predictivo con **reglas explícitas**. También agregamos un pequeño **estado de conversación**: si alguien pide un préstamo sin indicar las cuotas, Nova pregunta por ellas y recuerda el monto. El score crediticio y la decisión de preaprobación se calculan mediante reglas del ejercicio; no son predicciones de la regresión logística ni consultas a una central real.

Esto se relaciona con el **agente inteligente** que vimos en la materia: recibe un mensaje, lo procesa y elige una acción. Las reglas nos permiten explicar por qué responde de cierta manera, y el clasificador aporta una forma de generalizar a frases que no escribimos exactamente como ejemplos. No estamos construyendo una IA general ni una red neuronal: hicimos un sistema acotado, que podemos probar y defender.

Para implementarlo usamos **Python** para la clasificación y el diálogo, **scikit-learn** para TF-IDF y los modelos, y **Flask** para conectar ese código con la pantalla. La interfaz HTML, CSS y JavaScript se armó con asistencia de IA. En la lógica fuimos tomando decisiones, probando frases, revisando errores y simplificando funciones hasta dejar un comportamiento que entendemos. El notebook muestra cómo comparamos los modelos; `app.py` contiene el bot que se ejecuta.

## Qué construimos

BUAInco es un prototipo académico de chatbot bancario. El usuario escribe una consulta en lenguaje cotidiano y Nova intenta identificar qué quiere hacer. Puede responder sobre saldo, tarjeta de crédito (TC), tarjeta de débito (TD), préstamos personales (PP), transferencias, alias/CBU, productos y contacto con un asesor. También atiende pérdida de tarjeta. Para los datos personales pide un DNI de prueba; acepta cualquier secuencia de ocho dígitos y genera un perfil reproducible si no figura en los ejemplos. No crea una cuenta real.

Hay dos conversaciones de varios pasos: el préstamo (monto, cuotas, y, si se solicita evaluación, DNI e ingreso declarado) y el bloqueo de tarjeta (débito o crédito). El estado de la sesión le permite recordar qué dato está esperando. Las tasas, saldos, importes de transferencias y resultados crediticios proceden de datos y reglas del ejercicio: no se consulta una central externa ni se concede dinero. El DNI de prueba se conserva durante la sesión para continuar el diálogo y no se guarda en una base de datos.

## Qué parte es IA

La tarea de IA central es la **clasificación de intenciones**. Preparamos 198 frases etiquetadas en nueve categorías. Por ejemplo, «cuánto dinero tengo» corresponde a `saldo` y «quiero pedir un préstamo» a `prestamo`. Es aprendizaje supervisado: las frases y sus etiquetas son conocidas durante el entrenamiento.

`TfidfVectorizer` convierte cada frase en una representación numérica basada en fragmentos de caracteres de dos a cinco posiciones. Es útil para expresiones cortas y pequeñas variaciones de escritura. Una regresión logística aprende de esas representaciones y, ante una frase nueva, estima qué intención es más probable. El modelo se entrena al iniciar `app.py`; durante la conversación se usa para predecir, no para volver a entrenar. Si la mayor puntuación es inferior a 0,45, el bot pide reformular. Ese valor es una regla práctica de decisión, no una garantía estadística de que la predicción sea correcta.

El clasificador no trabaja solo. Hay **reglas prioritarias** para casos que conviene interpretar explícitamente, como pérdida o robo de tarjeta, las siglas PP/TC/TD y alias/CBU. Las respuestas a saludos, el cierre de sesión, la extracción de monto y plazo, y la evaluación crediticia también son reglas programadas. El proyecto combina clasificación predictiva, reglas y un estado de diálogo pequeño; no utiliza un modelo generativo ni aprende de los mensajes recibidos en producción.

## Qué modelos probamos y por qué elegimos uno

Comparamos tres clasificadores con las mismas 198 frases, la misma representación TF-IDF y validación cruzada estratificada de cinco partes. En cada ronda, las frases evaluadas quedan fuera del entrenamiento de esa ronda.

| Modelo | Aciertos | Exactitud | F1 macro |
| --- | ---: | ---: | ---: |
| SVM lineal | 159/198 | 80,3 % | 0,793 |
| Regresión logística | 155/198 | 78,3 % | 0,777 |
| Naive Bayes | 124/198 | 62,6 % | 0,631 |

**SVM obtuvo la mejor exactitud en esta prueba.** Elegimos regresión logística para Nova porque `predict_proba()` facilita aplicar el umbral de 0,45 y pedir una reformulación ante una consulta dudosa. La elección favorece el comportamiento conversacional que queríamos, no una supuesta superioridad en aciertos. Estos valores miden el clasificador aislado sobre un conjunto pequeño de frases elaboradas para el ejercicio; no equivalen al rendimiento general frente a usuarios reales.

También medimos reglas más clasificador con validación cruzada. Sin umbral, hubo 161 aciertos de 198; con el umbral de 0,45, hubo 143 aciertos, 14 respuestas equivocadas y 41 pedidos de reformulación. Los tres resultados reflejan el intercambio: el umbral reduce respuestas erróneas, pero también hace que Nova responda menos consultas directamente. El notebook conserva el análisis de errores y la comparación completa.

## Relación con el material de la materia

En **«Clase nro 1: Definición de la IA»**, la materia presenta cuatro enfoques: sistemas que piensan como humanos, que actúan como humanos, que piensan racionalmente y que actúan racionalmente. BUAInco se vincula sobre todo con el enfoque de **agentes que actúan racionalmente**: recibe un mensaje (*percibe*), identifica una intención y el estado disponible (*procesa*), y elige una respuesta o el próximo dato que debe pedir (*actúa*). Las reglas explícitas recuerdan a un sistema experto, aunque el proyecto no implementa un motor de lógica formal. No pretende imitar el pensamiento humano ni utiliza una red neuronal.

En **«Clase Nro 2: Agentes Inteligentes»**, las consultas independientes se parecen al comportamiento de un **agente reactivo simple**: una entrada activa una respuesta. En los flujos de préstamo y tarjeta perdida hay además un estado breve (`paso`, `monto`, `cuotas`, `dni`) para interpretar la respuesta siguiente. No mantiene un modelo completo del entorno, no optimiza una función de utilidad y no aprende mientras conversa. Esta es una aplicación acotada y explicable de conceptos de agente, percepción, acción, reglas y estado.

## Cómo está organizado el código

El archivo `app.py` se puede recorrer en este orden:

1. **Datos y configuración:** `EJEMPLOS` contiene las frases etiquetadas; `clientes.json` aporta algunos perfiles ficticios. Se definen límites, plazos y mensajes iniciales.
2. **Clasificación:** `normalizar()` unifica el texto; `entrenar_modelo()` arma TF-IDF + regresión logística; `detectar_intencion()` aplica primero reglas claras y luego consulta al modelo.
3. **Utilidades:** `perfil_de_prueba()` crea datos reproducibles a partir del DNI; `puntaje()`, `cuota_francesa()` y `evaluar_prestamo()` hacen cálculos y aplican criterios explícitos. Ese score es una fórmula del ejercicio, no un score de una central real.
4. **Diálogo:** `extraer_prestamo()` busca monto y cuotas; `avanzar_prestamo()` valida y pregunta por lo que falte; `responder()` toma el mensaje y el estado, decide la acción y devuelve respuesta, opciones y estado nuevo.
5. **Interfaz web:** Flask recibe los mensajes en `/api/chat`, conserva el estado de conversación en una sesión firmada y envía la respuesta al JavaScript, que la muestra en HTML/CSS. Al cerrar la sesión, se borra ese estado.

La comparación de modelos, validación cruzada, matriz de confusión y análisis de frases equivocadas están en `BUAInco-Nova-IA.ipynb`, separado del servidor para que el funcionamiento cotidiano de la aplicación sea más sencillo de leer. `requirements.txt` declara Flask, scikit-learn y Gunicorn para despliegue. La carpeta `dist/` contiene una demostración estática con reglas en JavaScript. El clasificador Python funciona en la aplicación ejecutada con Flask.

## Proceso de desarrollo y herramientas

El desarrollo comenzó con la definición de las consultas bancarias que el sistema debía atender. Después agrupamos ejemplos por intención y construimos el flujo de cada operación. Probamos distintos clasificadores, medimos sus errores y elegimos regresión logística para poder pedir reformulación en casos dudosos. Incorporamos reglas para siglas y casos sensibles, y un estado breve para continuar préstamos y tarjetas. Las pruebas con frases problemáticas llevaron a simplificar las intenciones y las respuestas.

La interfaz HTML, CSS y JavaScript se armó con asistencia de IA. En la parte de Python también se usó asistencia durante el desarrollo. La definición del problema, las decisiones sobre intenciones y flujos, las pruebas, la comparación de modelos y la simplificación progresiva del sistema formaron parte del trabajo del equipo.

La aplicación se inicia con `pip install -r requirements.txt` y `python app.py`, y queda disponible en `http://127.0.0.1:5000`. El notebook permite reproducir la tabla comparativa y examinar las frases clasificadas incorrectamente.
