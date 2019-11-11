# DNS over HTTPS (DoH) Detection
BYU CS 474 Deep Learning Final Project

---
The code in this repo is mostly intended for generating a mix of HTTPS GET traffic for both websites and DoH resolvers. Generated pcaps are tarred in a release binary (since the tar exceeded the regular file size limit). Pcaps are sorted by traffic type (web/doh) before having IPs anonymized

Import into Google Colab using the following:
```
! wget -v -O pcaps.tar.gz -L "https://github.com/jacobgb24/doh_detection/releases/download/01/pcaps_01.tar.gz"
! tar -xzf pcaps.tar.gz
```
