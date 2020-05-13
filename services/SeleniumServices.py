from urllib.parse import urlencode
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

class SeleniumService:
    """ Base service for emulating browser and page scraping """

    def __init__(self):
        """ Initialize virtual browser using selenium webdriver """

        self.opts = Options()
        self.opts.set_headless()
        self.opts.add_argument("lang=pl")
        self.browser = Firefox(options=self.opts)

    def load_page(self, url):
        """ load new page from given url

            Arguments:
            url -- webpage url
        """

        self.browser.get(url)

    def get_page_elements_by_class(self, classname):
        """ Scrape all elements by css classname 

            Arguments:
            classname -- classname of elements that we want to scrape
        """

        elements =  self.browser.find_elements_by_class_name(classname)
        return elements

class DuckDuckGoService(SeleniumService):
    """ Specialized service for scraping duckduckgo.com search engine """

    def __init__(self):
        """ Initialize virtual browser and set correct url base """

        SeleniumService.__init__(self)
        self.URLBASE = "http://duckduckgo.com/html?"

    def process_query(self, query):
        """ Process query and return all titles and snippets in one list 
        
            Arguments:
            query -- query that we want to answer
        """

        params = {"q": query, "kl": "pl-pl"}
        browser_url = "{}{}".format(self.URLBASE, urlencode(params))
        self.load_page(browser_url)
        
        titles = self.get_page_elements_by_class("result__title")
        snippets = self.get_page_elements_by_class("result__snippet")

        combined_divs = list(zip(titles, snippets))
        results = list(map(lambda x: {"query": query, "title": x[0].text, "snippet": x[1].text}, combined_divs))
        return results
