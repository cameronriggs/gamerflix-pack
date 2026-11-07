# Decompiles the fish mods and writes each class's declaration line plus entity registration and category lines to entscan.txt.
import os, subprocess, glob, urllib.request, zipfile, re
out = open("entscan.txt", "w")
for u in open("tools/entjars.txt").read().split():
    name = u.rsplit("/", 1)[-1]
    os.makedirs("dl", exist_ok=True); p = "dl/" + name
    open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "gamerflix-scan"}), timeout=60).read())
    z = zipfile.ZipFile(p)
    base = name[:-4]
    cdir = "cls/" + base; d = "srcout/" + base
    os.makedirs(d, exist_ok=True)
    for n in z.namelist():
        if n.endswith(".class"):
            os.makedirs(os.path.dirname(os.path.join(cdir, n)), exist_ok=True)
            open(os.path.join(cdir, n), "wb").write(z.read(n))
    subprocess.run(["java", "-jar", "vineflower.jar", "-log=ERROR", cdir, d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out.write(f"\n##### {name}\n")
    for f in sorted(glob.glob(d + "/**/*.java", recursive=True)):
        rel = f[len(d)+1:]
        src = open(f, errors="replace").read()
        for l in src.splitlines():
            s = l.strip()
            if re.match(r"(public |abstract |final |private |protected |static )*(class|interface|record|enum) ", s) or "MobCategory." in s or "EntityType.Builder" in s or "fireImmune" in s or "isMonster" in s or re.search(r"\b(Monster|Enemy|Bucketable)\b", s):
                out.write(f"{rel}: {s[:300]}\n")
        if re.search(r"(Registries\.ENTITY_TYPE|EntityType\.Builder)", src) or "Entities" in rel.split("/")[-1]:
            out.write(f"\n===== FULL {rel}\n" + "\n".join(x for x in src.splitlines() if not x.startswith("import ")) + "\n")
out.close()
