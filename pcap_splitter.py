import os
import argparse
import shlex
import subprocess as sp
import shutil
from tqdm import tqdm
import re

# anonymize pcap IP addresses
# tcpprep -i edns.pcap -o input.cache -p
# tcprewrite -i edns.pcap -e 192.0.0.1:192.0.0.2 -o edns-anon.pcap -c input.cache
# rm input.cache

dst_regex = re.compile(r'(?<=> ).+?(?=.\d+:)')


def get_destination(filepath):
    get_line = sp.Popen(shlex.split(f"tcpdump -r {filepath} -qlnc 1"),
                        stdout=sp.PIPE, encoding='utf-8', stderr=sp.DEVNULL)
    line, _ = get_line.communicate()
    return dst_regex.search(line).group()


def anonymize(inpath, outpath, src, dst):
    prep = sp.Popen(shlex.split(f"tcpprep -i {inpath} -o tmp.cache -p"))
    prep.wait()
    rewrite = sp.Popen(shlex.split(f"tcprewrite -i {inpath} -e {src}:{dst} -o {outpath} -c tmp.cache"))
    rewrite.wait()
    os.remove("tmp.cache")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('input', help="pcap to split up")
    parser.add_argument('res_ips', help="File containing a list of doh resolver IPs")
    parser.add_argument('own_ip', help="The IP used for sending queries")
    parser.add_argument('output', help="output directory of named pcaps")
    parser.add_argument('-n', '--no_anon', action='store_true')
    parser.add_argument('-s', '--source', help="new source IP", default="192.0.0.1")
    parser.add_argument('-d', '--dest', help="new dest IP", default="192.0.0.2")

    args = parser.parse_args()

    with open(args.res_ips, 'r') as f:
        resolvers = f.readline().split(' ')

    print("Splitting pcap by connections")
    os.mkdir('tmp')
    splitter = sp.Popen(shlex.split(f"PcapSplitter -f {args.input} -o tmp -m connection"), stdout=sp.PIPE)
    splitter.communicate()

    doh_count = 0
    web_count = 0

    print("Identifying and anonymizing each pcap")

    if not os.path.exists(args.output):
        os.mkdir(args.output)
    for root, _, files in os.walk('tmp'):
        for file in tqdm(files, total=len(files)):
            if file.endswith(".pcap"):

                dst_ip = get_destination(f"tmp/{file}")

                if dst_ip == args.own_ip:
                    break
                if dst_ip in resolvers:
                    outname = f"doh_{doh_count}.pcap"
                    doh_count += 1
                else:
                    outname = f"web_{web_count}.pcap"
                    web_count += 1

                if args.no_anon:
                    shutil.copy(os.path.join(root, file), f"{args.output}/{outname}")
                else:
                    anonymize(os.path.join(root, file), f"{args.output}/{outname}", args.source, args.dest)


    shutil.rmtree('tmp')

