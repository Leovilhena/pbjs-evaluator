import traceback
from io import BytesIO
from typing import Generator
from zipfile import ZipFile, BadZipFile

class TimeoutError(Exception):
    def __init__(self, value):
        self.value = value

def _handle_timeout(signum, frame):
    raise TimeoutError('[*] Request timed out')

def unzip_request_content(content: [str, bytes]) -> [ZipFile, None]:
    if not content:
        return

    try:
        unzipped_file = ZipFile(BytesIO(content))
        return unzipped_file
    except BadZipFile:
        traceback.print_exc(limit=1)

def parse_row(unzipped_file: ZipFile) -> [str, None]:
    if not unzipped_file:
        return

    for file in unzipped_file.namelist():
        for row in unzipped_file.open(file).readlines():
            yield row.decode()

def parse_url(raw_url: [str, Generator[str, int, bytes]]) -> [str, None]:
    if not raw_url:
        return

    try:
        if not isinstance(raw_url, str):
            raw_url = next(raw_url)

        row, url = raw_url.split(',')
        return url.replace('\n', '')
    except (UnicodeDecodeError, ValueError):
        traceback.print_exc(limit=1)