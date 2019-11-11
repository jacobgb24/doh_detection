import argparse
from tqdm import tqdm

bad_words = ["porn", "xxx", "xnxx", "anal", "anus", "ass", "bitch", "boner", "boob", "clitoris", "cock", "cunt", "damn",
             "dick", "dildo", "fap", "fuck", "jerk", "jizz", "labia", "milf", "penis", "pussy", "queer", "scrotum",
             "sex", "shit", "slut", "tit", "vagina", "wank", "whore", "gay", "lesbian", "hentai", "babe", "nude",
             "sperm", "nipple", "ebony"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('input', help="Input file of alexa sites", type=argparse.FileType('r'))
    parser.add_argument('filter', help="Filter file containing a list of domains to remove", type=argparse.FileType('r'))
    parser.add_argument('output', help="Output file to write results to", type=argparse.FileType('w'))
    parser.add_argument('-n', '--num-domains', help="The number of domains to output", type=int, default=300000)
    args = parser.parse_args()

    print("Filtering out bad sites...")
    raw_domains = args.input.readlines()
    domains = []
    domain_filter = args.filter.readlines()
    pbar = tqdm(total=args.num_domains, desc="Clean sites")
    for site in raw_domains:
        if site not in domain_filter and not any(k in site for k in bad_words):
            domains.append(site)
            pbar.update()
            if len(domains) >= args.num_domains:
                break

    for d in domains:
        args.output.write(d)
