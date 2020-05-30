
from nltk.util import ngrams
import json
class NGram:

    def __init__(self,stopwords_path="./config/stopwords.config.json" ):

        with open(stopwords_path, "r") as read_file:
            self.stopwords = json.load(read_file)

    def set_text(self, text):
        self.words = text

    def find_ngram(self):
        """ create unique unigram, bigram and trigram from one summary """

        unigram_list = list(set(self.words))
        bigram_list = list(set(ngrams(self.words, 2)))
        trigram_list = list(set(ngrams(self.words, 3)))

        return [unigram_list, bigram_list, trigram_list]

    def convert_bigrams_to_string(self, bi):

        index = 0
        for words in bi[0]:
            bi[0][index] = str(words[0]) + " " + str(words[1])
            index = index + 1

        return bi

    def convert_trigrams_to_string(self, tri):

        index = 0
        for words in tri[0]:
            tri[0][index]  = str(words[0])+' '+ str(words[1])+' '+str(words[2])
            index = index + 1
            
        return tri


    def preprocess_summary(self, summaries):
        """ create two list: first with origin summary but without interpuntion, second only lemmas """
        summary_word_list = []
        summary_lemma_list = []

        for sentence in summaries:
            for word in sentence:
                if word.POS != 'interp':
                    summary_word_list.append(word)
                    summary_lemma_list.append(word.lemma)

        return [summary_word_list, summary_lemma_list]

    def add_to_gram_list(self, new_grams, gram_list, gram_position_list, position):
        """ put ngram in gram_list and put id of summary in gram_position_list"""
        for gram in new_grams:
            if gram not in gram_list:
                gram_list.append(gram)
                gram_position_list.append(list())
            index = gram_list.index(gram) 
            gram_position_list[index].append(position)

        return [gram_list, gram_position_list]

    def create_ngram_list(self, summaries):

        all_unigrams = [ [], [] ]
        all_bigrams = [ [], [] ]
        all_trigrams = [ [], [] ]

        sum_index = 0
        for summary in summaries:
            [full_info, lemmas] = self.preprocess_summary(summary)
            self.set_text(lemmas)
            [unigram, bigram, trigram] = self.find_ngram()
        
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

    def split_by_stopwords(self, ngram_list, is_uni):
        no_stop_gram = [[],[]]
        stop_gram = [[],[]]

        index = 0

        for ngram in ngram_list[0]:
 
            if_stopword = True

            if(is_uni):
                if ngram not in self.stopwords: 
                    if_stopword = False
            else:
                for word in ngram:
                    if word not in self.stopwords: 
                        if_stopword = False

            if if_stopword :
                stop_gram[0].append(ngram_list[0][index])
                stop_gram[1].append(ngram_list[1][index])
            else:
                no_stop_gram[0].append(ngram_list[0][index])
                no_stop_gram[1].append(ngram_list[1][index])

            index=index+1

        return no_stop_gram, stop_gram