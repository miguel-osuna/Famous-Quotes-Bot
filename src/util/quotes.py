import os
import requests

QUOTES_API_URL = os.getenv("QUOTES_API_URL")


class URLs:
    def __init__(self):
        self.base = QUOTES_API_URL
        self.api_version = "/api/v1"

        # Quotes
        self.quote = "/quote"
        self.quotes = "/quotes"
        self.random_quote = "/quotes/random"

        # Author
        self.authors = "/authors"

        # Tags
        self.tags = "/tags"

    def base_url(self):
        """ Returns the api base url. """
        return self.base + self.api_version

    def quote_url(self):
        """ Returns the api quote resource url. """
        return self.base + self.api_version + self.quote

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


class QuotesApi:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = URLs()

    def __create_auth(self):
        """ Creates authentication headers for api key. """
        headers = {
            "Authorization": "Bearer {}".format(self.api_key),
            "Content-Type": "application/json",
        }

        return headers

    def __get_data(self, url):
        """ Private method that performs a get request. """
        headers = self.__create_auth()

    def __post_data(self, url):
        """ Private method that performs a post request. """
        headers = self.__create_auth()

    def __put_data(self, url):
        """ Private method that performs a put request. """
        headers = self.__create_auth()

    def __patch_data(self, url):
        """ Private method that performs a patch request. """
        headers = self.__create_auth()

    def __delete_data(self, url):
        """ Private method that performs a delete request. """
        headers = self.__create_auth()

