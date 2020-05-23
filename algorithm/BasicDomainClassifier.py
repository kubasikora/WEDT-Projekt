import json

class BasicDomainClassifier:

    def __init__(self, question, pathname="./config/question-words.config.json"):
        self.question = question
        self.position = -1
        self.domain = ""

        with open(pathname, "r") as read_file:
            self.question_types = json.load(read_file)


    def get_domain(self) -> str:
        self.domain = ""
        
        if self.question:
            words = self.question.split()

            for word in words:
                tmp_type = self.question_types.get(word.lower())
                if tmp_type:
                    self.domain = tmp_type
                    self.position = words.index(word)
                    break
    
        return [self.domain, self.position]
