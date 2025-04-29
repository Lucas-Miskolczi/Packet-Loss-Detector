# Captura de Paquetes y Análisis de Red

Este programa captura paquetes de una red, almacena la información en una base de datos PostgreSQL y muestra estadísticas básicas a través de una interfaz gráfica (DearPyGui) y una API (FastAPI).

---

## Requisitos Necesarios Previo a Utilizar el Programa:

* Python 3.8 o superior

* Acceso de administrador/root para capturar paquetes de red

* PostgreSQL funcionando

* Si esta usando Windows, debe descargar NPCAP con la opcion de "Install Npcap in WinPcap API-compatible Mode" (https://npcap.com/#download)

## Instalación y Uso

1. **Descargar o clonar** el proyecto:

```
bash
git clone <https://github.com/Lucas-Miskolczi/Packet-Loss-Detector.git>
cd Packet-Loss-Detector
```

2. Uso de entorno virtual **(venv - opcional)**:

```
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Luego instalar las librerías/dependencias:

```
pip install -r requirements.txt
```

4. **Configurar las variables de entorno**:

Modificar el archivo `.env` en la raíz del proyecto con el contenido:

```
dotenv
POSTGRES_USER={tu_usuario} # generalmente postgres
POSTGRES_PASSWORD={tu_contraseña}
POSTGRES_DB={tu_bdd}
POSTGRES_HOST={localhost}
POSTGRES_PORT={5434}
```

5. **Ejecutar el programa**:

Primero ejecutar el archivo "start.py"

```
python start.py
```

Luego, ejecutar el archivo "gui.py" (dentro del src -> src/app/gui.py)

```
python gui.py
```

## Informacion Importante:

La terminal de start.py recibe "CTRL + C" (Win) para finalizar los threads, no es necesario hacer kill a la terminal.
Se autoselecciona la red mas compatible. En caso de no encontrar una, se dispone de una lista e ingreso manual en terminal.
Si no se selecciona la red correcta, puede reemplazar la linea siguiente con el nombre correcto (Line 32, start.py):

```
("ethernet" in iface_name or "wi-fi" in iface_name)
```

API_URL resuelve automaticamente a localhost:8000 ; En caso de usar otro puerto o IP, reemplace la linea siguiente con la API_URL (Line 6, gui.py)

```
API_URL = "http://127.0.0.1:8000"
```

