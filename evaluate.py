from classes import Crawl
from helpers import unzip_request_content, parse_row, parse_url


def main():
    zipfile_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

    crawler = Crawl()
    response = crawler.get(zipfile_url)
    unzipped_file = unzip_request_content(response.content)
    count = 0
    for row in parse_row(unzipped_file):
        url = 'https://' + parse_url(row).strip()

        if not url:
            continue
        elif count >= 10000:
            break

        js_function = 'pbjs.cbTimeout'
        response = crawler.get(url, tor_proxy=False)
        evaluated = crawler.parse_js(response, look_up=('pbjs', 'prebid'), js_script=js_function)
        print('[*]', evaluated)
        crawler.save_two_columns_csv(url, evaluated, 'results.json')


if __name__ == "__main__":
    print('[*] Starting script...')
    main()