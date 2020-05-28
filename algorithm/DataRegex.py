import collections
import re

class DataTypeRecognition:
    def __init__(self, query, lemmas, position):
        query = query.split()
        self.query = query
        self.query_lemmas = lemmas
        self.position = position

    def recognize_type(self):
        date_type = "all"

        if((self.position > 0) and (self.query_lemmas[self.position-1] == "o" )):
            date_type = "hour"
        elif((self.position > 0) and (self.query_lemmas[self.position+1] == "godzina" )):
            data_type = "hour"
        elif((self.position > 0) and (self.query_lemmas[self.position+1] == "stulecie" )):
            data_type = "age"
        elif((self.position > 0) and (self.query_lemmas[self.position+1] == "wiek" )):
            data_type = "age"
        elif((self.position > 0) and (self.query_lemmas[self.position+1] == "dzień" )):
            data_type = "day"
        elif((self.position > 0) and (self.query_lemmas[self.position+1] == "miesiąc" )):
            data_type = "month"
        elif((self.position > 0) and (self.query_lemmas[self.position+1] == "rok" )):
            data_type = "year"
        elif((self.position > 0) and (self.query[self.position+1] == "latach" )):
            data_type = "range"
        
        return date_type

class DataRegex:
    def __init__(self, summaries, minimum_appearance, date_type):
        self.summaries = summaries
        self.minimum_appearance = minimum_appearance
        self.date_type = date_type

    def append_found_regex(self, current_list, summary, regex):
        new_answer = re.findall(regex, summary)
        if len(new_answer) == 0: return current_list
        current_list = current_list + new_answer
        return current_list
        
    def find_answer(self):
        regex_list = []

        if self.data_type == "hour":
            regex_list.append("\d{1,2}[.:]\d{1,2}")
        elif self.data_type == "age":
            regex_list.append("\d+")
            regex_list.append("^[MDCLXVI]+$")
        elif self.data_type == "day":
            regex_list.append("\d{1,2}[.:]\d{1,2}")
            regex_list.append("(\s(?:poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela)\s)")
        elif self.data_type == "month":
            regex_list.append("(\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
        elif self.data_type == "year":
            regex_list.append("\d+")
        elif self.data_type == "range":
            regex_list.append("\d{4}-\d{4}")
        else:
            regex_list.append("([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s[\d]{4})")
            regex_list.append("([\d]{1,2}\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            regex_list.append("(\s(?:styczeń|luty|marzec|kwiecień|maj|czerwiec|lipiec|sierpień|wrzesień|październik|listopad|grudzień)\s)")
            regex_list.append("(\s(?:poniedziałek|wtorek|środa|czwartek|piątek|sobota|niedziela)\s)")
            regex_list.append("\d{1,2}[.:]\d{1,2}")

        for summary in self.summaries:
            for regex in regex_list:
                all_list = self.append_found_regex(all_list, summary[0], regex)

        all_list = collections.Counter(all_list).most_common()

        result = []
        for res in all_list:
            if res[1] > self.minimum_appearance:
                result.append(res[0])
        
        return  result