import argparse
import dns.message
import dns.exception
import base64
import requests
import urllib3

# verification is lame
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_doh(resolver, query):
    headers = {"accept": "application/dns-message", 'host': resolver}
    msg = dns.message.make_query(query, dns.rdatatype.from_text('TXT')).to_wire()
    msg = base64.urlsafe_b64encode(msg).decode('utf-8').strip("=")
    payload = {"dns": msg}
    url = "https://{}/dns-query".format(resolver)
    try:
        res = requests.get(url, params=payload, headers=headers, timeout=3, verify=False)
        ans = dns.message.from_wire(res.content)
        if len(ans.answer) > 0:
            return True

    except Exception as e:
        print(e)
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('input', help="Input file of doh resolver domains", type=argparse.FileType('r'))
    parser.add_argument('output', help="Output file of responding doh resolver domains", type=argparse.FileType('w'))
    args = parser.parse_args()

    domains = args.input.readlines()
    domains = list(set(domains))  # remove dupes

    for d in domains:
        d = d.strip()
        works = get_doh(d, 'example.com')
        print(f"{d}  {works}")
        if works:
            args.output.write(d + '\n')
