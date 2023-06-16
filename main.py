import tkinter as tk
from tkhtmlview import HTMLLabel
import requests as req
from tkinter import ttk

station = 'ANS'
api_url = 'https://api.metrobilbao.eus/api/stations/'
fetch_headers = {'accept': 'application/ld+json'}


data = req.get(f"{api_url}{station}", headers=fetch_headers).json()

root = tk.Tk()
root.title("Panel de Salidas")

# Estilos personalizados
style = ttk.Style()
style.configure("TLabel", font=("Arial", 12))
style.configure("Title.TLabel", font=("Arial", 16, "bold"))

# Crear un contenedor para los paneles de salida
container = ttk.Frame(root, padding=20)
container.pack()

# Agregar título
title_label = ttk.Label(container, text="Estación: " + data["platforms"]["Station"], style="Title.TLabel")
title_label.pack()

# Agregar paneles de salida
for platform in data["platforms"]["Platforms"]:
    platform_frame = ttk.Frame(container, padding=10)
    platform_frame.pack(pady=10)

    for train in platform:
        train_frame = ttk.Frame(platform_frame, relief="groove", padding=10)
        train_frame.pack(side="left", padx=10)

        destination_label = ttk.Label(train_frame, text="Destino: " + train["Destination"])
        destination_label.pack()

        minutes_label = ttk.Label(train_frame, text="Minutos: " + str(train["Minutes"]))
        minutes_label.pack()

        length_label = ttk.Label(train_frame, text="Longitud: " + str(train["Length"]))
        length_label.pack()

        time_label = ttk.Label(train_frame, text="Hora: " + train["Time"])
        time_label.pack()

        line_label = ttk.Label(train_frame, text="Línea: " + train["line"])
        line_label.pack()

        if 'Direction' in train:
            direction_label = ttk.Label(train_frame, text="Dirección: " + train["Direction"])
            direction_label.pack()

root.mainloop()
