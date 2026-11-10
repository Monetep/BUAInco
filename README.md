# BUAInco · Nova

Chatbot bancario académico con perfiles y datos ficticios. El backend en Python clasifica intenciones con TF-IDF de caracteres y regresión logística (scikit-learn), combina reglas para expresiones específicas y conserva el estado breve de cada conversación mediante la sesión de Flask. No consulta centrales crediticias ni requiere claves API. Usá únicamente DNI de prueba.

## Estructura

- `app.py`: **único archivo Python de la aplicación**; está ordenado en datos de entrenamiento, configuración, clasificación de intenciones, utilidades, diálogo e interfaz Flask.
- `clientes.json`: perfiles ficticios; no es una base de datos de personas reales.
- `templates/index.html`: pantalla que sirve Flask.
- `static/`: CSS y JavaScript de la interfaz; `demo.js` permite la demostración estática.
- `dist/`: copia lista para alojar como página estática. Usa reglas JavaScript y **no ejecuta** el clasificador Python.
- `BUAInco-Nova-IA.ipynb`: notebook para revisar y exponer la lógica de IA.
- `EXPLICACION_TP.md`: guía de exposición sobre el funcionamiento, los modelos probados, los conceptos de la materia y el recorrido del código.
- `requirements.txt`: dependencias Python, incluido Gunicorn para despliegue.

## Ejecutar localmente

Requiere Python 3.10 o superior. En la carpeta del proyecto:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abrí `http://127.0.0.1:5000`. Para una instalación mínima también sirven `pip install flask scikit-learn` y `python app.py`; Gunicorn se usa para el despliegue.

## Desplegar en Render (Web Service de Python)

1. Subí **los archivos dentro de esta carpeta** a la raíz de tu repositorio GitHub.
2. Creá un **Web Service** de tipo Python apuntando a ese repositorio.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. Agregá la variable de entorno `BUAINCO_SECRET_KEY` con un valor largo y aleatorio para firmar las sesiones. No la subas a GitHub.

El servidor expone `/` y `/api/chat`. No necesita una base de datos ni servicios externos. El estado de conversación queda en una cookie de sesión firmada; no envíes DNI reales. El presupuesto, score, TNA y evaluación crediticia pertenecen al ejercicio académico, no son una oferta financiera.

## Probar la parte de IA

Abrí `BUAInco-Nova-IA.ipynb` en Jupyter o Colab y ejecutá las celdas en orden. Allí están la validación cruzada, la matriz de confusión, el análisis de errores y, al final, la comparación de regresión logística con Naive Bayes y SVM lineal. Los tres usan el mismo TF-IDF de caracteres y las mismas cinco particiones estratificadas: cada frase evaluada queda fuera del entrenamiento de su ronda. El servidor `app.py` solo entrena y usa el modelo elegido.

| Modelo | Exactitud | F1 macro | Errores / 198 |
| --- | ---: | ---: | ---: |
| Regresión logística (C=10) | 0,783 | 0,777 | 43 |
| SVM lineal (C=1) | 0,803 | 0,793 | 39 |
| Naive Bayes (α=1) | 0,626 | 0,631 | 74 |

El clasificador distingue **9 intenciones** con 198 frases etiquetadas. Eliminamos la apertura de cuentas y su botón. Cualquier DNI de prueba de 8 dígitos activa datos temporales para consultar productos personales, sin alta ni nombre adicional. Los seis DNI de `clientes.json` muestran nombres definidos y los demás generan datos reproducibles. También se quitó `movimientos`; las preguntas sobre límite se clasifican dentro de `tc` y la respuesta muestra límite total, consumos, cierre, vencimiento y disponible.

SVM acierta cuatro frases más que regresión logística en esta validación. Nova conserva regresión porque `predict_proba` permite pedir reformulación por debajo de 0,45. El híbrido sin umbral acierta 161/198; con umbral acierta 143, se equivoca en 14 y pide reformular 41. Estos resultados no se comparan directamente con versiones anteriores porque cambió el conjunto evaluado. Flask usa el clasificador Python; `dist/` es una demo estática con reglas JavaScript.

El notebook `BUAInco-Nova-IA.ipynb` permite repetir la comparación y genera `errores_clasificador.csv`; se incluye el reporte en `analisis/`.
