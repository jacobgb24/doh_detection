import requests
import argparse
import random
from shared.packet_reader import PktReader
import logging
from tqdm import tqdm
import urllib3
import dns.message
import base64
from requests_toolbelt.adapters import source
import multiprocessing as mp
import signal
import time

# verification is lame
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_doh(resolver, query):
    headers = {"accept": "application/dns-message", 'host': resolver}
    msg = dns.message.make_query(query, dns.rdatatype.from_text('TXT')).to_wire()
    msg = base64.urlsafe_b64encode(msg).decode('utf-8').strip("=")
    payload = {"dns": msg}
    url = "https://{}/dns-query".format(resolver)
    session.get(url, params=payload, headers=headers, timeout=3, verify=False, allow_redirects=False)


def send_query(d):
    try:
        domain = d["domain"]
        if d["type"] == "web":
            session.get(f"https://{domain}", timeout=3, headers={"host": domain}, verify=False, allow_redirects=False)
            logging.warning(f"{d['type']} {d['num']:04d}: {domain}")

        else:
            resolver = d["resolver"]
            get_doh(resolver, domain)
            logging.warning(f"{d['type']} {d['num']:04d}: {domain} (via {resolver})")
        return True
    except Exception as e:
        logging.error(f"{d['type']} {d['num']:04d}:  FAILED - {type(e).__name__} {d['domain']}  ({d['resolver']})")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('domains', help="Input file of domains to query for", type=argparse.FileType('r'))
    parser.add_argument('resolvers', help="Input file of doh resolvers", type=argparse.FileType('r'))
    parser.add_argument('output', help="Output file name (appended with .pcap and .log)", type=str)
    parser.add_argument('ip', help="IP queries will go out from for filtering")
    parser.add_argument('-n', '--num-samples', help="The number of samples to collect (of each web and doh)",
                        type=int, default=10000)
    parser.add_argument('-t', '--threads', help="Number of parallel threads to send queries from", type=int, default=25)
    args = parser.parse_args()

    domains = args.domains.readlines()
    resolvers = args.resolvers.readlines()

    logging.basicConfig(level=logging.WARNING, filename=f"{args.output}.log", filemode='w',
                        format="%(asctime)s:  %(message)s")
    reader = PktReader(write_mode='file', out_file=f"{args.output}.pcap",
                       pkt_filter=f'host {args.ip} and tcp port 443', interface="ens33", unique_out_file_name=False)
    reader.start()

    # send traffic out specified IP for filtering
    session = requests.Session()
    s = source.SourceAddressAdapter(args.ip)
    session.mount('http://', s)
    session.mount('https://', s)

    queries = []

    print("Generating queries...")
    for i in range(args.num_samples):
        web_args = {"num": i, "type": "web", "domain": random.choice(domains).strip(), "resolver": ""}
        doh_args = {"num": i, "type": "doh", "domain": random.choice(domains).strip(),
                    "resolver": random.choice(resolvers).strip()}
        if random.random() < 0.5:
            queries.append(web_args)
            queries.append(doh_args)
        else:
            queries.append(doh_args)
            queries.append(web_args)

    print("Sending queries...")
    with mp.Pool(processes=args.threads, initializer=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)) as p:
        try:
            for _ in tqdm(p.imap_unordered(send_query, queries), total=len(queries), unit="query"):
                pass

        except KeyboardInterrupt:
            p.terminate()
            p.join()
            print("Exiting early from queries.")

    reader.stop()
