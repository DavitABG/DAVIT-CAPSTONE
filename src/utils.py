import importlib
import json
import pickle
import random
import string
from argparse import ArgumentParser
from pathlib import Path
from typing import Union, Dict

from fastapi.openapi.utils import get_openapi


def generate_guid(k: int = 6):
    """
    Generate random id

    Parameters
    ----------

    k : int
        length of guid
    Returns
    -------
    guid : str
        random id
    """

    guid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=k))
    return guid


def pickle_save(path: Union[str, Path], obj: Dict):
    """
    Save supported files in pickle format
    Parameters
    ----------
    path : str
        path to save object
    obj : object
        any pickle serializable object

    Returns
    -------
    """
    with open(path, 'wb') as file:
        pickle.dump(obj, file)


def pickle_load(path: Union[str, Path]):
    """
    Load supported pickle format files
    Parameters
    ----------
    path : str
        path to save object

    Returns
    -------
    obj : (Object)
        any object with any pickle supported format
    """

    with open(path, 'rb') as file:
        obj = pickle.load(file)

        return obj


def json_load(path: Union[str, Path], encoding: str = 'utf-8'):
    """
    Load json files from path
    Parameters
    ----------
    path : str
        path to save object
    encoding : str
        encoding type

    Returns
    -------
    obj : (Object) object

    """
    with open(path, 'r', encoding=encoding) as file:
        obj = json.load(file)
        return obj


def json_save(path: Union[str, Path], obj: Dict):
    """
    Save supported files to json format
    Parameters
    ----------
    path : str
        path to save object
    -------
    obj : (Object) object

    Returns
    ---------
    """
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(obj, file)


def generate_openapi_json(openapi_version="3.1.0"):
    """
    Generate and save openapi specification of the application

    Parameters
    ----------
    openapi_version : str
        openapi version specifier

    Returns
    -------
    None
    """
    parser = ArgumentParser()
    parser.add_argument('--app_path')
    parser.add_argument('--server_url', default='0.0.0.0:8000')
    args = parser.parse_args()
    app_path = args.app_path
    server_url = args.server_url
    module = importlib.import_module(app_path)
    app = module.app

    openapi_json = get_openapi(
        title=app.title,
        openapi_version=openapi_version,
        version=app.version,
        description=app.description,
        routes=app.routes,
        servers=[{'url': server_url}]
    )
    json_save('openapi.json', openapi_json)


if __name__ == '__main__':
    generate_openapi_json(openapi_version='3.1.0')
