from services.WordnetServices import WordnetService

class WordnetInterpreter:

    def __init__ (self, wordnet_map):
        self.wordnet_map = wordnet_map
        self.domain = ""

    def convert_to_custom_domain(self, wordnet_domains):
        self.domain = ""
        if len(wordnet_domains) > 0 :

            for wordnet_domain in wordnet_domains:

                """ find first meaning that its domain appears in self.wordnet_map """ 
                tmp_domain = self.wordnet_map.get(wordnet_domain)

                if tmp_domain is not None:
                    self.domain = tmp_domain
                    break
        
        return self.domain

    def get_wordnet_domains(self, lemma):
        domains = []

        wordnet = WordnetService()
        wordnet.set_text(lemma)
        res = wordnet.make_request()
        
        for defs in res[1]:
            domains.append(defs['domain'])
  
        return domains

class NERInterpreter:

    def __init__(self, text = ""):
        self.text = text
    
    def set_text(self, text):
        self.text = text

    def interpret_result(self):
           
        domain = None

        tokens = self.text["chunkList"]["chunk"]["sentence"]["tok"]

        is_all_ner = True
        nam_category = ""

        index = 0
    
        for word in tokens:

            if isinstance(word, list):
                is_all_ner = False
                break

            else:
                if 'ann' in word:                
                    res = word["ann"]
                    #print (res)

                    if index == 0 and  "@head" not in res:
                        is_all_ner = False
                        break

                    tmp_nam_category = res['@chan']

                    """ different nam_category found """
                    if nam_category:
                        if nam_category != tmp_nam_category:
                            is_all_ner = False
                            break
                    nam_category = tmp_nam_category

                else:
                    is_all_ner = False
                    break

                index = index + 1

        if is_all_ner:
            if nam_category =="nam_liv":
                domain = "OSOBA"
            if nam_category =="nam_fac":
                domain = "MIEJSCE"
            if nam_category =="nam_loc":
                domain = "MIEJSCE"
            if nam_category == "nam_pro":
                domain = "RZECZ"
        
        return domain


class TaggerInterpreter:

    def __init__(self, text = ""):
        self.text = text
    
    def set_text(self, text):
        self.text = text

    def interpret_result(self,format):

        words_list = []
        if format == "LIST":
            sentence_list = []
        else :
            sentence_list = ""

        tokens = self.text["chunkList"]["chunk"]["sentence"]
        
        if isinstance(tokens, list):
            for sentence in tokens:
                words = sentence["tok"]
                words_list = self.process_sentence(words,format)

                if format =="LIST":
                    sentence_list.append(words_list)
                else:
                    sentence_list = sentence_list + " " + words_list
        else:
            words = tokens["tok"]
            words_list = self.process_sentence(words,format)

            if format =="LIST":
                sentence_list.append(words_list)
            else:
                sentence_list = sentence_list + " " + words_list

        
            
        return sentence_list


    def process_sentence(self, words, format):

        if format == "LIST":
            words_list = []

            for token in words:
        
                question_word = ""
                lemma = ""
                pos_tag = ""

                
                question_word = token["orth"]
                lemma = token["lex"]["base"]
                pos_tag = token["lex"]["ctag"]
                            
                words_list.append(WordProperties(question_word, lemma, pos_tag))

            return words_list
        
        else:

            words_list = ""
            
            for token in words:
                lemma = token["lex"]["base"]

                words_list = words_list + " " + lemma

            return words_list



class SyntaxParserInterpreter:

    def __init__(self, text = ""):
        self.text = text
    
    def set_text(self, text):
        self.text = text

    def process_sentence(self, words):
        """ create WordProperties object for each word in sentence """
        words_list = []

        for token in words:
            question_word = ""
            lemma = ""
            pos_tag = ""

            inner_tokens = token["fs"]["f"]

            for inner_token in inner_tokens:

                token_type = inner_token["@name"]

                if token_type == "orth":
                    question_word = inner_token["string"]
                
                if token_type == "disamb":
                    inside_disamb =  inner_token["fs"]["f"]

                    for inside in inside_disamb:
                        if (inside["@name"]) == "interpretation":
                            pos_tag = inside["string"]
                            lemma = pos_tag.split(':')[0]
                            
            words_list.append(WordProperties(question_word, lemma, pos_tag))
        
        return words_list

    def interpret_result(self):
        words_list = []
        sentence_list = []

        tokens = self.text["teiCorpus"]["TEI"]["text"]["body"]["p"]
  
        if isinstance(tokens, list):
            """ query consist of more than one sentence """ 
            for sentence in tokens:
                words = sentence["s"]["seg"]
                words_list = self.process_sentence(words)
                sentence_list.append(words_list)
        else:
            """ query consist of exactly one sentence """ 
            words = tokens["s"]["seg"]
            words_list = self.process_sentence(words)
            sentence_list.append(words_list)
            
        return sentence_list

class WordProperties:

    def __init__(self, word, lemma, pos):
        self.word = word
        self.lemma = lemma
        self.POS = pos

    def __repr__(self):
        return  self.word

