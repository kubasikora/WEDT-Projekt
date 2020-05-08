import requests
import json

class WordnetService:
    """ Service that is specialized in calling plWordNet.
        URL: http://plwordnet.pwr.wroc.pl
    """

    def __init__(self):
        """ Initialize service with proper url """
        self.url_base = "http://plwordnet.pwr.wroc.pl/wordnet/api/lexemes"
        self.word = ""

    def set_text(self, word):
        """ Set word to be analyzed """
        self.word = word

    def make_request(self) -> dict:
        result = requests.get(self.url_base + "/"  + self.word)
        if result.status_code != 200:
            raise Exception('Wordnet backend response with non 2xx response: {}'.format(result.text))

        response = json.loads(result.text)
        return response
