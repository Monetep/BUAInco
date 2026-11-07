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
```

Ese comando imprime precision, recall, F1 y matriz de confusión sobre las frases de entrenamiento mediante validación cruzada de cinco partes. La app web ejecutada con Flask usa el clasificador Python; `dist/` es solamente una demo web estática.
