import sys
import eel
import jinja2 as jinja
import requests
import time
import inflect


# Declarar Inflect

def get_train_index(number):
    train_index = inflect.engine().number_to_words(number)
    return train_index


# Configuración de Eel
eel.init('web')

# URL de la API y configuración de la estación
api_url = 'https://api.metrobilbao.eus/api/stations/'
station = 'SIN'
fetch_headers = {'accept': 'application/ld+json'}

# Ruta al archivo de plantilla HTML
template_file = 'web/jinja2/template.html'
timetable_file = 'web/jinja2/timetable.html'


# Renderizar la plantilla HTML con los datos iniciales
def render_html(platforms_template, station_name):
    template_loader = jinja.FileSystemLoader(searchpath="./")
    template_env = jinja.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    rendered_html = template.render(platforms=platforms_template, index=get_train_index, name=station_name)
    return rendered_html


# Función para obtener los datos actualizados y renderizar el HTML
@eel.expose
def update_data():
    try:
        # Obtener los datos JSON de la API
        data = requests.get(f"{api_url}{station}", headers=fetch_headers).json()
        platforms_data = data['platforms']['Platforms']
        station_friendly_name = data["Name"]
    except KeyError:
        try:
            data = requests.get(f"{api_url}{station}", headers=fetch_headers).json()
            station_friendly_name = data['name']
            html = render_html('no_trains', station_friendly_name)
            eel.updateHTML(html)

        except KeyError:
            station_friendly_name = 'Error'
            platforms_data = 'La estación no existe'
            html = render_html(platforms_data, station_friendly_name)
            eel.updateHTML(html)


    else:

        # Renderizar el HTML con los nuevos datos
        html = render_html(platforms_data, station_friendly_name)

        # Devolver el HTML actualizado al frontend
        eel.updateHTML(html)


# Función para obtener la hora actual y enviarla al frontend
@eel.expose
def get_current_time():
    current_time = time.strftime("%H:%M", time.localtime())
    eel.updateTime(current_time)


def render_timetable_update(platform_data):
    with open(timetable_file, 'r') as file:
        template_content = file.read()
        template = jinja.Template(template_content)
        rendered_html = template.render(platforms=platform_data, index=get_train_index)
        return rendered_html


@eel.expose
def update_timetable():
    updated_data = requests.get(f"{api_url}{station}", headers=fetch_headers).json()
    updated_platform_data = updated_data['platforms']['Platforms']
    for track_count, track in enumerate(range(len(updated_platform_data))):
        for train_count, train in enumerate(range(len(updated_platform_data[track_count]))):
            print(get_train_index(track_count * 2 + train_count + 1))
            current_destination = eel.getTrainDestination(get_train_index(track_count * 2 + train_count + 1))()
            updated_destination = updated_platform_data[track_count][train_count]["Destination"]
            current_time = eel.getTrainTime(get_train_index(track_count * 2 + train_count + 1))()
            updated_time = updated_platform_data[track_count][train_count]["Minutes"]
            if current_destination != updated_destination:
                updated_timetable = render_timetable_update(updated_platform_data)
                eel.updateTimetable(updated_timetable)
            elif updated_time != current_time:
                if current_time == '':
                    updated_timetable = render_timetable_update(updated_platform_data)
                    eel.updateTimetable(updated_timetable)
                elif updated_time == 0:
                    # Renderizar el HTML con los nuevos datos
                    updated_timetable = render_timetable_update(updated_platform_data)
                    eel.updateTimetable(updated_timetable)
                else:
                    eel.updateTrainTime(get_train_index(track_count * 2 + train_count + 1), updated_time)
            else:
                continue


# Definir la configuración de Eel
eel_kwargs = {
    'mode': 'chrome',  # Modo de la aplicación (puede ser "chrome" o "edge")
    'host': 'localhost',
    'port': 8080,
    'size': (800, 400)  # Tamaño de la ventana de la aplicación
}

# Iniciar la aplicación Eel
if __name__ == '__main__':
    # Obtener los datos iniciales y renderizar el HTML
    update_data()

    # Iniciar la aplicación Eel
    eel.start('main.html', jinja_templates='jinja2', options=eel_kwargs, suppress_error=True)
