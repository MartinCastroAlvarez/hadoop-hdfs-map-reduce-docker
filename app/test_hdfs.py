"""
Python script that tests writing data into HDFS.

Referneces:
- https://stackoverflow.com/questions/47926758/python-write-to-hdfs-file
"""

import json
import random
import socket
import string

from typing import Dict, List, Tuple

import requests
from urllib3.util import connection

from hdfs import InsecureClient

characters: List[str] = string.ascii_letters + string.digits

NAMENODE_HOST: str = 'localhost'
NAMENODE_PORT: int = 9870
NAMENODE_URL: str = f'http://{NAMENODE_HOST}:{NAMENODE_PORT}'
HDFS_URL: str = f'{NAMENODE_URL}/webhdfs/v1/'
USER: str = 'martin'

records: List[Dict] = [
    {'name': 'foo', 'weight': 1},
    {'name': 'bar', 'weight': 2},
]

_orig_create_connection = connection.create_connection


def patched_create_connection(address: Tuple, *args, **kwargs) -> socket.socket:
    """
    We have to override the DNS entries because hitting one container using
    the Python requests library with a 307 response redirect from the Namenode
    indicating the hostname of the Datanode to send the write request results in
    Python trying to hit a container by Container ID instead of by hostname, which
    should be localhost. In addition, we don't want to update the DNS configuration
    of the host since this is just a test, so we mock the DNS resolver of the urllib3
    library.
    """
    hostname, port = address
    if hostname != 'localhost':
        print(f'WARNING: Replacing {hostname} with localhost.')
        hostname: str = 'localhost'
    return _orig_create_connection((hostname, port), *args, **kwargs)

connection.create_connection = patched_create_connection

client: InsecureClient = InsecureClient(NAMENODE_URL, user=USER)

total_words: int = 0
total_files: int = 0
total_chars: int = 0
for total_files in range(random.randint(0, 1000)):
    doc_id: int = random.randint(1, 10000)
    file_name: str = f'doc-{doc_id}.txt'
    words: int = random.randint(0, 1000)
    total_words += words
    print(doc_id, words, 'words')
    text: list = []
    for word in range(words):
        length: int = random.randint(1, 10)
        total_chars += length
        text.append(''.join(random.choice(characters) for i in range(length)))
    with client.write(file_name, overwrite=True, encoding='utf-8') as writer:
        writer.write(' '.join(text))

for file_ in client.list(f'/user/{USER}/'):
    print(file_)

print('Written:', total_files, 'files', total_words, 'words', total_chars, 'chars')
