
def get_text_search_query(key, value):
    return {
        "query_string": {
            "query": f"{key}:{value}*"
        }
    }

def get_number_search_query(key, value):
    return {
        "query_string": {
            "query": f"{key}:{value}"
        }
    }
