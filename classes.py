import csv
import urllib3
import datetime
import requests.exceptions as requests_exec
from pyppeteer.errors import ElementHandleError, NetworkError
from requests_html import HTMLSession, MaxRetries
from fake_useragent import UserAgent

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Crawl:
    __slots__ = ['session', 'proxies_priority', 'stats', 'user_agent']

    def __init__(self):
        self.session = HTMLSession()
        self.proxies_priority = {}
        self.user_agent = UserAgent(verify_ssl=False)
        self.stats = {
            'start': datetime.datetime.now(),
        }

    def load_proxies(self, path: str = 'proxies.txt') -> bool:
        try:
            with open(path, 'r') as fp:
                self.proxies_priority = { proxy.replace('\n', ''): 0 for proxy in fp.readlines()}

            return True
        except FileNotFoundError:
            print('[*] No proxies file found!')
            return False

    def _rotate_proxies(self) -> sorted:
        return sorted(self.proxies_priority.items(), key=lambda kv: kv[1])[0][0]

    def _get_proxy(self) -> [str, None]:
        try:
            rotated = self._rotate_proxies()
        except (ValueError, KeyError, IndexError):
            rotated = None

        return rotated

    def get(self, url: str, js_script: str ='', render: bool = False, tor_proxy: bool = False) -> [str, None]:
        if tor_proxy:
            proxies = {
                'http':  'socks5h://127.0.0.1:9050',  # TOR sockets
                'https': 'socks5h://127.0.0.1:9050'
            }
        else:
            proxies = self._get_proxy()

        retries = 3
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
                if isinstance(proxies, str) and proxies and proxies in self.proxies_priority:
                    self.proxies_priority[proxies] += 1

                if render and js_script:
                    try:
                        response.html.render(retries=0, script=js_script, reload=False)
                    except (MaxRetries, NetworkError):
                        retries -= 1
                        continue
                    except ElementHandleError:
                        return 'pbjs not found'

                content = response.content
                if not content:
                    return 'pbjs not found'
                else:
                    return content

            except requests_exec.RequestException:
                print('[*] An exception has occurred while fetching the URL')
                if isinstance(proxies, str) and proxies and proxies in self.proxies_priority:
                    self.proxies_priority[proxies] -= 1
                proxies = self._get_proxy()
                retries -= 1
                continue

    @staticmethod
    def save_csv(evaluated, content, file_name='results.csv'):
        with open(file_name,'a+') as result_file:
            wr = csv.writer(result_file, delimiter=',')
            wr.writerow([evaluated, content])

    def get_headers(self):
        return {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Cache-Control': 'no-cache',
        }