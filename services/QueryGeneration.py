class SingleQueryStrategy:
    """ Implementation of single query algorithm. Returns list that contain
        only one element - the original query
    """

    def generate_queries(self, original_query):
        """ Create list with only one query - the original one 
        
            Arguments:
            query -- original query
        """
        
        queries = list()
        queries.append(original_query)
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