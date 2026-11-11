# Finds every mod that adds music or touches the music system, and measures streamed tracks.
import glob, os, re, subprocess, tomllib, urllib.request, zipfile, io, json
out = open("musicscan.txt", "w")
os.makedirs("jars", exist_ok=True); os.makedirs("classes", exist_ok=True); os.makedirs("src", exist_ok=True); os.makedirs("ogg", exist_ok=True)
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
        req = urllib.request.Request(url.replace(" ", "%20"), headers={"User-Agent": "gamerflix-musicscan"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=60).read())
    except Exception as e:
        out.write(f"!! download failed {f}: {e}\n")
for p in glob.glob("mods/*.jar"):
    os.system(f"cp '{p}' jars/")
PAT = [b"net/minecraft/client/sounds/MusicManager", b"net/minecraft/sounds/Music;", b"getSituationalMusic",
       b"SelectMusicEvent", b"net/minecraft/client/sounds/SoundManager", b"SoundEngine", b"stopMusic", b"PlaySoundEvent"]
hits = {}
def ffinfo(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect,ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    e = r.stderr
    dur = re.search(r"Duration: ([0-9:.]+)", e); mx = re.search(r"max_volume: ([-0-9.]+)", e)
    mn = re.search(r"mean_volume: ([-0-9.]+)", e); I = re.findall(r"I:\s+([-0-9.]+) LUFS", e)
    lra = re.findall(r"LRA:\s+([-0-9.]+) LU", e)
    return f"dur={dur and dur.group(1)} mean={mn and mn.group(1)} max={mx and mx.group(1)} I={I[-1] if I else None} LRA={lra[-1] if lra else None}"
def scan(name, data, mod):
    try: z = zipfile.ZipFile(io.BytesIO(data))
    except Exception: return
    names = set(z.namelist())
    for n in z.namelist():
        if n.endswith(".jar"):
            scan(n, z.read(n), mod); continue
        if n.endswith(".class"):
            b = z.read(n)
            found = [x.decode() for x in PAT if x in b]
            if found:
                hits.setdefault(mod, []).append((n, found))
                dst = os.path.join("classes", mod, n)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                open(dst, "wb").write(b)
        m = re.match(r"assets/([^/]+)/sounds\.json$", n)
        if m:
            ns = m.group(1)
            try: js = json.loads(z.read(n).decode("utf-8", "replace"))
            except Exception as ex:
                out.write(f"!! {mod} {n} bad json {ex}\n"); continue
            for ev, v in js.items():
                sounds = v.get("sounds", []) if isinstance(v, dict) else []
                streamed = any(isinstance(s, dict) and s.get("stream") for s in sounds)
                if not (streamed or "music" in ev.lower() or ns == "minecraft"): continue
                out.write(f"SOUND {mod} {ns}:{ev} replace={v.get('replace') if isinstance(v,dict) else None} stream={streamed} n={len(sounds)}\n")
                for s in sounds:
                    sn = s if isinstance(s, str) else s.get("name")
                    typ = None if isinstance(s, str) else s.get("type")
                    extra = "" if isinstance(s, str) else json.dumps({k: s[k] for k in s if k not in ("name",)})
                    if typ == "event":
                        out.write(f"   -> event {sn} {extra}\n"); continue
                    sns, _, sp = sn.partition(":") if ":" in sn else (ns, ":", sn)
                    op = f"assets/{sns}/sounds/{sp}.ogg"
                    info = ""
                    if op in names and streamed:
                        lp = os.path.join("ogg", mod + "_" + op.replace("/", "_"))
                        open(lp, "wb").write(z.read(op)); info = ffinfo(lp)
                    out.write(f"   {sn} {extra} {info}\n")
for p in sorted(glob.glob("jars/*.jar")):
    mod = os.path.basename(p)[:-4]
    scan(p, open(p, "rb").read(), mod)
out.write("\n\n##### CLASS HITS\n")
for mod in sorted(hits):
    for n, f in hits[mod]:
        out.write(f"HIT {mod} {n} {f}\n")
full = open("musicsrc.txt", "w")
for mod in sorted(os.listdir("classes")):
    srcdir = os.path.join("src", mod)
    subprocess.run(["java", "-jar", "vineflower.jar", "-log=ERROR", os.path.join("classes", mod), srcdir],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for j in sorted(glob.glob(srcdir + "/**/*.java", recursive=True)):
        t = "\n".join(l for l in open(j, errors="replace").read().splitlines() if not l.startswith("import "))
        full.write(f"\n===== {mod} :: {j[len(srcdir)+1:]}\n{t}\n")
full.close(); out.close()
