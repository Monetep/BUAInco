# BUAInco · Nova

Chatbot bancario académico con perfiles y datos ficticios. El backend en Python clasifica intenciones con TF-IDF de caracteres y regresión logística (scikit-learn), combina reglas para expresiones específicas y conserva el estado breve de cada conversación mediante la sesión de Flask. No consulta centrales crediticias ni requiere claves API. Usá únicamente DNI de prueba.

## Estructura

- `app.py`: **único archivo Python**; contiene los ejemplos de entrenamiento, clasificador, reglas, evaluación y servidor Flask.
- `clientes.json`: perfiles ficticios; no es una base de datos de personas reales.
- `templates/index.html`: pantalla que sirve Flask.
- `static/`: CSS y JavaScript de la interfaz; `demo.js` permite la demostración estática.
- `dist/`: copia lista para alojar como página estática. Usa reglas JavaScript y **no ejecuta** el clasificador Python.
- `BUAInco-Nova-IA.ipynb`: notebook para revisar y exponer la lógica de IA.
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

```bash
python app.py --evaluar
python app.py --comparar
```

`--evaluar` imprime precisión, recall, F1 y matriz de confusión para la regresión logística. `--comparar` prueba también Naive Bayes y SVM lineal. Los tres usan el mismo TF-IDF de caracteres y las mismas cinco particiones estratificadas: cada frase evaluada queda fuera del entrenamiento de su ronda.

| Modelo | Exactitud | F1 macro | Errores / 288 |
| --- | ---: | ---: | ---: |
| Regresión logística (C=10) | 0,733 | 0,731 | 77 |
| SVM lineal (C=1) | 0,729 | 0,726 | 78 |
| Naive Bayes (α=1) | 0,663 | 0,664 | 97 |

Nos quedamos con regresión logística porque rindió mejor en esta prueba y entrega probabilidades con `predict_proba`, usadas para pedir reformulación cuando la mayor es menor que 0,45. Su ventaja sobre SVM es **solo una frase**; este conjunto pequeño no demuestra superioridad general. La evaluación mide el clasificador, no las reglas prioritarias ni el diálogo completo. La app web ejecutada con Flask usa el clasificador Python; `dist/` es solamente una demo web estática.
