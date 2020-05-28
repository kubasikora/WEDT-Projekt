import collections
import re


class DataRegex:
    def __init__(self, summaries, minimum_appearance):
        self.summaries = summaries
        self.minimum_appearance = minimum_appearance

    def append_found_regex(self, current_list, summary, regex):
        new_answer = re.findall(regex, summary)
        if len(new_answer) == 0: return current_list
        current_list = current_list + new_answer
        return current_list
        
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

        all_list = full_dates + short_dates + month + numbers + hour + dayweek
        all_list = collections.Counter(all_list).most_common()

        result = []
        for res in all_list:
            if res[1] > self.minimum_appearance:
                result.append(res[0])
        
        return  result