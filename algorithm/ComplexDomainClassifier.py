from services.SummaryService import SummaryService
from services.WordnetServices import WordnetService
from services.ClarinServices import SyntaxParserService, NERService, TaggerService, MorphologicService, ClarinService, SynchronousClarinService, AsynchronousClarinService
import json
from collections import OrderedDict


class ComplexDomainClassifier:

    def __init__(self, question, position):
        self.question = question
        self.question_word_position = position
        self.domain = ""

    def call_syntax_parser(self):
    
        parser = SyntaxParserService()
        parser.set_text(self.question)
        res = parser.make_request()

        syntaxInterpreter = SyntaxParserInterpreter(res)
        words = syntaxInterpreter.interpret_result()

        return words[0]

    def get_domain(self) -> str:

        self.domain= ""

        if self.question:

            words = self.call_syntax_parser()
    
            if(words[self.question_word_position].lemma in ["który", "jaki"]):
                recognizer = WhichQuestionRecognizer(words, self.question_word_position)
                self.domain = recognizer.get_domain()

            elif(words[self.question_word_position].lemma == "jak"):
                recognizer = HowQuestionRecognizer(words, self.question_word_position)
                self.domain = recognizer.get_domain()

        return self.domain


class WhichQuestionRecognizer():

    def __init__(self, words, pos, wordnet_domain_path = "config/wordnet-categories.config.json", verb_abbrev_path = "config/verb-abbreviation.config.json"):
        self.words = words
        self.pos = pos
        self.domain = ""

        with open(verb_abbrev_path, "r") as read_file:
            self.verb_list_abrev = json.load(read_file)

        with open(wordnet_domain_path, "r") as read_file:
            self.wordnet_map = json.load(read_file)

    def check_declension(self, question, word):
        question_parts = question.split(':')
        word_parts= word.split(':')
    
        if(len(question_parts) > 3 and len(word_parts) > 3) :
            if(question_parts[2] == word_parts[2] and question_parts[3] == word_parts[3]):
                return True

        return False


    def convert_to_custom_domain(self, domains):
        if len(domains) > 0 :
            for domain in domains:
                print(domain)
                tmp_domain = self.wordnet_map.get(domain)
                if tmp_domain is not None:
                    print("found domain" + tmp_domain)
                    self.domain = tmp_domain
                    break
        
        return self.domain

    def find_domain_by_declension(self, end):
        question_declension = self.words[self.pos].POS
    
        i = self.pos + 1
        while i < end :
            print(self.words[i].lemma + " " + self.words[i].POS + " " + question_declension )
            if((self.check_declension(question_declension, self.words[i].POS)) and (self.check_if_noun(self.words[i]))):
                print("declesnion correct " +self.words[i].lemma)
                morf = WordnetService()
                morf.set_text(self.words[i].lemma)
                res = morf.make_request()
                domains = []
            
                for defs in res[1]:
                    domains.append(defs['domain'])
                print(domains)
                return self.convert_to_custom_domain(domains)
                break
            i = i+1

        return self.domain

    def check_if_noun(self, word):
        noun = [':subst:', ':depr:']
        for j in noun:
            if word.POS.find(j) != -1:
                return True
        return False


    def get_verb_position(self):
        for i in range(0 , len(self.words)):
            for j in self.verb_list_abrev:
                if self.words[i].POS.find(j) != -1:
                    return i
        return -1

    def get_domain(self) -> str:

        self.domain = self.find_domain_by_declension(len(self.words))

        return self.domain

class HowQuestionRecognizer():

    def __init__(self, words, pos, verb_abbrev_path = "config/verb-abbreviation.config.json"):
        self.words = words
        self.pos = pos
        self.domain = ""

        with open(verb_abbrev_path, "r") as read_file:
            self.verb_list_abrev = json.load(read_file)

    def get_verb_position(self):
        for i in range(0 , len(self.words)):
            for j in self.verb_list_abrev:
                if self.words[i].POS.find(j) != -1:
                    return i
        return -1


    def get_domain(self):
        self.domain = ""

        i = self.pos + 1
        
        end = self.get_verb_position()


        if(end == -1): end = len(self.words) 

        while i < end :
            if self.words[i].POS.find('adj') != -1:
                self.domain = "WIELKOŚĆ"
                break
            i = i+1

        if not self.domain:
            self.domain = ["RZECZ", "OSOBA", "MIEJSCE", "WIELKOŚĆ", "DATA"]
        return self.domain


class SyntaxParserInterpreter:

    def __init__(self, text = ""):
        self.text = text
    
    def set_text(self, text):
        self.text = text

    def find(self, key, value):
        if isinstance(value, dict):
            for k, v in value.items():
                if k == key:
                    yield v
                else:
                    for result in self.find(key, v):
                        yield result
        elif isinstance(value, list):
            for element in value:
                for result in self.find(key, element):
                    yield result


    def process_sentence(self, words):
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
            for sentence in tokens:
                words = sentence["s"]["seg"]
                words_list = self.process_sentence(words)
                sentence_list.append(words_list)
        else:
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
        return self.word + " " + self.lemma + " " + self.POS
