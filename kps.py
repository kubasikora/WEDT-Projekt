""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT kps_server:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5000
"""

from flask import Flask, render_template, request, abort, jsonify
from algorithm.QuestionTypeRecognition import QuestionTypeRecognition


app = Flask(__name__)
app_name = "KPS - moduł odpowiadania na pytania"

engines = ["combined", "duckduckgo", "bing", "google", "yahoo"]
strategies = ["singlequery", "stopwords"]

def find_answer(query, engine, strategy):

    recognizer = QuestionTypeRecognition()
    recognizer.set_question(query)
    domain = recognizer.find_domain()

    return {
        "query": query,
        "engine": engine,
        "strategy": strategy,
        "answer": domain,
        "url": "<brak>"
    }


@app.route("/")
def index():
    data = {
        "engines": engines,
        "strategies": strategies
    }
    return render_template('kps/index.html', app_name=app_name, data=data)

@app.route("/fe/ask")
def show_result():
    engine = request.args.get("engine", "combined")
    strategy = request.args.get("strategy", "singlequery")
    query = request.args.get("query")
    
    answer = find_answer(query, engine, strategy)
    return render_template("kps/result.html", app_name=app_name, data=answer)

@app.route("/ask/<query>")
def ask(query):
    engine = request.args.get("engine", "combined")
    strategy = request.args.get("strategy", "singlequery")

    answer = find_answer(query, engine, strategy)
    return jsonify(answer)

if __name__ == "__main__":
    app.run()