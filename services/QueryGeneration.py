import json
import re

class BasicStrategy:
    """ Basic strategy class that provides common utilites for 
        implemented strategies
    """

    def __init__(self, strategy_name):
        self.strategy_name = strategy_name

    def prepare_query(self, query):
        """ Remove all non-letter signs and make all letters
            lowercase

            Arguments:
            query -- query to be preprocessed
        """

        regex = re.compile("[^a-zA-ZąĄęĘżŻźŹćĆńŃóÓłŁśŚ ]")
        return regex.sub("", query).lower()

class SingleQueryStrategy(BasicStrategy):
    """ Implementation of single query algorithm. Returns list that contain
        only one element - the original query
    """

    def __init__(self):
        """ Init strategy with proper serialization name """
        BasicStrategy.__init__(self, "singlequery")

    def generate_queries(self, original_query):
        """ Create list with only one query - the original one 
        
            Arguments:
            query -- original query
        """
        
        queries = list()
        queries.append(self.prepare_query(original_query))
        return queries

class StopwordsStrategy(BasicStrategy):
    """ Implementation of removing stop words strategy. Returns list with query without
        stopwords and optional original query
    """

    def __init__(self, use_original=False, pathname="./config/stopwords.config.json"):
        """ Initialize strategy with proper serialization name
            and load all stopwords from config file

            Arguments
            use_original -- should original query be also included
        """

        BasicStrategy.__init__(self, "stopwords")
        self.use_original = use_original
        with open(pathname, "r") as file:
            self.stopwords = json.load(file)
        
    def is_stopword(self, word):
        """ Check if given word is a stopword

            Arguments:
            word -- word that we want to check
        """
        return word in self.stopwords

    def generate_queries(self, original_query):
        queries = list()
        query = self.prepare_query(original_query)
        query = " ".join(filter(lambda x: not self.is_stopword(x), query.split()))
        queries.append(query)

        og_query = self.prepare_query(original_query)
        if query != og_query and self.use_original:
            queries.append(og_query)

        return queries
        

class QueryGenerator:
    """ Service responsible for generating new queries based on a given one
        Implements strategy pattern. Actual query generation is performed in 
        strategy object

        strategy -- object that is responsible for query generation
    """

    def __init__(self, strategy=SingleQueryStrategy()):
        """ Initialize generator with a given strategy 

            Arguments:
            strategy -- object that is responsible for query generation
        """

        self.strategy = strategy

    def generate_queries(self, query):
        """ Use strategy object and a query to generate some more queries

            Arguments:
            query -- original query that needs to be duplicated in some way
        """

        return self.strategy.generate_queries(query)