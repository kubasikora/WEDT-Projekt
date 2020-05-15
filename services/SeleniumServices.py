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
        self.engine = ""

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

    def combine_processed_tags(self, query, titles, urls, snippets):
        """ Combine all scraped tags into one container. Resulting object 
            is a list of dicts.

            Arguments:
            query -- query that generated results
            titles -- tags with titles
            urls -- tags with urls
            snippets -- tags with actual answers
        """
        
        combined_divs = list(zip(titles, urls, snippets))
        results = list(map(lambda x: {
            "query": query, 
            "engine": self.engine, 
            "title": x[0].text, 
            "url": x[1].text, 
            "snippet": x[2].text
        }, combined_divs))

        return results

class DuckDuckGoService(SeleniumService):
    """ Specialized service for scraping duckduckgo.com search engine """

    def __init__(self):
        """ Initialize virtual browser and set correct url base """

        SeleniumService.__init__(self)
        self.engine = "duckduckgo"
        self.URLBASE = "http://duckduckgo.com/html?"

    def process_query(self, query):
        """ Process query and return all titles and snippets in one list 
        
            Arguments:
            query -- query that we want to answer
        """

        params = { "q": query, "kl": "pl-pl" }
        browser_url = "{}{}".format(self.URLBASE, urlencode(params))
        self.load_page(browser_url)
        
        titles = self.get_page_elements_by_class("result__title")
        urls = self.get_page_elements_by_class("result__url")
        snippets = self.get_page_elements_by_class("result__snippet")

        return self.combine_processed_tags(query, titles, urls, snippets)

class BingService(SeleniumService):
    """ Specialized service for scraping bing.com search engine """

    def __init__(self):
        """ Initialize virtual browser and set correct url base """

        SeleniumService.__init__(self)
        self.engine = "bing"
        self.URLBASE = "http://bing.com/search?"

    def process_query(self, query):
        """ Process query and return all titles and snippets in one list 
        
            Arguments:
            query -- query that we want to answer
        """

        params = { "q": query }
        browser_url = "{}{}".format(self.URLBASE, urlencode(params))
        self.load_page(browser_url)

        titles = list()
        urls = list()
        snippets = list()

        result_divs = self.browser.find_elements_by_class_name("b_algo")
        for div in result_divs:
            title = div.find_elements_by_tag_name("h2")
            url = div.find_elements_by_class_name("b_attribution")
            snippet = div.find_elements_by_tag_name("p")

            if len(title) == 1 and len(url) == 1 and len(snippet) == 1:
                titles.append(title[0])
                urls.append(url[0])
                snippets.append(snippet[0])
            
        return self.combine_processed_tags(query, titles, urls, snippets)

class GoogleService(SeleniumService):
    """ Specialized service for scraping bing.com search engine """

    def __init__(self):
        """ Initialize virtual browser and set correct url base """

        SeleniumService.__init__(self)
        self.engine = "google"
        self.URLBASE = "http://google.com/search?"

    def combine_processed_tags(self, query, titles, urls, snippets):
        """ Combine all scraped tags into one container. Resulting object 
            is a list of dicts.

            Arguments:
            query -- query that generated results
            titles -- tags with titles
            urls -- actual url in plain text, thats how google shows urls
            snippets -- tags with actual answers
        """
        
        combined_divs = list(zip(titles, urls, snippets))
        results = list(map(lambda x: {
            "query": query, 
            "engine": self.engine, 
            "title": x[0].text, 
            "url": x[1], 
            "snippet": x[2].text
        }, combined_divs))

        return results

    def process_query(self, query):
        """ Process query and return all titles and snippets in one list 
        
            Arguments:
            query -- query that we want to answer
        """

        params = { "q": query }
        browser_url = "{}{}".format(self.URLBASE, urlencode(params))
        self.load_page(browser_url)

        titles = list()
        urls = list()
        snippets = list()

        result_divs = self.browser.find_elements_by_class_name("rc")
        for div in result_divs:
            a_tags = div.find_elements_by_tag_name("a")
            if len(a_tags) == 0:
                continue
            url = a_tags[0].get_attribute("href")

            h3_tags = div.find_elements_by_tag_name("h3")
            if len(h3_tags) == 0:
                continue
            title = h3_tags[0]

            spans = div.find_elements_by_class_name("st")
            if len(spans) == 0:
                continue
            snippet = spans[0]

            titles.append(title)
            urls.append(url)
            snippets.append(snippet)
        
        return self.combine_processed_tags(query, titles, urls, snippets)
