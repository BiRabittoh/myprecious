from igdb.wrapper import IGDBWrapper
from urllib.parse import urlencode
from contextlib import suppress
import Constants as c
import requests
import os, json

def get_token():
    if None in [ c.CLIENT_ID, c.CLIENT_SECRET ]:
        print("Please check your .env file.")
        exit(1)
    url = f"{ c.AUTH_URL }?{ urlencode(c.AUTH_URL_PARAMS) }"
    response = requests.request("POST", url).json()
    return response['access_token']

def construct_wrapper(token):
    return IGDBWrapper(c.CLIENT_ID, token)

def get_wrapper():
    with suppress(FileExistsError):
        os.makedirs(c.BASE_DIRECTORY)
    try:
        with open(c.TOKEN_PATH, "r", encoding="utf-8") as in_file:
            token = in_file.readline()
        # we got a token, it may be expired
        w = construct_wrapper(token)
        try:
            w.api_request("games", "limit 1;")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("Invalid token. Getting a new one.")
                raise FileNotFoundError
            print("API connection error.")
            exit(1)
        return w # valid token
    except FileNotFoundError:
        # invalid or missing token
        token = get_token()
        with open(c.TOKEN_PATH, "w", encoding="utf-8") as out_file:
            out_file.write(token)
        return construct_wrapper(token)

def req(endpoint, query):
    result_bs = wrapper.api_request(endpoint, query)
    result_str = result_bs.decode("utf-8")
    return json.loads(result_str)

def search_game(query: str):
    cleaned_up_query = query.replace('"', '').replace("'","")
    return req("games", f'search "{ cleaned_up_query }"; fields *, cover.*, platforms.*;')

wrapper = get_wrapper()
