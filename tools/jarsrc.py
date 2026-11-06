# Decompiles whole jars and writes their sources and small config files to jarsrc.txt.
import os, subprocess, glob, urllib.request, zipfile
out = open("jarsrc.txt", "w")
for u in open("tools/jars.txt").read().split():
    name = u.rsplit("/", 1)[-1]
    os.makedirs("dl", exist_ok=True); p = "dl/" + name
    open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "gamerflix-keyscan"}), timeout=60).read())
    z = zipfile.ZipFile(p)
    for n in z.namelist():
        if n.endswith((".toml", ".json", ".txt", ".cfg", ".properties")) and "lang/" not in n and "models/" not in n and "textures/" not in n:
            out.write(f"\n===== {name} :: {n}\n{z.read(n).decode(errors='replace')[:3000]}\n")
    d = "srcout/" + name
    subprocess.run(["java", "-jar", "vineflower.jar", "-log=ERROR", p, d], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for f in sorted(glob.glob(d + "/**/*.java", recursive=True)):
        t = "\n".join(l for l in open(f, errors="replace").read().splitlines() if not l.startswith("import "))
        out.write(f"\n===== {name} :: {f[len(d)+1:]}\n{t}\n")
out.close()
