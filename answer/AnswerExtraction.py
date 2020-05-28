
from services.SeleniumServices import DuckDuckGoService, BingService, GoogleService, YahooService
from services.QueryGeneration import QueryGenerator
from summary_search import create_snippet_service, create_query_strategy
from algorithm.ComplexDomainClassifier import SyntaxParserInterpreter, WordProperties
from services.ClarinServices import TaggerService, NERService
from services.WordnetServices import WordnetService
from services.SummaryService import SummaryService
from answer.NGram import NGram
import re
import collections
import json

class AnswerExtraction:

    def __init__(self, query, domain,  wordnet_domain_path = "config/wordnet-categories.config.json"):
        self.query = query
        self.domain = domain
        self.summaries = ""
        self.answer = ""

        with open(wordnet_domain_path, "r") as read_file:
            self.wordnet_map = json.load(read_file)

    def convert_to_custom_domain(self, domains):
        tmp_domain = None
        if len(domains) > 0 :
            for domain in domains:
                tmp_domain = self.wordnet_map.get(domain)
                if tmp_domain is not None:
                    break
        
        return tmp_domain

    def make_tagger_parse(self, query, format):
        parser = TaggerService()
        parser.set_text(query)
        res = parser.make_request()

        syntax_parser =TaggerInterpreter(res)
        word_list = syntax_parser.interpret_result(format)
        return word_list

    def find_summaries(self, engine, strategy):

        s = SummaryService("http://localhost:5000")             
        self.summaries = s.get_snippets_by_engine(self.query, engine, strategy)


    def compare_summaries_with_query(self, query ,summaries):
        new_summaries = []
        query_lemmas = []
        
        for query_word in query:
            query_lemmas.append(query_word.lemma)

        for summary in summaries:
            counter = 0
            for summary_word in summary:
                if summary_word[0].lemma in query_lemmas:
                        counter = counter + 1
                
            # make filter params
            if(counter > 0):
                new_summaries.append(summary)

        return new_summaries

    def preprocess_summary(self, summaries):
        summary_word_list = []
        summary_lemma_list = []
        for sentence in summaries:
            for word in sentence:
                if word.POS != 'interp':
                    summary_word_list.append(word)
                    summary_lemma_list.append(word.lemma)
        return [summary_word_list, summary_lemma_list]

    def create_ngram_list(self, summaries):
        ngram = NGram()
        all_unigrams = [[],[] ]
        all_bigrams = [ [], []]
        all_trigrams = [[], [] ]


        sum_index = 0
        for summary in summaries:
            [full_info, lemmas] = self.preprocess_summary(summary)
            ngram.set_text(lemmas)
            [unigram, bigram, trigram] = ngram.find_ngram()
        
            all_unigrams = self.add_to_gram_list(unigram,all_unigrams[0],all_unigrams[1], sum_index)
            all_bigrams = self.add_to_gram_list(bigram,all_bigrams[0],all_bigrams[1], sum_index)
            all_trigrams =self.add_to_gram_list(trigram,all_trigrams[0],all_trigrams[1], sum_index)
            sum_index = sum_index + 1

        all_unigrams.append(list())
        for unigram in all_unigrams[1]:
            all_unigrams[2].append(len(unigram))

        all_bigrams.append(list())
        for bigram in all_bigrams[1]:
            all_bigrams[2].append(len(bigram))

        all_trigrams.append(list())
        for trigram in all_trigrams[1]:
            all_trigrams[2].append(len(trigram))

        [all_unigrams[2], all_unigrams[1], all_unigrams[0]] = (list(t) for t in zip(*sorted(zip(all_unigrams[2], all_unigrams[1], all_unigrams[0]), reverse = True)))
        [all_bigrams[2], all_bigrams[1], all_bigrams[0]] = (list(t) for t in zip(*sorted(zip(all_bigrams[2], all_bigrams[1], all_bigrams[0]), reverse = True)))
        [all_trigrams[2], all_trigrams[1], all_trigrams[0]] = (list(t) for t in zip(*sorted(zip(all_trigrams[2], all_trigrams[1], all_trigrams[0]), reverse = True)))

       

        return all_unigrams, all_bigrams, all_trigrams 

    def add_to_gram_list(self, new_grams, gram_list, gram_position_list, position):
        for gram in new_grams:
            if gram not in gram_list:
                gram_list.append(gram)
                gram_position_list.append(list())
            index = gram_list.index(gram) 
            gram_position_list[index].append(position)

        return [gram_list, gram_position_list]

            
    def find_answer_in_ngram(self, ngram_list):
   
        length = len(ngram_list[0])
        if length == 0: 
            return False

        morf = WordnetService()

        for word in ngram_list[0]:
            #print(word)
            morf.set_text(word)
            res = morf.make_request()

            domains = []
            for defs in res[1]:
                domains.append(defs['domain'])

            #print(domains)
            domain = self.convert_to_custom_domain(domains)
            #print(domain)

            if domain is None:                          
                NER_service = NERService()
                NER_service.set_text(word)
                res = NER_service.make_request()

                NER_parser = NERParser()
                NER_parser.set_text(res)
                domain = NER_parser.interpret_result()

            if self.check_domain(word, domain): 
                return True


        return False

    def check_domain(self, word, domain):
        if domain is None:
            return False
        if(domain in self.domain):
            self.answer = word
            print(self.answer)
            return True
        return False


    def find_answer(self):
        print("start finding anwer")
        query_list = self.make_tagger_parse(self.query, "LIST")

        query_list = query_list[0]

        query_lemmas = []
        
        for query_word in query_list:
            query_lemmas.append(query_word.lemma)
            
        summary_list = []
        print("end tagging query")

        if self.domain == "DATA":
            tagger_format = "COMBINED"
        else:
            tagger_format = "LIST"

        for summary in self.summaries:
            snippet = summary['snippet']
            if snippet != '':
                result_list = self.make_tagger_parse(snippet, tagger_format)
                summary_list.append(result_list)
        print("end tagging summaries")


        if self.domain == "DATA":
            d_regex = DataRegex(summary_list)
            answer = d_regex.find_answer()
            return answer


        uni, bi, tri = self.create_ngram_list(summary_list)
        print("end creating ngram")
        uni = self.filter_ngram_list(uni, query_lemmas, 3, True)
        bi = self.filter_ngram_list(bi, query_lemmas, 3, False)
        tri = self.filter_ngram_list(tri, query_lemmas, 3, False)
        print("end filtering ngram")
        index = 0
        for words in bi[0]:
            bi[0][index] = str(words[0]) + " " + str(words[1])
            index = index + 1

        index = 0
        for words in tri[0]:
            tri[0][index]  = str(words[0])+' '+str(words[1])+' '+str(words[2])
            index = index + 1
            
        if not self.find_answer_in_ngram(tri):
            if not self.find_answer_in_ngram(bi):
                result = self.find_answer_in_ngram(uni)
        print("end checking in wordnet")
                    
        return self.answer



    def filter_ngram_list(self, ngram_list, query_words, min_appearance, is_uni):
        new_ngram_list = [[], []]

        index = 0

        for ngram in ngram_list[0]:
            if(ngram_list[2][index] < min_appearance): 
                break

            if_not_all_query = False

            if(is_uni):
                if ngram not in query_words: 
                    if_not_all_query = True
            else:
                for word in ngram:
                    if word not in query_words: 
                        if_not_all_query = True

            if if_not_all_query :
                new_ngram_list[0].append(ngram_list[0][index])
                new_ngram_list[1].append(ngram_list[1][index])

            index=index+1
        
        return new_ngram_list

class TaggerInterpreter:

    def __init__(self, text = ""):
        self.text = text
    
    def set_text(self, text):
        self.text = text

    def interpret_result(self,format):

        words_list = []
        sentence_list = []

        tokens = self.text["chunkList"]["chunk"]["sentence"]
        
        if isinstance(tokens, list):
            for sentence in tokens:
                words = sentence["tok"]
                words_list = self.process_sentence(words,format)
                sentence_list.append(words_list)
        else:
            words = tokens["tok"]
            words_list = self.process_sentence(words,format)
            sentence_list.append(words_list)
            
  
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



class NERParser:

    def __init__(self, text = ""):
        self.text = text
    
    def set_text(self, text):
        self.text = text

    def interpret_result(self):
           
        domain = None

        tokens = self.text["chunkList"]["chunk"]["sentence"]["tok"]

        is_all_ner = True
        nam_category = None


        for word in tokens:
            if 'ann' in word:
                res = word["ann"]
                nam_category = res['@chan']
            else:
                is_all_ner = False

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

class DataRegex:
    def __init__(self, summaries):
        self.summaries = summaries

    def append_found_regex(self, current_list, summary, regex):
        new_answer = re.findall(regex, summary)
        if len(new_answer) == 0: return current_list
        current_list = current_list + new_answer
        return current_list
        

    def check_threshold(self, full_dates, short_dates, month, numbers, hour, dayweek):
        
        result = []

        number_lists = [full_dates, short_dates, month, numbers, hour, dayweek]
        print(number_lists)
        for single_list in number_lists:

            if(len(single_list) > 0):
                if(single_list[0][1] > minimum_appearance):
                    result.append(single_list[0][0])
          
        return result

    def find_answer(self):
        full_dates = []
        short_dates = []
        month = []
        numbers = []
        hour = []
        dayweek = []

        for summary in self.summaries:
            
            full_dates = self.append_found_regex(full_dates, summary[0], "([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s[\d]{4})")
            short_dates = self.append_found_regex(short_dates, summary[0],"([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            month = self.append_found_regex(month, summary[0],"(\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            numbers = self.append_found_regex(numbers,summary[0], "\d+")
            hour = self.append_found_regex(hour,summary[0], "\d{1,2}[.:]\d{1,2}")
            dayweek =  self.append_found_regex(dayweek,summary[0], "(\s(?:poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela)\s)")

        all_list = full_dates+short_dates+month+numbers+hour+dayweek
        all_list = collections.Counter(all_list).most_common()
        print(all_list)

        minimum_appearance = 2
        result = []
        for res in all_list:
            if res[1] > minimum_appearance:
                result.append(res[0])
        
        return  result