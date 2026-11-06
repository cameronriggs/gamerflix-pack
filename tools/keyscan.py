# Downloads the client-side mod jars and decompiles every class that builds a KeyMapping,
# then prints the lines around each KeyMapping so the default keys can be read off.
import glob, os, re, subprocess, sys, tomllib, urllib.request, zipfile, io, shutil
out = open("keyscan.txt", "w")
os.makedirs("jars", exist_ok=True); os.makedirs("classes", exist_ok=True); os.makedirs("src", exist_ok=True)
for f in sorted(glob.glob("mods/*.pw.toml")):
    t = tomllib.load(open(f, "rb"))
    if t.get("side") == "server": continue
    d = t["download"]
    if d.get("mode") == "metadata:curseforge":
        fid = t["update"]["curseforge"]["file-id"]
        url = f"https://edge.forgecdn.net/files/{fid//1000}/{fid%1000}/{t['filename']}"
    else:
        url = d["url"]
    p = os.path.join("jars", os.path.basename(f)[:-8] + ".jar")
    try:
        req = urllib.request.Request(url.replace(" ", "%20"), headers={"User-Agent": "gamerflix-keyscan"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    except Exception as e:
        out.write(f"!! download failed {f}: {e}\n")
def scan(name, data, mod):
    try: z = zipfile.ZipFile(io.BytesIO(data))
    except Exception: return
    for n in z.namelist():
        if n.endswith(".jar"):
            scan(n, z.read(n), mod)
        elif n.endswith(".class"):
            b = z.read(n)
            if b"net/minecraft/client/KeyMapping" in b or b"KeyMappingHelper" in b or b"KeyBinding" in b:
                dst = os.path.join("classes", mod, n)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "wb").write(b)
for p in sorted(glob.glob("jars/*.jar")):
    mod = os.path.basename(p)[:-4]
    scan(p, open(p, "rb").read(), mod)
for mod in sorted(os.listdir("classes")):
    srcdir = os.path.join("src", mod)
    subprocess.run(["java", "-jar", "vineflower.jar", "-log=ERROR", os.path.join("classes", mod), srcdir],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for j in sorted(glob.glob(srcdir + "/**/*.java", recursive=True)):
        lines = open(j, errors="replace").read().splitlines()
        hits = [i for i, l in enumerate(lines) if re.search(r"KeyMapping\(|KeyBinding\(|InputConstants\.|GLFW\.|\"key\.|keybind", l)]
        if not hits: continue
        out.write(f"\n===== {mod} :: {j[len(srcdir)+1:]}\n")
        shown = set()
        for i in hits:
            for k in range(max(0, i - 2), min(len(lines), i + 3)):
                if k not in shown:
                    shown.add(k); out.write(f"{k+1}: {lines[k]}\n")
out.close()
