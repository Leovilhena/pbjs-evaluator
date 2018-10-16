import os
import io
import csv
from zipfile import ZipFile
from requests_html import HTMLSession
from fake_useragent import UserAgent
from helpers import unzip_request_content, parse_row, parse_url


# Tests functions and configuration

def create_testfiles(csv_entry, proxies):
    with open("./tests/test.csv",'w+') as result_file:
        wr = csv.writer(result_file, dialect=csv.Dialect.delimiter)
        wr.writerow(csv_entry.split(','))

    with ZipFile('./tests/test.zip', 'w') as my_zip:
        my_zip.write('./tests/test.csv')

    with open("./proxies_test.txt",'w+') as result_file:
        for proxy in proxies:
            result_file.write(proxy + '\n')

def clean_testfiles():
    try:
        os.remove('./tests/test.zip')
        os.remove('./tests/test.csv')
        os.remove('./proxies_test.txt')
        os.remove('./results.csv')
    except OSError:
        print("[*] Test files weren't removed during tests!")

def setup_module():
    create_testfiles('1,testing', ['123.123.123.123:80:user:password', '456.456.456.456:80:user:password'])

def teardown_module():
    clean_testfiles()


# Tests unit
def test_unzip_request_content():
    assert not unzip_request_content(b'')

    with io.open('./tests/test.zip', 'rb') as fp:
        unzipped = unzip_request_content(fp.read())
        assert isinstance(unzipped, ZipFile)

def test_parse_row(csv_entry):

    with io.open('./tests/test.zip', 'rb') as fp:
        unzipped = unzip_request_content(fp.read())

    parsed_row = next(parse_row(unzipped)).replace('\r\n', '')

    assert parsed_row == csv_entry

def test_parse_url(result_url_str):
    with io.open('./tests/test.zip', 'rb') as fp:
        unzipped = unzip_request_content(fp.read())

    parsed_row = next(parse_row(unzipped)).replace('\r\n', '')
    parsed_result = parse_url(parsed_row)

    assert parsed_result == result_url_str

def test_crawl_obj(crawl_obj):
    assert crawl_obj
    assert isinstance(crawl_obj.session, HTMLSession)
    assert not crawl_obj.proxies_priority
    assert isinstance(crawl_obj.user_agent, UserAgent)

    assert isinstance(crawl_obj.get_headers(), dict)
    assert not crawl_obj.load_proxies('')
    assert crawl_obj.load_proxies('./proxies_test.txt')
    assert crawl_obj.proxies_priority

    crawl_obj.proxies_priority = {}
    assert crawl_obj.get('https://www.rtbhouse.com')

    crawl_obj.save_two_columns_csv('test', 'test')
    assert os.path.isfile('results.csv')

    with open('results.csv', 'r') as fp:
        assert fp.read()

    assert crawl_obj.parse_js(None) is 'Not found'
