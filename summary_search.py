from urllib.parse import urlencode
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.set_headless()
browser = Firefox(options=opts)

DUCKDUCKGO_URL = "http://duckduckgo.com/html?"
params = {"q": "Łukasz Szumowski"}
browser_url = "{}{}".format(DUCKDUCKGO_URL, urlencode(params))

browser.get(browser_url)
titles = browser.find_elements_by_class_name("result__title")
snippets = browser.find_elements_by_class_name("result__snippet")

results = list(zip(titles, snippets))

for result in results:
    print(result[0].text)
    print(result[1].text)
    print("---")