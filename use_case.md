# Block DNS over HTTPS using Firepower NGFW
## Keep your users secure and avoid bypassing of your security controls

DNS-over-HTTPS (DoH) is a standard for performing DNS resolution via via the HTTPS protocol. Instead of performing plain text (n.a. for Umbrella) DNS requests on port 53, a client to a DoH-compatible DNS server using an encrypted HTTPS connection instead of a plain text (n.a. for Umbrella) one.

**Risks, why would you NOT use it:**
* Some individuals and organizations rely on DNS (e.g. Umbrella) to block malware, enable parental controls, or filter your browser’s access to websites;
* Mozilla Firefox uses Cloudlfare as default DoH provider. This gives Cloudflare full visibility into the DNS requests of the client;
* DoH could be [slower](https://support.mozilla.org/en-US/kb/firefox-dns-over-https) than traditional DNS queries.

**Business outcomes:**
* The result will be that DoH is blocked;
* This causes browsers to revert back to “regular” DNS;
* Cisco Umbrella is then again able to to block malware, enable parental controls, or filter your browser’s access to websites .

You can find the installation instructions on [Cisco DevNet Code Exchange](https://developer.cisco.com/codeexchange/github/repo/chrivand/block_doh_firepower).

## White Paper
The NSA also recommends to take a similar approach and blocking DoH. Read more [here](https://www.nsa.gov/News-Features/Feature-Stories/Article-View/Article/2471956/nsa-recommends-how-enterprises-can-securely-adopt-encrypted-dns/).

## Related Sandbox
Please check out the Firepower Manegement Center sandbox to give this a try yourself!
