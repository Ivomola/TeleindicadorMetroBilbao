import tkinter as tk
from tkinterweb import HtmlFrame
import requests as req


station = 'ANS'
api_url = 'https://api.metrobilbao.eus/api/stations/'
fetch_headers = {'accept': 'application/ld+json'}


data = req.get(f"{api_url}{station}", headers=fetch_headers).json()

root = tk.Tk()
root.title("Panel de Salidas")

html = "<style>"
html += "body { font-family: Arial, sans-serif; }"
html += "table { border-collapse: collapse; width: 100%; }"
html += "td, th { border: 1px solid #ddd; padding: 8px; }"
html += "th { background-color: #f2f2f2; }"
html += "</style>"

html += "<table>"
html += "<tr>"
html += "<th>Destino</th>"
html += "<th>Minutos</th>"
html += "<th>Longitud</th>"
html += "<th>Hora</th>"
html += "<th>Línea</th>"
html += "<th>Dirección</th>"
html += "</tr>"

for platform in data["platforms"]["Platforms"]:
    for train in platform:
        html += "<tr>"
        html += f"<td>{train['Destination']}</td>"
        html += f"<td>{train['Minutes']}</td>"
        html += f"<td>{train['Length']}</td>"
        html += f"<td>{train['Time']}</td>"
        html += f"<td>{train['line']}</td>"
        if 'Direction' in train:
            html += f"<td>{train['Direction']}</td>"
        html += "</tr>"

html += "</table>"

html_label = HTMLLabel(root, html=html)
html_label.pack(fill="both", expand=True)

root.mainloop()
