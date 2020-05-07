from services.ClarinService import ClarinService
import json

class MorphologicService(ClarinService):
    """ Service that is specialized for calling morphological 
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
        
        ClarinService.__init__(self)

        settings = {
            "morfeusz2": use_morfeusz2
        }
        self.add_lpmn_command("maca({})".format(json.dumps(settings)))
    

class TaggerService(ClarinService):
    """ Service that is specialized for calling morpho-syntactic
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
        
        ClarinService.__init__(self)

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
    
