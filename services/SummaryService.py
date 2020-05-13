import requests
import json

class SummaryService:
    """ Base service for calling summary search daemon """
    
    def __init__(self, url):
        """ Initialize service parameters 
        
            Arguments:
            url -- url of daemon, something like http://localhost:5000
        """

        self.url_base = url

    def get_snippets_by_engine(self, query, engine="duckduckgo"):
        """ Get all snippets from daemon by using single search engine
            
            Arguments:
            query -- query that we want to search,
            engine -- which engine should daemon use
        """

        url = "{}/search/{}/{}".format(self.url_base, engine, query)
        call = requests.get(url)
        if call.status_code != 200:
            raise Exception('Search daemon response with non 2xx response: {}'.format(call.text))

        return json.loads(call.text)
