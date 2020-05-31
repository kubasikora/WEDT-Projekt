from algorithm.ServiceParser import NERInterpreter, TaggerInterpreter, WordnetInterpreter
from services.ClarinServices import TaggerService, NERService

from algorithm.DataRegex import DataRegex, DataTypeRecognition

from services.SummaryService import SummaryService
from algorithm.NGram import NGram

import json

class AnswerExtraction:

    def __init__(self, query, pos, domain,  wordnet_domain_path = "config/wordnet-categories.config.json", parameters_path = "config/parameters.config.json", stopwords_path="./config/stopwords.config.json"):
        self.query = query
        self.position = pos
        self.domain = domain
        self.summaries = ""
        self.answer = ""
        self.url = "<brak>"

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

            
    def check_parameters(self):
        if(self.parameters["minimal_regex_appearance"] < 0) : self.parameters["minimal_regex_appearance"] = 0
        if(self.parameters["minimal_regex_appearance"] > 100) : self.parameters["minimal_regex_appearance"] = 100   
        if(self.parameters["minimal_ngram_appearance"] < 0) : self.parameters["minimal_ngram_appearance"] = 0
        if(self.parameters["minimal_ngram_appearance"] > 100) : self.parameters["minimal_ngram_appearance"] = 100  


    def count_number_of_summary_by_percent(self, percent):
        number = int(len(self.summaries) * percent / 100.0)
        print(number)
        return number

    def find_answer_in_ngram(self, ngram_list):
   
        length = len(ngram_list[0])

        if length == 0: 
            return False

        wordnet_parser = WordnetInterpreter(self.wordnet_map)

        index = 0
        print(ngram_list[0])
        for word in ngram_list[0]:
            domains = ""
            domain = ""
            print(word)
            domains = wordnet_parser.get_wordnet_domains(word)
            domain = wordnet_parser.convert_to_custom_domain(domains)
            print(domain)

            if not domain:                         
                NER_service = NERService()
                NER_service.set_text(word)
                res = NER_service.make_request()

                NER_parser = NERInterpreter()
                NER_parser.set_text(res)
                domain = NER_parser.interpret_result()
                if domain:
                    print("NER "+ word + " " +domain)

            if self.check_domain(word, domain): 
                self.answer = word
                self.url = self.extract_url(ngram_list[1][index])
                return True

            index = index + 1

        return False

   
    def extract_url(self, list_of_index):
        url = self.summaries[list_of_index[0]]['url']
        return url

        #for index in list_of_index:
        #    url.append(self.summaries[index]['url'])

        #url = ','.join(url)
        
    
    def check_domain(self, word, domain):

        if domain is None:
            return False

        if isinstance(self.domain, list):
            if (domain in self.domain):
                return True
        else:
            if (domain == self.domain):
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
        summary_list = []
        
        for summary in self.summaries:
            snippet = summary['snippet']
            title = summary['title']
            snippet = title + ' ' + snippet
        
            if snippet != '':
                result_list = self.make_tagger_parse(snippet, tagger_format)
                summary_list.append(result_list)
               
            

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
        print(summary_list)

        print("End tagging")

        if self.domain == "DATA":
            minimal_appearance = self.count_number_of_summary_by_percent(self.parameters["minimal_regex_appearance"])
            data_type_recognition = DataTypeRecognition(self.query, query_lemmas, self.position)
            regex_type = data_type_recognition.recognize_type()
            d_regex = DataRegex(summary_list, minimal_appearance, regex_type)
            answer = d_regex.find_answer()
            return answer, self.url

        nGram = NGram()

        uni, bi, tri = nGram.create_ngram_list(summary_list)
   
        minimal_appearance = self.count_number_of_summary_by_percent(self.parameters["minimal_ngram_appearance"])

        print("Start filtering ngram")
        print(query_lemmas)
        uni = nGram.filter_ngram_list(uni, query_lemmas, minimal_appearance, True)
        bi  = nGram.filter_ngram_list(bi, query_lemmas, minimal_appearance, False)
        tri = nGram.filter_ngram_list(tri, query_lemmas, minimal_appearance, False)
       
        uni, uni_stop =  nGram.split_by_stopwords(uni, True)
        bi, bi_stop =  nGram.split_by_stopwords(bi, False)
        tri, tri_stop = nGram.split_by_stopwords(tri, False)

        bi = nGram.convert_bigrams_to_string(bi)
        tri = nGram.convert_trigrams_to_string(tri)  

        bi_stop = nGram.convert_bigrams_to_string(bi_stop)
        tri_stop = nGram.convert_trigrams_to_string(tri_stop)  

        print("End filtering ngram")
        print("Start finding anwer in ngram")          

        if not self.find_answer_in_ngram(tri):
            if not self.find_answer_in_ngram(bi):
                if not self.find_answer_in_ngram(uni):
                    if not self.find_answer_in_ngram(tri_stop):
                        if not self.find_answer_in_ngram(bi_stop):
                            result = self.find_answer_in_ngram(uni_stop)
        
        print("End finding answer")
        return self.answer, self.url


