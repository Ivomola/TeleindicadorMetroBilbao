import eel
import requests

station = 'ANS'
api_url = 'https://api.metrobilbao.eus/api/stations/'
fetch_headers = {'accept': 'application/ld+json'}


# Función para obtener los datos del JSON y actualizar el HTML
def update_timetable():
    data = requests.get(f"{api_url}{station}", headers=fetch_headers).json()
    platforms = data['platforms']['Platforms']

    # Actualizar los datos en el HTML
    for i, platform in enumerate(platforms):
        for j, train in enumerate(platform):
            destination = train['Destination']
            minutes = train['Minutes']

            # Actualizar los elementos del HTML con los nuevos datos
            eel.set_train_destination(f".platform-{i + 1} .train-{j + 1} .destination", destination)
            eel.set_train_minutes(f".platform-{i + 1} .train-{j + 1} .time", minutes)


# Iniciar la aplicación Eel
eel.init('web')


@eel.expose
def start_update_thread():
    # Lanzar un hilo para actualizar los datos cada 15 segundos
    def update_thread():
        while True:
            update_timetable()
            eel.sleep(15)

    # Iniciar el hilo
    threading.Thread(target=update_thread, daemon=True).start()


# Definir las funciones expuestas a JavaScript para actualizar los elementos del HTML
eel._js_functions()(
    lambda selector, destination: document.querySelector(selector).textContent == destination, 'set_train_destination')
eel._js_functions()(lambda selector, minutes: document.querySelector(selector).textContent == minutes, 'set_train_minutes')

# Cargar y mostrar el archivo HTML
eel.start('index.html', size=(1200, 360))