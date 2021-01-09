import os
import requests

from config import QUOTES_API_URL


class URLs:
    def __init__(self):
        self.base = QUOTES_API_URL
        self.api_version = "/api/v1"

        # Quotes
        self.quotes = "/quotes"
        self.random_quote = "/quotes/random"

        # Author
        self.authors = "/authors"

        # Tags
        self.tags = "/tags"

    def base_url(self):
        """ Returns the api base url. """
        return self.base + self.api_version

    def quotes_url(self):
        """ Returns the api quotes resources url. """
        return self.base + self.api_version + self.quotes

    def random_quote_url(self):
        """ Returns the api random quote resource url. """
        return self.base + self.api_version + self.random_quote

    def authors_url(self):
        """ Returns the api authors resources url. """
        return self.base + self.api_version + self.authors

    def tags_url(self):
        """ Returns the api tags resources url. """
        return self.base + self.api_version + self.tags


class BearerAuth(requests.auth.AuthBase):
    """ Custom authentication class for Quotes API. """

    def __init__(self, token):
        self.token = token

    def __call__(self, req):
        req.headers["Authorization"] = "Bearer " + self.token
        return req


class QuotesApi:
    """ Quotes API Wrapper. """

    def __init__(self, api_key):
        self.api_key = api_key
        self.url = URLs()

    def __get_data(self, url, payload=None):
        """ Private method that performs a get request. """

        if payload is not None:
            return requests.get(url, auth=BearerAuth(self.api_key), params=payload)
        else:
            return requests.get(url, auth=BearerAuth(self.api_key))

    def __put_data(self, url, data):
        """ Private method that performs a put request. """
        return requests.put(url, json=data, auth=BearerAuth(self.api_key))

    def __patch_data(self, url, data):
        """ Private method that performs a patch request. """
        return requests.put(url, json=data, auth=BearerAuth(self.api_key))

    def __delete_data(self, url):
        """ Private method that performs a delete request. """
        return requests.delete(url, auth=BearerAuth(self.api_key))

    def __post_data(self, url, data):
        """ Private method that performs a post request. """
        return requests.post(url, json=data, auth=BearerAuth(self.api_key))

    def get_quote(self, quote_id, query_params=None):
        """ Get quote resource by id. """
        quotes_url = self.url.quotes_url() + f"/{quote_id}"
        return self.__get_data(quotes_url, query_params)

    def put_quote(self, quote_id, data):
        """ Update quote resource by id. """
        quotes_url = self.url.quotes_url() + f"/{quote_id}"
        return self.__put_data(quotes_url, data)

    def patch_quote(self, quote_id, data):
        """ Patch quote resource by id. """
        quotes_url = self.url.quotes_url() + f"/{quote_id}"
        return self.__patch_data(quotes_url, data)

    def delete_quote(self, quote_id):
        """ Delete quote resource by id. """
        quotes_url = self.url.quotes_url() + f"/{quote_id}"
        return self.__delete_data(quotes_url)

    def post_quote(self, data):
        """ Creates quote resource. """
        quotes_url = self.url.quotes_url()
        return self.__post_data(quotes_url, data)

    def get_random_quote(self, query_params=None):
        """ Get random quote resource. """
        quotes_url = self.url.random_quote_url()
        return self.__get_data(quotes_url, query_params)

    def get_all_quotes(self, query_params=None):
        """ Get list of quote resources. """
        quotes_url = self.url.quotes_url()
        return self.__get_data(quotes_url, query_params)

    def get_all_authors(self, query_params=None):
        """ Get list of author resources. """
        authors_url = self.url.authors_url()
        return self.__get_data(authors_url, query_params)

    def get_all_tags(self):
        """ Get list of tag resources. """
        tags_url = self.url.tags_url()
        return self.__get_data(tags_url)

