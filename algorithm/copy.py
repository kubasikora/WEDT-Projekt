from services.SummaryService import SummaryService
from services.WordnetServices import WordnetService
from services.ClarinServices import SyntaxParserService, NERService, TaggerService, MorphologicService, ClarinService, SynchronousClarinService, AsynchronousClarinService
import json
from collections import OrderedDict

def callSummaryService(question):
    print("call summary service with question: "+question)
    ss = SummaryService("http://localhost:5000")
    answer = ss.get_snippets(question)
    for singleAnswer in answer:
        print(singleAnswer['snippet'])


def get_verb_position(words):
    verb_list_abrev = [":fin:", ":bedzie:", ":aglt:",":praet:", ":impt:",":imps:",":inf:",":pcon:",":pant:",":ger:",":pact:", ":ppas:", ":winien:"]
    for i in range(0 , len(words)):
        for j in verb_list_abrev:
            if words[i][2].find(j) != -1:
                return i
    return -1


def check_declension(question, word):
    question_parts = question.split(':')
    word_parts= word.split(':')
  
    if(len(question_parts) > 3 and len(word_parts) > 3) :
        if(question_parts[2] == word_parts[2] and question_parts[3] == word_parts[3]):
            return True

    return False


def convert_to_custom_domain(domains, conversion_map):
    domain = "Domain not recognized"
    if len(domains) > 0 :
        print(domains)
        tmp_domain = conversion_map.get(domains[0])
        if tmp_domain :
            domain = tmp_domain
    
    return domain

def find_domain_by_declension(words, pos, end, conversion_map):
    question_declension = words[pos][2]
  
    i = pos + 1
    while i < end :
        if(check_declension(question_declension, words[i][2])):
            morf = WordnetService()
            morf.set_text(words[i][1])
            res = morf.make_request()
            domains = []
            for defs in res[1]:
                domains.append(defs.get('domain'))
                return convert_to_custom_domain(domains, conversion_map)
            break
        i = i+1

    return "Domain not recognized"








def get_domain_from_jak(words, pos):
    adjective_domain = False
    other_domain = False

    i = pos + 1
    end = get_verb_position(words)
    if(end == -1): end = len(words) 

    while i < end :
        if words[i][2].find('adj') != -1:
            adjective_domain = True
            break
        i = i+1

    domain = ""
    if adjective_domain:
        domain = "WIELKOŚĆ"
    else:
        domain = "Domain not recognized" # todo think about it 
        

    return domain

def get_domain_from_jaki_ktory(words, pos, conversion_map):
    end = get_verb_position(words)
    if(end == -1): end = len(words)
    
    domain = find_domain_by_declension(words, pos, end, conversion_map)

    return domain




















def get_complex_domain( sentence, pos, conversion_map):
    parser = SyntaxParserService()
    parser.set_text(sentence)
    res = parser.make_request()

    generated_list = list(find('string', res))
   
    # words is list of [word, lemma, word:symbols]
    words = [generated_list[x:x+3] for x in range(0, len(generated_list), 3)]
    
    if(words[pos][1] in ["który", "jaki"]):
    
        return get_domain_from_jaki_ktory(words, pos, conversion_map)
    elif(words[pos][1] == "jak"):
        return get_domain_from_jak(words, pos)
































def get_basic_domain(question_types, sentence):
    words = sentence.split()
    pos = -1
    type = ""
    for word in words:
        type = question_types.get(word.lower())
        if(type):
            pos = words.index(word)
            break

    return [type, pos]

if __name__ == "__main__":
    with open("params/question-words", "r") as read_file:
        question_types = json.load(read_file)

    with open("params/conversion", "r") as read_file:
        conversion_map = json.load(read_file)

    while True:
        print("waiting for input")
        text = input()
        if text == "exit":
            break

        [domain, pos] = get_basic_domain(question_types, text)

        if domain:
            if(domain == "complex"):
                domain = get_complex_domain(text, pos, conversion_map)
        else:
            print("This type of question is not supprted")

        print(domain)
    
        #wordnet = WordnetService()
        #wordnet.set_text(text)
        #wordnet.request_lemma_info()
        #[dict, list] = wordnet.make_request()
        #print(dict)
        #print(list)
        #print("################################################################")
        
        
        
        #callSummaryService(text)


