# collection of helper functions to keep things modular and easily testable
#

from urllib import parse



# FIXME this needs a unit test or three...
def is_valid_url(url):
    """
    helper that returns a bool indicating whether or not what the caller submitted is a valid url
    :param url:
    :return:
    """
    parsed_url = parse(url)

    # this is a shitty way to do this...
    is_valid = True

    if parsed_url.scheme != "http" or parsed_url.scheme != "https":
        is_valid = False

    if parsed_url.hostname == None:
        is_valid = False

    return is_valid