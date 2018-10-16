import csv
import urllib3
import datetime
import requests.exceptions as requests_exec
from typing import Iterable, Any
from pyppeteer.errors import ElementHandleError, NetworkError
from requests_html import HTMLSession, MaxRetries, HTMLResponse
from fake_useragent import UserAgent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Crawl:
    __slots__ = ['session', 'proxies_priority', 'stats', 'user_agent']

    def __init__(self) -> None:
        self.session = HTMLSession()
        self.proxies_priority = {}
        self.user_agent = UserAgent(verify_ssl=False)
        self.stats = {
            'start': datetime.datetime.now(),
        }

    def load_proxies(self, path: str = 'proxies.txt') -> bool:
        """Load proxies from file

        :param path: path to proxies file
        :type path: str

        :return bool
        """
        try:
            with open(path, 'r') as fp:
                self.proxies_priority = { proxy.replace('\n', ''): 0 for proxy in fp.readlines()}

            return True
        except FileNotFoundError:
            print('[*] No proxies file found!')
            return False

    def _rotate_proxies(self) -> sorted:
        """Rotates proxies and sort them by priority

        :return sorted function to be run
        """
        return sorted(self.proxies_priority.items(), key=lambda kv: kv[1])[0][0]

    def _get_proxy(self) -> [str, None]:
        """Get proxy from sorted dict of proxies

        :return str or None
        """
        try:
            rotated = self._rotate_proxies()
        except (ValueError, KeyError, IndexError):
            rotated = None

        return rotated

    def get(self, url: str, tor_proxy: bool = False) -> [HTMLResponse, None]:
        """Makes a GET request and returs the response. It handles proxies, exceptions and retries.

        :param url: URL to be fetched
        :type url: str

        :param tor_proxy: Flag to redirect traffic through Tor port
        :type tor_proxy: bool

        :return HTMLResponse
        """
        if tor_proxy:
            proxies = {
                'http':  'socks5h://127.0.0.1:9050',  # TOR sockets
                'https': 'socks5h://127.0.0.1:9050'
            }
        else:
            proxies = self._get_proxy()

        retries = 3
        response = None
        while retries:
            try:
                elapsed_time = str(datetime.datetime.now() - self.stats["start"])
                print(f'[*] Fetching: {url} | '
                      f'Retry: {retries} | '
                      f'Elapsed time: {elapsed_time}')
                response = self.session.get(
                    url,
                    timeout=(10.0, 30.0),
                    headers=self.get_headers(),
                    verify=False,
                    proxies=proxies
                )
                if all([
                    isinstance(proxies, str), proxies, proxies in self.proxies_priority, response.status_code == 200
                ]):
                    self.proxies_priority[proxies] += 1

                if response.ok:
                    return response
                else:
                    retries -= 1

            except requests_exec.RequestException:
                print('[*] An exception has occurred while fetching the URL')
                if isinstance(proxies, str) and proxies and proxies in self.proxies_priority:
                    self.proxies_priority[proxies] -= 1
                proxies = self._get_proxy()
                retries -= 1
                continue

        return response
    def parse_js(self, response: HTMLResponse, look_up: [str, None, Iterable] = None, js_script: str = '') -> Any:
        """Parses rendered HTML and returns the evaluation of JS script

        :param response: GET request response
        :type response: HTMLResponse

        :param look_up: Lookup condition to run JS script
        :type look_up: str or None or Iterable

        :param js_script: JS script to be run
        :type js_script: str

        :return: Any
        """
        not_found = f'Not found {js_script}'.strip()

        if not response:
            return not_found

        rendered = None
        if js_script and self._look_up_in_content(response.content, look_up):
            rendered = self._render_JS(response, js_script)
        elif js_script:
            rendered = self._render_JS(response, js_script, retries=0)

        if not rendered:
            return not_found
        else:
            return rendered

    def _render_JS(self, response: HTMLResponse, js_script: str, retries: int = 4) -> Any:
        """

        :param response: GET response
        :type response: HTMLResponse

        :param js_script: JS script to be run
        :type js_script: str

        :param retries: Number of rendering retries
        :type retries: int

        :return: Any
        """
        try:
            rendered = response.html.render(script=js_script, retries=retries)
        except (MaxRetries, NetworkError, ElementHandleError):
            print('[*] An exception has occurred while rendering the HTML')
            return
        else:
            return rendered

    def _look_up_in_content(self, content: bytes, look_up: [str, None, Iterable]) -> bool:
        """Method to look up for strings inside content. It helps define whether a certain JS file is available

        :param content: content string
        :type content: bytes

        :param look_up: Lookup condition to run JS script
        :type look_up: str or None or Iterable

        :return bool
        """
        if isinstance(look_up, str):
            if bytes(look_up, encoding='utf8') in content:
                return True
        elif isinstance(look_up, (tuple, list)):
            for look in look_up:
                if bytes(look, encoding='utf8') in content:
                    return True
        else:
            return False

    @staticmethod
    def save_two_columns_csv(evaluated: str, content: Any, file_name: str = 'results.csv') -> None:
        """Saves two columns of information into a csv file

        :param evaluated: JS function that was evaluated
        :type evaluated: str

        :param content: content from JS evaluated function
        :type content: Any
        """
        with open(file_name,'a+') as result_file:
            wr = csv.writer(result_file, delimiter=',')
            wr.writerow([evaluated, content])

    def get_headers(self) -> dict:
        """Returns fake headers
        :return dict
        """
        return {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Cache-Control': 'no-cache',
        }