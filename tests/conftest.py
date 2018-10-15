import pytest
from classes import Crawl

@pytest.fixture()
def csv_entry():
    return '1,testing'

@pytest.fixture()
def result_url_str():
    return 'testing'

@pytest.fixture()
def crawl_obj():
    return Crawl()

@pytest.fixture()
def proxies():
    return ['123.123.123.123:80:user:password', '456.456.456.456:80:user:password']
