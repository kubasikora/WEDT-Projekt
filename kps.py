""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT kps:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5010
"""

from flask import Flask, render_template, request, abort, jsonify
from algorithm.QuestionTypeRecognition import QuestionTypeRecognition
from algorithm.AnswerExtraction import AnswerExtraction

app = Flask(__name__)
app_name = "KPS - moduł odpowiadania na pytania"

engines = ["combined", "duckduckgo", "bing", "google", "yahoo"]
strategies = ["singlequery", "stopwords", "chunks"]

def find_answer(query, engine, strategy):
        
    recognizer = QuestionTypeRecognition()
    recognizer.set_question(query)
  
    domain = recognizer.find_domain()
    url = "<brak>"
    answer = "<brak>"

    if domain != "Domain not found":
        pos = recognizer.get_position()
        extract_answer = AnswerExtraction(query, pos, domain)
        extract_answer.find_summaries(engine, strategy)
        [answer,url] = extract_answer.find_answer()

    return {
        "query": query,
        "engine": engine,
        "strategy": strategy,
        "answer": answer,
        "url": url
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
    app.run(host="localhost",port=5010)