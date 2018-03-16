import requests
import json


def xml_requester(unam_variant, year, start_record) -> str:
    """
    This function make and send a request to the xml api (SRU standard) of library of congress
    :param unam_variant: A variant of UNAM name
    :param year: Year of publications
    :param start_record: The first record per XML page
    :return: XML code as string
    """
    base = 'http://lx2.loc.gov:210/lcdb?version=1.2&operation=searchRetrieve&'
    query = 'query="' + unam_variant + '" AND dc.date=' + year + '&startRecord=' + start_record + \
            '&maximumRecords=100&recordSchema=dc'
    url = base + query
    r = requests.get(url)
    return r.content


def json_requester(query="universidad nacional autonoma de mexico", scope="/search/?") -> dict:
    """ This function make and send a general request to the library
    Parameters
    ----------
    query: the field that we are interested. By default "universidad nacional autonoma de mexico"
    scope: the scope of the search on the www.loc.gov website. By default "/search/? (everything)"

    Returns
    -------
    dict: A dictionary with response data
    """
    base_url = "https://www.loc.gov/" \
               + scope \
               + "q=" + query \
               + "&all=true&fo=json"  # all=true for online and physical resources

    r = requests.get(base_url)
    response = json.loads(r.text)

    return response

