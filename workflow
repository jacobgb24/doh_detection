py doh/test_res.py doh/all_resolvers.txt doh/resolver.txt

sudo ip addr add 10.2.4.25 dev ens33
py generator.py alexa/alexa.txt doh/resolvers.txt <out> 10.2.4.25

py doh/ip_tester.py doh/resolvers.txt doh/ips.txt
py pcap_splitter.py <out>.pcap doh/ips.txt 10.2.4.25 <out_dir>

find . -type f -size +100k -delete
tar -czvf out.tar.gz <out_dir>
