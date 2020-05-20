import json
import re
from services.ClarinServices import ChunkerService
from itertools import combinations

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
            use_original -- should original query be also included,
            pathname -- path to file with stopwords
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
        """ Create list with queries 
        
            Arguments:
            original_query -- original query
        """

        queries = list()
        query = self.prepare_query(original_query)
        query = " ".join(filter(lambda x: not self.is_stopword(x), query.split()))
        queries.append(query)

        og_query = self.prepare_query(original_query)
        if query != og_query and self.use_original:
            queries.append(og_query)

        return queries

class ChunksStrategy(BasicStrategy):
    """ Implementation of querying chunks strategy. Returns list with queries. Queries
        are made out of chunks, where one query can have from 1 to all chunks
    """

    def __init__(self, pathname="./config/stopwords.config.json"):
        """ Initialize strategy with proper serialization name and 
            chunker endpoint service.

            Arguments:
            pathname -- path to list of stopwords 
        """

        BasicStrategy.__init__(self, "chunks")
        self.cs = ChunkerService()
        with open(pathname, "r") as file:
            self.stopwords = json.load(file)
        
    def is_stopword(self, word):
        """ Check if given word is a stopword

            Arguments:
            word -- word that we want to check
        """
        return word in self.stopwords

    def group_by_annotiations(self, tokens):
        """ Group tokens by chunk annotations 
        
            Arguments:
            tokens -- list of tokens
        """
        annotations = {
            "chunk_adjp": {},
            "chunk_agp": {},
            "chunk_np": {}, 
            "chunk_vp": {}
        }

        for word in tokens: 
            anns = word["ann"]
            for chunk in anns:
                if chunk["#text"] != "0":
                    if chunk["#text"] not in annotations[chunk["@chan"]]:
                        annotations[chunk["@chan"]][chunk["#text"]] = []
                    annotations[chunk["@chan"]][chunk["#text"]].append(word["orth"])
        
        return annotations

    def group_tokens_into_chunks(self, annotations):
        """ Change lists of tokens, grouped by annotations and 
            create one list of chunks. Removes duplicates on the end.

            Arguments:
            annotations - dictionary of lists, where keys are chunk groups
        """

        chunks = list()
        for idx, chunktype in enumerate(annotations):
            group = annotations[chunktype]
            for idx, chunk in enumerate(group):
                chunks.append(" ".join(group[chunk]))
        chunks = list(dict.fromkeys(chunks))

        return chunks
        
    def split_to_chunks(self, query):
        """ Splits given query into chunks.

            Arguments:
            query -- original query
        """
    
        self.cs.set_text(query)
        analysis = self.cs.make_request()
        tokens = analysis["chunkList"]["chunk"]["sentence"]["tok"]

        annotations = self.group_by_annotiations(tokens)
        chunks = self.group_tokens_into_chunks(annotations)

        pairs = combinations(chunks, 2)
        for pair in pairs:
            if " ".join(pair) in chunks:
                chunks.remove(" ".join(pair))
    
        return chunks

    def generate_queries(self, original_query):
        """ Create list with queries 
        
            Arguments:
            original_query -- original query
        """

        query = self.prepare_query(original_query)
        chunks = self.split_to_chunks(query)
    
        queries = list()
        for size in range(len(chunks) + 1):
            if size == 0 or size == 1:
                continue
            combinator = combinations(chunks, size)
            comination_list = list(combinator)
            query_list = list()
            for comb in comination_list:
                query_list.append(" ".join(comb))
            queries += query_list

        final_queries = list()
        for query in queries:
            all_stop_words = True
            for word in query.split(" "):
                all_stop_words &= self.is_stopword(word)

            if not all_stop_words:
                final_queries.append(query)
            
        return final_queries

     
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