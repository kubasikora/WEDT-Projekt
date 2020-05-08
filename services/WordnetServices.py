import requests
import json

class WordnetService:
    """ Service that is specialized in calling plWordNet.
        URL: http://plwordnet.pwr.wroc.pl
    """

    def __init__(self):
        """ Initialize service with proper url """
        
        self.url_base = "http://plwordnet.pwr.wroc.pl/wordnet/api/lexemes"
        self.url_senses = "http://plwordnet.pwr.wroc.pl/wordnet/api/senses"
        self.url_domains = "http://plwordnet.pwr.wroc.pl/wordnet/api/domains"
        self.word = ""

        self.load_domains()

    def load_domains(self):
        """ Load domain names from plWordNet backend """

        result = requests.get(self.url_domains)
        if result.status_code != 200:
            raise Exception('Wordnet backend response with non 2xx response: {}'.format(result.text))

        self.domains = json.loads(result.text)

    def set_text(self, word):
        """ Set word to be analyzed """
        self.word = word

    def request_lemma_info(self) -> dict:
        """ Load info about given word """

        result = requests.get(self.url_base + "/"  + self.word)
        if result.status_code != 200:
            raise Exception('Wordnet backend response with non 2xx response: {}'.format(result.text))

        lemma = json.loads(result.text)
        return lemma

    def request_sense_info(self, sense_id) -> dict:
        """ Load info about given lemma sense """

        result = requests.get(self.url_senses + "/"  + sense_id)
        if result.status_code != 200:
            raise Exception('Wordnet backend response with non 2xx response: {}'.format(result.text))

        lemma = json.loads(result.text)
        return lemma

    def get_full_domain(self, domain_id):
        """ Parse domain id to domain name """

        for domain in self.domains:
            if domain["id"] == domain_id:
                return domain["pl"]
        return ""

    def make_request(self) -> (dict, list):
        """ Make request to plWordNet backend and parse response to tuple, 
            where first element is lemma info and second element is a list 
            with all lemma senses """

        lemma = self.request_lemma_info()
        if len(lemma) == 0:
            return ([], [])
        else:
            results = []
            for sense in lemma:
                id = sense["sense_id"]
                result = self.request_sense_info(id)
                result["domain"] = self.get_full_domain(result["domain_id"])
                results.append(result)

        return (lemma, results)
