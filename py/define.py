import urllib.request
import urllib.parse
import json

"""
I suck at web stuff, so I wanna make web stuff :)
requests definitions for words from wiktionary
https://en.wiktionary.org/wiki/Special:ApiSandbox
^ very useful
"""

SEARCH_URL = "https://en.wiktionary.org/w/api.php?"

def make_request(data):
    request_url = SEARCH_URL + urllib.parse.urlencode(data)

    with urllib.request.urlopen(request_url) as f:
        return json.loads(f.read())

def search(query):
    data = {
        "action" : "opensearch",
        "format" : "json",
        "utf-8" : "1",
        "search" : query
    }

    return make_request(data)[1]

def retrieve_page(title):
    data = {
        "action" : "parse",
        "prop" : "wikitext",
        "format" : "json",
        "page" : title
    }

    return make_request(data)["parse"][data["prop"]]["*"]

def main():
    while 1:
        query = input("enter search term:\n> ")
        results = search(query)
        found = None

        if query == results[0]: # perfect match
            found = results[0]
        else:
            print("found results:")
            for i in range(len(results)):
                print(f"{i}:\t{results[i]}")

            while found == None:
                try:
                    found = results[int(input("> "))]
                except:
                    pass

        page = retrieve_page(found)

        print("page:")
        print(page)

if __name__ == "__main__":
    main()
