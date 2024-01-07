import feedparser
import urllib.error
import urllib.request 

class arXapi():

    def __init__(self, category:str, identifier:str, base_url:str) -> None:

        self.category:str = category
        self.identifier:str = identifier
        self.base_url:str = base_url
        self.query:str = base_url
        
    def __str__(self):
        return self.identifier 
    
    def construct_search_query(self, **kwargs) ->str:

        """ 
        From arXiv api description:
            If only search_query is given (id_list is blank or not given), 
            then the API will return results for each article that matches the search query.

            If only id_list is given (search_query is blank or not given), then the API 
            will return results for each article in id_list.

            If BOTH search_query and id_list are given, then the API will return each article 
            in id_list that matches search_query. This allows the API to act as a results filter.
        """

        self.query = f"{self.base_url}" + f"search_query="

        keys = kwargs.keys()

        # Adding category info to the query
        if "category" in keys:
                self.query += f"cat:{kwargs['category']}"
        
        # Adding sort method to the query
        if "sort_method" in keys:
            if kwargs['sort_method'] == "submitted_date":
                self.query += "&sortBy=submittedDate"
            elif kwargs['sort_method'] == "relevence":
                self.query += "&sortBy=relevence"
            elif kwargs['sort_method'] == "last_update_date":
                self.query += "&sortBy=lastUpdatedDate"
        else:
            self.query += "&sortBy=submittedDate"
        
        # Adding sort information to the query
        if "sort_order" in keys:
            if kwargs["sort_order"] == "decending":
                self.query += "&sortOrder=descending"
            else:
                self.query += "&sortOrder=ascending"
        else:
            self.query += "&sortOrder=ascending"

        # Adding query chunk information
        if "start_index" in keys:
            self.query +=  f"&start={kwargs['start_index']}"
        else:
            self.query +=  f"&start={0}"
        if "max_results" in keys:
            self.query += f"&max_results={kwargs['max_results']}"
        else:
            self.query += f"&max_results={0}"

        return self.query


    def make_query(self)->str:
        """Make query with urllib.request for self.query and handle the erroe using 
        urllib.errors.
        Accepted arguments: None,
        Request is made based on the value of self.query.
        """

        # Handle query and response to the request.
        try:
            with urllib.request.urlopen(self.query, timeout=20) as response:
                return response.status, response.read()
            
        except urllib.error.HTTPError as err: 
            print (f"HTTPError:\n\t{err.status}\n\t{err.reason}")
            return err.status, None
        except urllib.error.URLError as err:
            print (f"URLError:\n\tstatus={404}\n\t{err.reason}")
            return 404, None
        except TimeoutError as err:
            print("Request timeout")
            return None, None
    
    
    def parse_response(self, response:str)->list:
        self.parsed_response = []
        feed = feedparser.parse(response)
        self.parsed_response = [entry for entry in feed.entries]
        return self.parsed_response

def main():
    obj = arXapi(category="High Energy Astrophysics", identifier="astro-ph.HE", base_url="http://export.arxiv.org/api/query?")
   
    query = obj.construct_search_query(
        category="astro-ph.HE", 
        sort_method="submitted_date",
        sort_order="descenting",
        start_index=0,
        max_results=10,
    )
    print(f"{query=}")
    status, response = obj.make_query()
    parsed_response = obj.parse_response(response=response)
    print(f"{parsed_response}")


if __name__ == "__main__":
    main()

