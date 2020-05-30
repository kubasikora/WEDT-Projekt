from services.WordnetServices import WordnetService
from services.ClarinServices import SyntaxParserService
from algorithm.ServiceParser import SyntaxParserInterpreter, WordnetInterpreter
import json

class ComplexDomainClassifier:

    def __init__(self, question, position):
        self.question = question
        self.question_word_position = position
        self.domain = ""

    def call_syntax_parser(self):
    
        parser = SyntaxParserService()
        parser.set_text(self.question)
        result = parser.make_request()

        """ get list of: word, lemma, tag for each word in question """
        syntax_interpreter = SyntaxParserInterpreter(result)
        words = syntax_interpreter.interpret_result()

        """ return first and only sentence """
        return words[0]

    def get_domain(self) -> str:

        if self.question:

            words = self.call_syntax_parser()
    
            if(words[self.question_word_position].lemma in ["który", "jaki"]):
                recognizer = WhichQuestionRecognizer(words, self.question_word_position)
                self.domain = recognizer.get_domain()

            elif(words[self.question_word_position].lemma == "jak"):
                recognizer = HowQuestionRecognizer(words, self.question_word_position)
                self.domain = recognizer.get_domain()

        return self.domain


class QuestionRecognizer():

    def __init__(self, words, pos, verb_abbrev_path):
        self.words = words
        self.pos = pos
        self.domain = ""

        with open(verb_abbrev_path, "r") as read_file:
            self.verb_list_abrev = json.load(read_file)

    def get_verb_position(self):

        """ find verb position in question """
        for i in range(0 , len(self.words)):
            for j in self.verb_list_abrev:
                if self.words[i].POS.find(j) != -1:
                    return i
        return -1

    def get_essential_position(self):
        begin = self.pos + 1
        verb = self.get_verb_position()
        end = len(self.words)
        return begin, verb, end

class HowQuestionRecognizer(QuestionRecognizer):

    def __init__(self, words, pos, verb_abbrev_path = "config/verb-abbreviation.config.json"):
        
        QuestionRecognizer.__init__(self, words, pos, verb_abbrev_path)

    def get_domain(self):
        
        """ find position of first word after interrogative pronoun and position of verb (or end of sentence if no verb is found) """
        index, verb, end = self.get_essential_position()

        if(verb != -1):
            end = verb

        """ Recognize question like "Jak długi jest" """
        while index < end :
            if self.words[index].POS.find('adj') != -1:
                self.domain = "WIELKOŚĆ"
                break
            index = index+1

        """ Recognize question like "Jak długo ..." or "Jak nazywa się" """ 
        if not self.domain:
            self.domain = ["RZECZ", "OSOBA", "MIEJSCE", "WIELKOŚĆ"]

        return self.domain

class WhichQuestionRecognizer(QuestionRecognizer):

    def __init__(self, words, pos, verb_abbrev_path = "config/verb-abbreviation.config.json", wordnet_domain_path = "config/wordnet-categories.config.json"):

        QuestionRecognizer.__init__(self, words, pos, verb_abbrev_path)

        with open(wordnet_domain_path, "r") as read_file:
            self.wordnet_map = json.load(read_file)

    def check_declension(self, question, word):
        """ check if word declension is consistent with interrogative noun declension """
        question_parts = question.split(':')
        word_parts= word.split(':')

        """ compare tag of word and question: (przypadek i liczba) """
        if(len(question_parts) > 3 and len(word_parts) > 3) :
            if(question_parts[2] == word_parts[2] and question_parts[3] == word_parts[3]):
                return True

        return False

    def check_if_noun(self, word):
       
        noun = [':subst:', ':depr:']
        for j in noun:
            if word.POS.find(j) != -1:
                return True
        return False

    def get_question_word_declension(self):
        return self.words[self.pos].POS

    def check_if_plural_gen(self, pos):
        if pos.find(':pl:') != -1:
            if pos.find(':gen:') != -1:
                return True
        return False

    def find_noun_with_matching_declension(self, index, question_declension, wordnet_parser):

        """ find domain in wordnet if word is noun and declension is consistent with question_declension"""
        if((self.check_declension(question_declension, self.words[index].POS)) and (self.check_if_noun(self.words[index]))):
            domains = wordnet_parser.get_wordnet_domains(self.words[index].lemma)
            self.domain = wordnet_parser.convert_to_custom_domain(domains)
            return True
        else:
            return False

    def find_noun_with_correct_declension(self, index, question_declension, wordnet_parser):

        """ find domain in wordnet if word is noun and declension is consistent with question_declension"""
        if((self.check_if_plural_gen(self.words[index].POS)) and (self.check_if_noun(self.words[index]))):
            domains = wordnet_parser.get_wordnet_domains(self.words[index].lemma)
            self.domain = wordnet_parser.convert_to_custom_domain(domains)
            return True
        else:
            return False


    def get_domain(self) -> str:
        print("Begin checking complex domain")

        begin, verb, end = self.get_essential_position()
        question_declension = self.get_question_word_declension()
           
        wordnet_parser = WordnetInterpreter(self.wordnet_map)

        if begin < end:
            """ question like "ktory z" """
            if self.words[begin].lemma == "z":
                print("question ktory z")
                index = begin
                while index < verb :
                    print(self.words[index])
                    if(self.find_noun_with_correct_declension(index, question_declension, wordnet_parser)):
                        print("End checking complex domain")
                        print(self.words[index])
                        print(self.domain)
                        return self.domain

                    index = index +1
                    

        """ find noun with correct declension between interrogative pronoun and verb """
        index = begin
        while index < verb :

            if(self.find_noun_with_matching_declension(index, question_declension, wordnet_parser)):
                print("End checking complex domain")
                print(self.words[index])
                print(self.domain)
                return self.domain

            index = index +1
        
        """ find adj with correct declension between interrogative pronoun and verb """
        index = begin
        while index < verb :
            if self.words[index].POS.find('adj') != -1:

                domains = wordnet_parser.get_wordnet_domains(self.words[index].lemma)
                self.domain = wordnet_parser.convert_to_custom_domain(domains)

                print("End checking complex domain")
                print(self.words[index])
                print(self.domain)
                return self.domain

            index = index+1

        """ find noun with correct declension between verb and end """
        index = verb + 1
        while index < end :
            if(self.find_noun_with_matching_declension(index, question_declension, wordnet_parser)):
                print("End checking complex domain")
                print(self.words[index])
                print(self.domain)
                return self.domain

            index = index +1

        print("End checking complex domain")
        print(self.domain)
        return self.domain


