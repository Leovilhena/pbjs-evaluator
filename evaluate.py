from classes import Crawl
from helpers import unzip_request_content, parse_row, parse_url


def main():
    zipfile_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

    crawler = Crawl()
    content = crawler.get(zipfile_url)
    unzipped_file = unzip_request_content(content)
    count = 0
    for row in parse_row(unzipped_file):
        url = 'https://' + parse_url(row).strip()

        if not url:
            continue
        elif count >= 10000:
            break

        js_function = 'pbjs.cbTimeout'
        evaluated = crawler.get(url, js_function, render=True, tor_proxy=True)
        print(f'[*] pbjs.cbTimeout Evaluation: {evaluated}')
        crawler.save_csv(url, evaluated, 'results.json')


if __name__ == "__main__":
    print('[*] Starting script...')
    main()