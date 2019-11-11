import argparse
import multiprocessing as mp
import signal
import dns.resolver
import dns.exception
from tqdm import tqdm


def get_ip(domain: str):
    """
    gets the first IPv4 address for the given domain

    :returns None if lookup failed, else a string of ``domain ip``
    """
    domain = domain.strip()
    try:
        for i in range(total_tries):
            results = resolver.query(domain, "A", raise_on_no_answer=False, lifetime=5)
            if len(results) > 0:
                return [str(r) for r in results]
        return None
    except Exception as ex:
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('input', help="Input file of doh resolver domains", type=argparse.FileType('r'))
    parser.add_argument('-r', '--resolver', help="The resolver to use for queries. Default is google",
                        default='8.8.8.8')
    parser.add_argument('-n', '--num-tries', help="The number of total times to try a query if NoAnswer is received. "
                                                  "Default is 3", type=int, default=3)
    parser.add_argument('-t', '--threads', help="Number of parallel threads to query with. Default is 100",
                        type=int, default=10)

    args = parser.parse_args()

    total_tries = args.num_tries
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [args.resolver]
    resolver.port = 53

    domains = args.input.readlines()
    domains = list(set(domains))  # remove dupes

    ips = set()

    print("Starting queries...")
    with mp.Pool(processes=args.threads, initializer=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)) as p:
        try:
            for results in tqdm(p.imap_unordered(get_ip, domains), total=len(domains), unit="domains", position=0):
                if results is not None:
                    for r in results:
                        ips.add(r)
        except KeyboardInterrupt:
            p.terminate()
            p.join()
            print("Exiting early from queries.")

    print("\n[", end="")
    for i, ip in enumerate(ips):
        print(f'"{ip}"', end="")
        if i < len(ips) - 1:
            print(", ", end="")
    print(']')
