from pathlib import Path
import httpx

RFCS = {
    791: "Internet Protocol (IPv4)",
    792: "ICMP",
    826: "ARP",
    1034: "DNS concepts",
    1035: "DNS implementation",
    2131: "DHCP",
    2328: "OSPFv2",
    4271: "BGP-4",
    8200: "IPv6",
    9293: "TCP",
}

out = Path("data/docs/rfc")
out.mkdir(parents=True, exist_ok=True)
rows = []
for n, title in RFCS.items():
    url = f"https://www.rfc-editor.org/rfc/rfc{n}.txt"
    r = httpx.get(url, timeout=60, follow_redirects=True)
    r.raise_for_status()
    (out / f"rfc{n}.txt").write_text(r.text, encoding="utf-8")
    rows.append(f"| RFC {n} | {title} | {url} |")
    print("ok", n)

with open("data/docs/SOURCES.md", "a", encoding="utf-8") as f:
    f.write("\n".join(rows) + "\n")