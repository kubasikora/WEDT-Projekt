import json

class BasicDomainClassifier:

    def __init__(self, question, pathname="./config/question-words.config.json"):
        self.question = question
        self.position = -1
        self.domain = ""

        with open(pathname, "r") as read_file:
            self.question_types = json.load(read_file)


    def get_domain(self) -> str:
        """ recognize basic question types and locate position of interrogative pronoun """

        print("Begin checking basic domain")

        self.domain = ""
        
        if self.question:

            words = self.question.split()

            question_word = []
            domains = []
            positions = []

            for word in words:
                tmp_type = self.question_types.get(word.lower())

                """ find all reconizable interrogative pronoun and it's positions """
                if tmp_type:
                    question_word.append(word)
                    domains.append(tmp_type)
                    positions.append(words.index(word))


            if len(question_word) == 1:
                """ set position of first found interrogative pronoun """
                self.domain = domains[0]
                self.position = positions[0]

            elif len(question_word) > 1:

                """ if more than one question word is found, check if it isn't 'co <interrogative pronoun>' case,
                    if not choose first interrogative pronoun 
                """
                if ((question_word[0] == "co") and (positions[1] == positions[0] + 1 )):
                    self.domain = domains[1]
                    self.position = positions[1]
                else:
                    self.domain = domains[0]
                    self.position = positions[0]

        print("End checking basic domain")

        return [self.domain, self.position]
