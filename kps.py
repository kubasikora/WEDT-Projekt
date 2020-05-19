""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT summary_search:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5000
"""

from flask import Flask, render_template

app = Flask(__name__)
app_name = "KPS - moduł odpowiadania na pytania"

@app.route("/")
def index():
    return render_template('kps/index.html', app_name=app_name)

if __name__ == "__main__":
    app.run()