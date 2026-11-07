# Dumps item names, recipes, loot tables, tags and configs from mod jars into datadump.txt.gz.
import zipfile, urllib.request, os, gzip, json
urls = open("tools/datajars.txt").read().split()
out = gzip.open("datadump.txt.gz", "wt")
for u in urls:
    name = u.rsplit("/", 1)[-1]
    os.makedirs("dl", exist_ok=True); p = "dl/" + name
    open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "gamerflix-scan"}), timeout=60).read())
    z = zipfile.ZipFile(p)
    out.write(f"\n##### {name}\n")
    for n in z.namelist():
        keep = (n.startswith("data/") and n.endswith(".json")) or n.endswith("lang/en_us.json") or n.endswith((".toml", ".mcmeta")) or (n.startswith("assets/") and "/models/item/" in n)
        if not keep: continue
        if "/models/item/" in n:
            out.write(f"MODELITEM {n}\n"); continue
        out.write(f"\n===== {n}\n{z.read(n).decode(errors='replace')}\n")
out.close()
