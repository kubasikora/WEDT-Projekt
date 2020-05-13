""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT summary_search:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5000
"""

from flask import Flask, jsonify, request, abort
from services.SeleniumServices import DuckDuckGoService
from services.QueryGeneration import QueryGenerator, SingleQueryStrategy

app = Flask(__name__)

@app.route("/search/<engine>/<query>", methods=["GET"])
def search(engine, query):
    if engine == "duckduckgo":
        d = DuckDuckGoService()

        qg = QueryGenerator(SingleQueryStrategy())
        queries = qg.generate_queries(query)

        results = list()
        for query in queries:
            results += d.process_query(query)
            
        return jsonify(results)
    else:
        abort(404, description="Search engine not found")

@app.route("/engines")
def engines():
    engines = ["duckduckgo"]
    return jsonify(engines)

if __name__ == "__main__":
    app.run()