
from nltk.util import ngrams
class NGram:

    def set_text(self, text):
        self.words = text


    def find_ngram(self):
        unigram_list = list(set(self.words))
  
        bigram_list = list(set(ngrams(self.words, 2)))

        trigram_list = list(set(ngrams(self.words, 3)))


        return [unigram_list, bigram_list, trigram_list]