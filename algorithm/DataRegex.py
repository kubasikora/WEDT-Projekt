import collections
import re

class DataTypeRecognition:
    def __init__(self, query, lemmas, position):
        query = query.split()
        self.query = query
        self.query_lemmas = lemmas
        self.position = position

    def recognize_type(self):
        data_type = "all"

        if((self.position > 0) and ((self.query_lemmas[self.position-1]) == "o" )):
            data_type = "hour"
        elif((self.query_lemmas[self.position+1]) == "godzina" ):
            data_type = "hour"
        elif((self.query_lemmas[self.position+1]) == "stulecie" ):
            data_type = "age"
        elif((self.query[self.position+1] )== "latach" ):
            data_type = "range"
        elif ((self.query_lemmas[self.position+1]) == "wiek" ):
            data_type = "age"
        elif((self.query_lemmas[self.position+1]) == "dzień" ):
            data_type = "day"
        elif((self.query_lemmas[self.position+1])== "miesiąc" ):
            data_type = "month"
        elif((self.query_lemmas[self.position+1]) == "rok" ):
            data_type = "year"
        
        return data_type

class DataRegex:
    def __init__(self, summaries, minimum_appearance, date_type):
        self.summaries = summaries
        self.minimum_appearance = minimum_appearance
        self.data_type = date_type

    def append_found_regex(self, current_list, summary, regex):
        new_answer = re.findall(regex, summary)

        if len(new_answer) == 0: return current_list
        current_list = current_list + new_answer
        print (new_answer)
        print(summary)
        print("\n\n")
        return current_list
        
    def find_answer(self):
        regex_list = []
        all_list = []

        #print(self.data_type)

        print (self.data_type)
        if self.data_type == "hour":
            regex_list.append("\d{1,2}\.\d{1,2}")
            regex_list.append("\d{1,2}\s:\s\d{1,2}")
            regex_list.append("\s\d{1,2}\s")
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())
        elif self.data_type == "age":
            regex_list.append("\s[MDCLXVI]+\s")
            regex_list.append("\d{4}")
            regex_list.append("\d+")
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())
        elif self.data_type == "day":
            regex_list.append("(\s(?:poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela)\s)")
            regex_list.append("([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            regex_list.append("\d{1,2}")
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())
        elif self.data_type == "month":
            regex_list.append("(\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            all_list.append(list())       
        elif self.data_type == "year":
            regex_list.append("\d{4}")
            all_list.append(list())
        elif self.data_type == "range":
            regex_list.append("\d{4}\s-\s\d{4}")
            all_list.append(list())
        else:
            regex_list.append("([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s[\d]{4})")
            regex_list.append("([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            regex_list.append("(\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            regex_list.append("(\s(?:poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela)\s)")
            regex_list.append("\d{1,2}\.\d{1,2}")
            regex_list.append("\d{1,2}\s:\s\d{1,2}")
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())
            all_list.append(list())


       
        index = 0
        for regex in regex_list:
            for summary in self.summaries:
                all_list[index] = self.append_found_regex(all_list[index], summary, regex)

            index = index + 1

        index = 0
        for single_list in all_list:
            all_list[index] = collections.Counter(single_list).most_common()
            index = index + 1

        print(all_list)
        result = ""
        for single_list in all_list:
            for res in single_list:
                if res[1] > self.minimum_appearance:  
                    result = res[0]
                    return result
              
        return  result