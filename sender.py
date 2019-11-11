import dns.resolver
import requests
from shared.packet_reader import PktReader


resolvers = ["https://dns.adguard.com", "https://dns.google",
             "https://cloudflare-dns.com/dns-query", "https://dns.quad9.net/dns-query",
             "https://doh.opendns.com/dns-query", "https://doh.cleanbrowsing.org/doh/family-filter/"]

reader = PktReader(write_mode='raw', out_file="test.txt", pkt_filter='port 443')
reader.start()
resolver = dns.resolver.Resolver(configure=False)
resolver.nameservers = ["1.1.1.1"]
resolver.port = 443
try:
    answers = resolver.query("dl.dns-lab.org.", "A", transport='https', https_method='GET', lifetime=3, raise_on_no_answer=False)
except Exception:
    pass

print("sent doh")

res = requests.get("https://google.com")

print("sent get")
reader.stop()

