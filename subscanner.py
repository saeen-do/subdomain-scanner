#!/usr/bin/python3

from argparse import ArgumentParser, FileType
from threading import Thread, Lock
from requests import get, exceptions
from time import time

subdomains = []
lock = Lock()

def prepare_args():
    """ Prepare arguments and parse them.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = ArgumentParser(description="PYTHON BASED FAST SUBDOMAIN FINDER",
                            usage="%(prog)s example.com",
                            epilog="%(prog)s -w /path/to/wordlist -t 500 -V google.com")

    parser.add_argument(metavar="domain", dest="domain", help="domain name")
    parser.add_argument("-w", "--wordlist", dest="wordlist",
                        metavar="", type=FileType("r"),
                        help="wordlist of subdomains", default="wordlist.txt")
    parser.add_argument("-t", "--threads", dest="threads",
                        metavar="", type=int, help="threads to be used", default=500)
    parser.add_argument("-V", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("-v", "--version", action="version", help="print version", version="%(prog)s 1.0")
    
    return parser.parse_args()

def prepare_words(wordlist):
    """Generator function for words

    Args:
        wordlist (file): File object containing words

    Yields:
        str: Next word from the wordlist
    """
    words = wordlist.read().split()
    for word in words:
        yield word

def check_subdomain(domain, words, verbose):
    """Check subdomain for status 200

    Args:
        domain (str): The domain to check subdomains for
        words (generator): Generator object for words
        verbose (bool): Flag for verbose output
    """
    global subdomains
    while True:
        try:
            word = next(words)
            url = f"https://{word}.{domain}"
            request = get(url, timeout=5)
            if request.status_code == 200:
                with lock:
                    subdomains.append(url)
                if verbose:
                    print(url)
        except (exceptions.ConnectionError, exceptions.ReadTimeout):
            continue
        except StopIteration:
            break

def prepare_threads(domain, words, threads, verbose):
    """Create, start and join threads

    Args:
        domain (str): The domain to check subdomains for
        words (generator): Generator object for words
        threads (int): Number of threads to use
        verbose (bool): Flag for verbose output
    """
    thread_list = []
    for _ in range(threads):
        thread = Thread(target=check_subdomain, args=(domain, words, verbose))
        thread_list.append(thread)
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

if __name__ == "__main__":
    arguments = prepare_args()
    words = prepare_words(arguments.wordlist)
    start_time = time()
    prepare_threads(arguments.domain, words, arguments.threads, arguments.verbose)
    end_time = time()

    print("Subdomains found -\n" + "\n".join(i for i in subdomains))
    print(f"Total subdomains found: {len(subdomains)}")
    print(f"Time taken - {round(end_time - start_time)} seconds")
