from dataclasses import dataclass
from typing import List
import time
import eel
import jinja2 as jinja
import requests

api_url = 'https://api.metrobilbao.eus/api/stations/'
station_header = 'SIN'
fetch_headers = {'accept': 'application/ld+json'}
eel.init('web')
template_file = 'web/jinja2/template.html'
timetable_file = 'web/jinja2/timetable.html'
last_platform_data: str = ""


@dataclass
class Train:
    destination: str
    minutes: int
    length: int
    time: str
    line: str
    direction: str = None


@dataclass
class Track:
    trains: List[Train]


@dataclass
class TrainStation:
    station_id: str
    station: str
    entrances: str
    tracks: List[Track]
    error: str = None


def html_id_assigner(platform, train):
    return f"p{platform}t{train}"


@eel.expose
def timetable_updater():
    global last_platform_data
    local_last_platform_data = last_platform_data
    local_current_platform_data = get_timetable_data()
    print(local_current_platform_data)
    for track_index, track in enumerate(range(len(local_current_platform_data.tracks))):
        last_track_data = local_last_platform_data.tracks[track]
        current_track_data = local_current_platform_data.tracks[track]
        for train_index, train in enumerate(range(len(current_track_data.trains))):
            id_to_update = html_id_assigner(track_index, train_index)
            if last_track_data.trains[train] != current_track_data.trains[train]:
                html_update = render_timetable_update(current_track_data.trains[train], id_to_update)
                eel.updateTrain(id_to_update, html_update)
            else:
                continue


def get_timetable_data():
    # Obtener los datos JSON de la API
    station_data = requests.get(f"{api_url}{station_header}", headers=fetch_headers).json()
    current_platform_data = get_timetable(station_data)
    timetable_data_storer(current_platform_data)
    return current_platform_data
    # tracks = timetable_data.track
    # trains = tracks[track_no].train
    # train_info = trains[train_no]
    # return train_info


def timetable_data_storer(current_platform_data):
    global last_platform_data
    last_platform_data = current_platform_data


def get_timetable(station_data):
    current_timetable = station_data['platforms']
    station = TrainStation(
        station_id=current_timetable["StationId"],
        station=current_timetable["Station"],
        entrances=current_timetable["Entrances"],
        tracks=[
            Track(trains=[
                Train(
                    destination=train_data["Destination"],
                    minutes=train_data["Minutes"],
                    length=train_data["Length"],
                    time=train_data["Time"],
                    line=train_data["line"],
                    direction=train_data.get("Direction")
                )
                for train_data in track_data
            ])
            for track_data in current_timetable["Platforms"]
        ]
    )
    return station


print(get_timetable_data())


@eel.expose
def get_current_time():
    current_time = time.strftime("%H:%M", time.localtime())
    eel.updateTime(current_time)


@eel.expose
def render_html():
    template_loader = jinja.FileSystemLoader(searchpath="./")
    template_env = jinja.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    rendered_html = template.render(platforms=get_timetable_data, index=html_id_assigner)
    eel.updateHTML(rendered_html)


def render_timetable_update(platform_data, html_id):
    with open("web/jinja2/train.html", 'r') as file:
        template_content = file.read()
        template = jinja.Template(template_content)
        rendered_html = template.render(Train=platform_data, index=html_id)
        return rendered_html


eel_kwargs = {
    'mode': 'chrome',  # Modo de la aplicación (puede ser "chrome" o "edge")
    'host': 'localhost',
    'port': 8080,
    'size': (800, 400)  # Tamaño de la ventana de la aplicación
}

get_timetable_data()

if __name__ == '__main__':
    # Iniciar la aplicación Eel
    eel.start('main.html', jinja_templates='jinja2', options=eel_kwargs, suppress_error=True)
