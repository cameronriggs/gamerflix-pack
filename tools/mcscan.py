# Decompiles MineColonies classes that send colony music, and Bumblezone classes that call its MusicHandler.
import glob, os, subprocess, tomllib, urllib.request, zipfile, io
out = open("mcsrc.txt", "w")
WANT = {"minecolonies": [b"PlayAudioMessage", b"StopMusicMessage", b"RAID_", b"tavern"],
        "the-bumblezone": [b"MusicHandler"], "the-undergarden": [b"SoundManager"]}
for mod, pats in WANT.items():
    t = tomllib.load(open(f"mods/{mod}.pw.toml", "rb")); d = t["download"]
    if d.get("mode") == "metadata:curseforge":
        fid = t["update"]["curseforge"]["file-id"]; url = f"https://edge.forgecdn.net/files/{fid//1000}/{fid%1000}/{t['filename']}"
    else: url = d["url"]
    data = urllib.request.urlopen(urllib.request.Request(url.replace(" ", "%20"), headers={"User-Agent": "gamerflix-musicscan"}), timeout=120).read()
    z = zipfile.ZipFile(io.BytesIO(data)); cdir = f"mc_cls/{mod}"
    for n in z.namelist():
        if n.endswith(".class"):
            b = z.read(n)
            if any(p in b for p in pats):
                os.makedirs(os.path.dirname(os.path.join(cdir, n)), exist_ok=True); open(os.path.join(cdir, n), "wb").write(b)
    sd = f"mc_src/{mod}"
    subprocess.run(["java", "-jar", "vineflower.jar", "-log=ERROR", cdir, sd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for j in sorted(glob.glob(sd + "/**/*.java", recursive=True)):
        tx = "\n".join(l for l in open(j, errors="replace").read().splitlines() if not l.startswith("import "))
        out.write(f"\n===== {mod} :: {j[len(sd)+1:]}\n{tx}\n")
out.close()
