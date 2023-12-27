import urllib
import feedparser

# Base api query url
base_url = 'http://export.arxiv.org/api/query?';

# Search parameters
search_query = 'all:electron' # search for electron in all fields
start = 0                     # retreive the first 5 results
max_results = 5

query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                     start,
                                                     max_results)

# Opensearch metadata such as totalResults, startIndex, 
# and itemsPerPage live in the opensearch namespase.
# Some entry metadata lives in the arXiv namespace.
# This is a hack to expose both of these namespaces in
# feedparser v4.1
# feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
# feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

# perform a GET request using the base_url and query
response = urllib.request.urlopen(base_url+query).read()

# parse the response using feedparser
feed = feedparser.parse(response)
print(f"{feed=}")

# print out feed information
print (f'Feed title:{feed.feed.title}')
print (f'Feed last updated: {feed.feed.updated}')

# print opensearch metadata
print ('totalResults for this query: {feed.feed.opensearch_totalresults}')
print (f'itemsPerPage for this query: {feed.feed.opensearch_itemsperpage}')
print (f'startIndex for this query:{feed.feed.opensearch_startindex}')
print(f"{feed.entries=}")
# Run through each entry, and print out information
for entry in feed.entries:
    print (f'e-print metadata')
    print (f'arxiv-id: {entry.id.split("/abs/")[-1]}')
    print (f'Published: {entry.published}')
    print (f'Title:  {entry.title}')
