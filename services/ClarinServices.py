import json
import requests
import xmltodict
import time
import gzip

class ClarinService:
    """ Base service for calling clarin backend. """
    
    def __init__(self):
        """ Initialize service parameters """

        self.lpmn = "any2txt"
        self.user = "wedt_pw_demo"
        self.text = ""

    def set_text(self, text: str) -> str:
        """ Set text to be analyzed by clarin backend 
            
            Arguments:
            text -- text that should be added to request and analyzed
        """

        self.text = text
        return self.text

    def add_lpmn_command(self, lpmn_command) -> str:
        """ Set command for clarin backend, to process text with 
            
            Arguments:
            lpmn_command -- lpmn command thats should be added to request
        """

        self.lpmn += "|" + lpmn_command
        return self.lpmn
        

class SynchronousClarinService(ClarinService):
    """ Extended service for calling clarin backend api that can
        be called in synchronous way """

    def __init__(self):
        """ Init service with synchronous url """

        ClarinService.__init__(self)
        self.url_base = "http://ws.clarin-pl.eu/nlprest2/base/process"

    def make_request(self) -> dict:
        """ Make request to clarin backend and parse it from xml to python dict """

        request_data = {
            "lpmn": self.lpmn,
            "user": self.user,
            "text": self.text
        }
        call = requests.post(self.url_base, json=request_data)
        if call.status_code != 200:
            raise Exception('Clarin backend response with non 2xx response: {}'.format(call.text))

        response = xmltodict.parse(call.text)
        return response

class AsynchronousClarinService(ClarinService):
    """ Extended service for calling clarin backend api that must be 
         called in asynchronous way """

    def __init__(self):
        """ Init service with asynchronous url """

        ClarinService.__init__(self)
        self.url_base = "http://ws.clarin-pl.eu/nlprest2/base/startTask"
        self.url_check = "http://ws.clarin-pl.eu/nlprest2/base/getStatus"
        self.url_download = "http://ws.clarin-pl.eu/nlprest2/base/download"

        self.file_id = ""
        self.compressed_suffix = "ann_morphosyntax.xml.gz"

    def is_document_ready(self) -> bool:
        """ Ask clarin backend whether processed document is ready"""

        raw_response = requests.get(self.url_check + "/" + self.file_id)
        if raw_response.status_code != 200:
            raise Exception('Clarin backend response with non 2xx response: {}'.format(raw_response.text))

        response = json.loads(raw_response.text)
        if response["status"] == "DONE":
            self.file_id = response["value"][0]["fileID"]
            return True
        else:
            return False

    def upload_document(self):
        """ Send document to clarin backend and receive file id """

        request_data = {
            "lpmn": self.lpmn,
            "user": self.user,
            "text": self.text
        }
        call = requests.post(self.url_base, json=request_data)
        self.file_id = call.text
        if call.status_code != 200:
            raise Exception('Clarin backend response with non 2xx response: {}'.format(call.text))

    def request_response(self) -> dict:
        """ Make a request to clarin backend for compressed response """

        result = requests.get(self.url_download + self.file_id + "/" + self.compressed_suffix)
        if result.status_code != 200:
            raise Exception('Clarin backend response with non 2xx response: {}'.format(result.text))

        response = xmltodict.parse(gzip.decompress(result.content))
        return response

    def make_request(self) -> dict:
        """ Make asynchronous request to clarin backend and parse it from xml to python dict """

        self.upload_document()        
        while not self.is_document_ready():
            time.sleep(0.001)
        response = self.request_response()
        return response
        
class MorphologicService(SynchronousClarinService):
    """ Service that is specialized in calling morphological 
        analyzer from clarin. Is able to work with morfeusz in 
        versions 1 and 2.
        URL: http://ws.clarin-pl.eu/morpho.shtml
    """
    
    def __init__(self, use_morfeusz2=True):
        """ Initialize service with proper lpmn command. Uses 
            mofreusz analyzer in versions 1 or 2.

            Keyword arguments:
            use_morfeusz2 -- if set to True will use version 2, if not
                             falls back to version 1, default True
        """
        
        SynchronousClarinService.__init__(self)

        settings = { "morfeusz2": use_morfeusz2 }
        self.add_lpmn_command("maca({})".format(json.dumps(settings)))
    

class TaggerService(SynchronousClarinService):
    """ Service that is specialized in calling morpho-syntactic
        tagger from clarin. Is able to work with wcrft2 tagger 
        and with morfoDita tagger.
        URL: http://ws.clarin-pl.eu/tager.shtml
    """
    
    def __init__(self, 
                 use_wcrft2=True, 
                 use_morfeusz2=True,
                 use_morfoDita=False, 
                 all_forms=False, 
                 guesser=False, 
                 use_present_language_model=True):
        """ Initialize service with proper lpmn command. Uses wcrft2 and 
            morfoDita tagger. By default, uses wcrft2 tagger.

            Keyword arguments:
            use_wcrft2 -- if set to True will use wcrft2 tagger
            use_morfeusz2 -- if set, will use morfeusz in version 2 for 
                             wcrft2 tagging

            use_morfoDita -- if set to True will use morfoDiat tagger 
            all_forms -- find all forms, only for morfoDita tagger
            guesser -- allow tagger to guess type, only for morfoDita tagger
            use_present_language_model -- if set to False, will use language 
                                          from XIX century, only for morfoDita 
        """
        
        SynchronousClarinService.__init__(self)

        settings = {"guesser": guesser}
        if use_wcrft2:
            settings["morfeusz2"] = use_morfeusz2
            self.add_lpmn_command("wcrft2({})".format(json.dumps(settings))) 
        elif use_morfoDita:
            settings["allforms"] = all_forms
            settings["model"] = "XXI" if use_present_language_model else "XIX"
            self.add_lpmn_command("morphoDita({})".format(json.dumps(settings)))
        else:
            raise RuntimeError("Tagger service created without selected tagger")
    
class NERService(SynchronousClarinService):
    """ Service that is specialized in calling named-entity recognition 
        tool -- liner2. Can use up to 8 different models.
        URL: https://ws.clarin-pl.eu/ner.shtml
    """

    def __init__(self, model="top9"):
        """ Initialize service with proper lpmn command. Uses liner2 tool.
            By default, uses top9 model.

            Keyword arguments:
            model -- select which language model should be used by the tool.
                     Tool can use one of eight different models: 
                     - top9 - 9 kategorii
                     - n82 - 82 kategorie
                     - 5nam - 5 kategorii
                     - timex1
                     - timex4
                     - names - granice nazw
                     - events - atrybuty i relacje zdarzeń
                     - all - grupa modeli
        """

        SynchronousClarinService.__init__(self)

        ner_models = ["top9", "n82", "5nam", "timex1", "timex4", "names", "events", "all"]
        if model not in ner_models:
            raise RuntimeError("NER service created with incorrect model")
        settings = {"model":  model}
        self.add_lpmn_command("wcrft2")
        self.add_lpmn_command("liner2({})".format(json.dumps(settings)))

class SyntaxParserService(AsynchronousClarinService):
    """ Service that is specialized in calling syntax parser 
        tool -- spejd.
        URL: https://ws.clarin-pl.eu/spejd.shtml
    """

    def __init__(self):
        """ Initialize service with proper lpmn command. Uses spejd tool. """

        AsynchronousClarinService.__init__(self)

        self.add_lpmn_command('wcrft2({"morfeusz2":false})')
        self.add_lpmn_command("iobber")
        self.add_lpmn_command('liner2({"model":"n82","output":"tei:gz"})')
        self.add_lpmn_command("spejd")
            
class ChunkerService(SynchronousClarinService):
    """ Service that is specialized in calling chunker service
        called iobber
        URL: https://ws.clarin-pl.eu/chunker.shtml
    """

    def __init__(self):
        """ Initialize service. Iobber tool takes no arguments """

        SynchronousClarinService.__init__(self)
        self.add_lpmn_command("wcrft2")
        self.add_lpmn_command("iobber")
