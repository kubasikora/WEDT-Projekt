""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT summary_search:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5000
"""

from flask import Flask, jsonify, request, abort, render_template, url_for
from services.SeleniumServices import DuckDuckGoService, BingService, GoogleService, YahooService
from services.QueryGeneration import QueryGenerator, SingleQueryStrategy, StopwordsStrategy

app = Flask(__name__)

engines = ["duckduckgo", "bing", "google", "yahoo"]
strategies = ["singlequery", "stopwords"]
app_name = "Silnik wyszukiwania podsumowań"

def create_snippet_service(engine):
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

    return snippet_service

def create_query_strategy(strategy):
    if strategy == "singlequery":
        strategy_algorithm = SingleQueryStrategy()
    elif strategy == "stopwords":
        strategy_algorithm = StopwordsStrategy()
    else:
        abort(404, description="Query generation strategy not found")

    return strategy_algorithm

@app.route("/")
def index():
    data = {
        "engines": engines,
        "strategies": strategies
    }
    return render_template('summary/index.html', app_name=app_name, data=data)

@app.route("/fe/search", methods=["GET"])
def show_results():
    engine = request.args.get("engine")
    strategy = request.args.get("strategy")
    query = request.args.get("query")

    snippet_service = create_snippet_service(engine)
    strategy_algorithm = create_query_strategy(strategy)

    query_generator = QueryGenerator(strategy_algorithm)
    queries = query_generator.generate_queries(query)

    results = list()
    for query in queries:
        results += snippet_service.process_query(query)
    
    return render_template('summary/result.html', app_name=app_name, engine=engine, strategy=strategy, data=results)

@app.route("/search/<engine>/<strategy>/<query>", methods=["GET"])
def search(engine, strategy, query):
    snippet_service = create_snippet_service(engine)
    strategy_algorithm = create_query_strategy(strategy)

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
    elif strategy == "stopwords":
        strategy_algorithm = StopwordsStrategy()
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
def engines_list():
    return jsonify(engines)

@app.route("/strategies", methods=["GET"])
def strategies_list():
    return jsonify(strategies)

if __name__ == "__main__":
    app.run()