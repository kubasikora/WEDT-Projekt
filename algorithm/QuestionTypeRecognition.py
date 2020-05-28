from algorithm.BasicDomainClassifier import BasicDomainClassifier
from algorithm.ComplexDomainClassifier import ComplexDomainClassifier

class QuestionTypeRecognition:

    def __init__(self):
        self.question = ""
        self.domain = ""

    def set_question(self, question: str) -> str:

        self.question = question
        return self.question

    def find_domain(self) -> str:
        
        if self.question:
            
            self.domain = ""

            basic_classifier = BasicDomainClassifier(self.question)
            [tmp_domain, tmp_pos] = basic_classifier.get_domain()
            
            if tmp_domain == "complex":
                complex_classifier = ComplexDomainClassifier(self.question, tmp_pos)
                tmp_domain = complex_classifier.get_domain()

            if not tmp_domain:
                self.domain = "Domain not found"
            else :
                self.domain = tmp_domain

        print("Found domain " + self.domain)
        return self.domain
        
