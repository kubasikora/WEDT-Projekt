import requests
import xmltodict

class ClarinService:
    def __init__(self):
        """
            Initialize service parameters
        """

        self.url_base = "http://ws.clarin-pl.eu/nlprest2/base/process"
    
        self.lpmn = "any2txt"
        self.user = "wedt_pw_demo"
        self.text = ""

    def set_text(self, text: str) -> str:
        """
            Set text to be analyzed by clarin backend
        """

        self.text = text
        return self.text

    def add_lpmn_command(self, lpmn_command) -> str:
        """
            Set command for clarin backend, to process text with
        """

        self.lpmn += "|" + lpmn_command
        return self.lpmn
        
    def make_request(self) -> dict:
        """
            Make request to clarin backend and parse it from xml to 
        """

        request_data = {
            "lpmn": self.lpmn,
            "user": self.user,
            "text": self.text
        }
        call = requests.post(self.url_base, json=request_data)
        if call.status_code != 200:
            raise Exception('Clarin backend response with non 2xx response')

        response = xmltodict.parse(call.text)
        return response