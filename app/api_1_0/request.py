import requests
from .exceptions import FileNotFound, ConnectionError
from ..helper import get_env_var

"""Send a get request to server to retrieve a file.

@param file_id
    The name of the filei without extension.
@return
    The path to the requested file.
"""
def get_file(file_id, ext=".mp4"):
    host = get_env_var('VIDEOMAN_HOST')
    port = get_env_var('VIDEOMAN_PORT')
    uri = '%s:%s/videos/%s'
    print (uri % (host, port , file_id+ext))
    try:
        r = requests.get(uri % (host, port, file_id+ext))
    except:
        raise ConnectionError('Connection refused. Cache service running?')

    """GET request returns empty string if download fails or invalid uri."""
    if not r.text:
        raise FileNotFound('Invalid URI or file "%s" was not found on file hosting server.' %
                           file_id)
    return r.text

