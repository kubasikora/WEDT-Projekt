
from services.SeleniumServices import DuckDuckGoService, BingService, GoogleService, YahooService
from services.QueryGeneration import QueryGenerator
from summary_search import create_snippet_service, create_query_strategy
from algorithm.ComplexDomainClassifier import SyntaxParserInterpreter, WordProperties
from services.ClarinServices import SyntaxParserService


class AnswerExtraction:

    def __init__(self, query, domain):
        self.query = query
        self.domain = domain
        self.summaries = ""
        self.answer = ""

    def make_syntax_parse(self, query):
        parser = SyntaxParserService()
        parser.set_text(query)
        res = parser.make_request()

        syntax_parser = SyntaxParserInterpreter(res)
        word_list = syntax_parser.interpret_result()
        return word_list

    def find_summaries(self, engine, strategy):
        snippet_service = create_snippet_service(engine)
        strategy_algorithm = create_query_strategy(strategy)

        query_generator = QueryGenerator(strategy_algorithm)
        queries = query_generator.generate_queries(self.query)

        results = list()
        for query in queries:
           results += snippet_service.process_query(query)
             
        self.summaries = results


    def compare_summaries_with_query(self, summaries, query):
        new_summaries = []
        query_lemmas = []
        
        for query_word in query:
            query_lemmas.append(query_word.lemma)

        for summary in summaries:
            counter = 0
            for summary_word in summary:
                if summary_word.lemma in query_lemmas:
                    counter = counter + 1

            # make filter params
            if(counter > 2):
                new_summaries.append(summary)

        return new_summaries

    def find_answer(self):
        print ("yuhu")
        query_list = self.make_syntax_parse(self.query)

        summary_list = []

        for summary in self.summaries:
            snippet = summary['snippet']
            if snippet != '':
                result_list = self.make_syntax_parse(snippet)

                summary_list.append(result_list)

        new_summary_list = []
        print ("yuhu2")
        [new_summary_list] = self.compare_summaries_with_query(summary_list, query_list)

   
        print(summary_list.size + " " + new_summary_list.size)

        return self.answer
