from algorithm.ServiceParser import NERInterpreter, TaggerInterpreter, WordnetInterpreter
from services.ClarinServices import TaggerService, NERService

from services.SummaryService import SummaryService
from algorithm.NGram import NGram

import json

class AnswerExtraction:

    def __init__(self, query, domain,  wordnet_domain_path = "config/wordnet-categories.config.json", parameters_path = "config/parameters.config.json"):
        self.query = query
        self.domain = domain
        self.summaries = ""
        self.answer = ""

        with open(wordnet_domain_path, "r") as read_file:
            self.wordnet_map = json.load(read_file)
        
        with open(parameters_path, "r") as read_file:
            self.parameters = json.load(read_file)

    def find_summaries(self, engine, strategy):

        s = SummaryService(self.parameters["summary_search_localhost"])             
        self.summaries = s.get_snippets_by_engine(self.query, engine, strategy)

    def make_tagger_parse(self, query, format):
        parser = TaggerService()
        parser.set_text(query)
        res = parser.make_request()

        tagger_parser = TaggerInterpreter(res)
        word_list = tagger_parser.interpret_result(format)
        return word_list

            
    def find_answer_in_ngram(self, ngram_list):
   
        length = len(ngram_list[0])

        if length == 0: 
            return False

        wordnet_parser = WordnetInterpreter(self.wordnet_map)

        for word in ngram_list[0]:
            domains = wordnet_parser.get_wordnet_domains(word)
            domain = wordnet_parser.convert_to_custom_domain(domains)

            if domain is None:                         
                NER_service = NERService()
                NER_service.set_text(word)
                res = NER_service.make_request()

                NER_parser = NERInterpreter()
                NER_parser.set_text(res)
                domain = NER_parser.interpret_result()
                print("NER "+ word + " " +domain)

            if self.check_domain(word, domain): 
                return True

        return False

    def check_domain(self, word, domain):

        if domain is None:
            return False

        if isinstance(self.domain, list):
            if (domain in self.domain):
                print("check domain " + domain + " " + self.domain + " " + word)
                self.answer = word
                return True
        else:
            if (domain == self.domain):
                print("check domain " + domain + " " + self.domain + " " + word)
                self.answer = word
                return True

        return False    

    def find_question_lemmas(self):
               
        query_list = self.make_tagger_parse(self.query, "LIST")
        query_list = query_list[0]
        query_lemmas = []
        
        for query_word in query_list:
            query_lemmas.append(query_word.lemma)

        return query_lemmas

    def find_summary_lemmas(self, tagger_format):
        print("Begin finding summary")
        summary_list = []

        for summary in self.summaries:
            snippet = summary['snippet']
            if snippet != '':
                result_list = self.make_tagger_parse(snippet, tagger_format)
                summary_list.append(result_list)

        print("End finding summary")
        return summary_list

    def find_answer(self):
        print("Begin finding answer")
        print("Begin tagging")

        """ find lemma from question """
        query_lemmas = self.find_question_lemmas()

        if self.domain == "DATA":
            tagger_format = "COMBINED"
        else:
            tagger_format = "LIST"

        """ find lemma from summaries """
        summary_list = self.find_summary_lemmas(tagger_format)

        print("End tagging")

        if self.domain == "DATA":
            d_regex = DataRegex(summary_list, self.parameters["minimal_regex_appearance"])
            answer = d_regex.find_answer()
            return answer

        nGram = NGram()

        uni, bi, tri = nGram.create_ngram_list(summary_list)
   
        uni = nGram.filter_ngram_list(uni, query_lemmas, self.parameters["minimal_ngram_appearance"], True)
        bi  = nGram.filter_ngram_list(bi, query_lemmas, self.parameters["minimal_ngram_appearance"], False)
        tri = nGram.filter_ngram_list(tri, query_lemmas, self.parameters["minimal_ngram_appearance"], False)
       
        bi = nGram.convert_bigrams_to_string(bi)
        tri = nGram.convert_trigrams_to_string(tri)
            

        print(self.domain)
        print(tri)
        print(bi)
        print(uni)

        if not self.find_answer_in_ngram(tri):
            if not self.find_answer_in_ngram(bi):
                result = self.find_answer_in_ngram(uni)
        
        print("End finding answer")
        return self.answer, "<brak>"





