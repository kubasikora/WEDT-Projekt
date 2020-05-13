""" Aby uruchomić produkcyjną wersję należy skorzystać z gunicorna 
    Uruchamiamy poleceniem:
    gunicorn -w THREADS -b HOST:PORT summary_search:app 
    - THREADS - liczba niezależnych workerów (wątków)
    - HOST - host, dla localhosta ustawić 127.0.0.1
    - PORT - port, można wybrać dowolny, polecam 5000
"""

from flask import Flask, jsonify
from urllib.parse import urlencode
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.set_headless()


app = Flask(__name__)

DUCKDUCKGO_URL = "http://duckduckgo.com/html?"
params = {"q": "Łukasz Szumowski"}
browser_url = "{}{}".format(DUCKDUCKGO_URL, urlencode(params))


@app.route("/")
def hello():
    browser = Firefox(options=opts)
    browser.get(browser_url)
    titles = browser.find_elements_by_class_name("result__title")
    snippets = browser.find_elements_by_class_name("result__snippet")

    results = list(zip(titles, snippets))
    results = list(map(lambda x: {"title": x[0].text, "snippet": x[1].text}, results))
    return jsonify(results)

if __name__ == "__main__":
    app.run()