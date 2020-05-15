""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT summary_search:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5000
"""

from flask import Flask, jsonify, request, abort
from services.SeleniumServices import DuckDuckGoService, BingService, GoogleService, YahooService
from services.QueryGeneration import QueryGenerator, SingleQueryStrategy

app = Flask(__name__)

@app.route("/search/<engine>/<strategy>/<query>", methods=["GET"])
def search(engine, strategy, query):
    if engine == "duckduckgo":
        snippet_service = DuckDuckGoService()
    elif engine == "bing":
        snippet_service = BingService()
    elif engine == "google":
        snippet_service = GoogleService()
    elif engine == "yahoo":
        snippet_service = YahooService()
    else:
        abort(404, description="Search engine not found")

    if strategy == "singlequery":
        strategy_algorithm = SingleQueryStrategy()
    else:
        abort(404, description="Query generation strategy not found")

    query_generator = QueryGenerator(strategy_algorithm)
    queries = query_generator.generate_queries(query)

    results = list()
    for query in queries:
        results += snippet_service.process_query(query)
           
    return jsonify(results)

@app.route("/combined/<strategy>/<query>", methods=["GET"])
def combined_results(strategy, query):
    if strategy == "singlequery":
        strategy_algorithm = SingleQueryStrategy()
    else:
        abort(404, description="Query generation strategy not found")

    query_generator = QueryGenerator(strategy_algorithm)
    queries = query_generator.generate_queries(query)

    processors = list()
    processors.append(DuckDuckGoService())
    processors.append(BingService())
    processors.append(GoogleService())
    processors.append(YahooService())

    results = list()
    for query in queries:
        for processor in processors:
            results += processor.process_query(query)

    return jsonify(results)

@app.route("/engines", methods=["GET"])
def engines():
    engines = ["duckduckgo", "bing", "google", "yahoo"]
    return jsonify(engines)

@app.route("/strategies", methods=["GET"])
def strategies():
    strategies = ["singlequery"]
    return jsonify(strategies)

if __name__ == "__main__":
    app.run()