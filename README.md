# Gamerflix

The Gamerflix modpack: Minecraft 1.21.1 with NeoForge, about 85 mods (plus the libraries they need). The full list
with what each mod is for is at [riggs.one/gamerflix-modpack](https://riggs.one/gamerflix-modpack).

You install it once. After that, every time you press Play the launcher checks for changes to the pack and downloads
them, so you're always on the same mods as the server.

## Installing (players)

1. **Install Prism Launcher** from [prismlauncher.org](https://prismlauncher.org/download/) (on Windows, the
   "Setup" installer is easiest).
2. **Sign in:** open Prism, click **Accounts** (top right), **Manage Accounts**, **Add Microsoft**, and sign in with the
   account you play Minecraft with.
3. **Download the instance:** [Gamerflix.zip](https://cameronriggs.github.io/gamerflix-pack/instance/Gamerflix.zip).
   Don't unzip it.
4. **Import it:** in Prism, click **Add Instance**, choose **Import** on the left, pick `Gamerflix.zip` and click
   **OK**. A "Gamerflix" instance appears.
5. **Check its memory (RAM):** right-click Gamerflix, **Edit**, **Settings**, **Java**. It's set to use up to 8 GB
   (8192 MiB). That's right for a PC with 16 GB or more. With 8 GB in total, set the maximum to 6144.
6. **Play:** double-click Gamerflix. If Prism asks to download Java, say yes. The first launch downloads every mod
   (a small window shows the progress), so it takes a while; later launches only fetch what changed.

Then join the Gamerflix server from **Multiplayer** (ask Cameron for the address).

**If something goes wrong:** a launch that fails at the "pre-launch command" step means the pack couldn't be
downloaded (check your internet and try again). For anything else, send Cameron the log: right-click Gamerflix,
**Folder**, then `minecraft/logs/latest.log` (or `.minecraft/logs/latest.log`).

## How it works (for Cameron)

This repo is a [packwiz](https://packwiz.infra.link/) pack. `pack.toml` names the Minecraft and NeoForge versions,
`mods/` has one small `.pw.toml` file per mod (where to download it, its checksum, and whether it's for the client,
the server or both), and `index.toml` lists every file with its checksum. GitHub Pages serves the repo at
**https://cameronriggs.github.io/gamerflix-pack/pack.toml**, the pack URL.

The Prism instance runs `packwiz-installer-bootstrap.jar` before every launch (Edit, Settings, Custom commands,
"Pre-launch command"). It reads the pack URL and downloads whatever changed. The server does the same with:

```sh
java -jar packwiz-installer-bootstrap.jar -g -s server https://cameronriggs.github.io/gamerflix-pack/pack.toml
```

(`-g` means no window, `-s server` skips client-only mods such as Sodium and Mouse Tweaks.)

### Changing the pack

With [packwiz](https://github.com/packwiz/packwiz) installed (on the home PC it's in `C:\Users\cbenj\.local\bin`):

```sh
packwiz modrinth add <slug or URL>     # add a mod from Modrinth (preferred: CurseForge can block downloads)
packwiz curseforge add <URL>           # only for mods that aren't on Modrinth
packwiz remove <name>                  # remove one (the name is its file name in mods/, without .pw.toml)
packwiz update <name>                  # newest version of one mod
packwiz refresh                        # rebuild index.toml: run it before every commit
```

Then commit and push. GitHub Pages republishes within a minute or two, and its cache can take up to ten minutes more;
after that, every launch picks the change up.

Mods are pinned to the files chosen when they were added; nothing updates by itself except Cubits (below).

### Cubits

The **Update Cubits** workflow (Actions tab) runs every hour and on demand: it takes the newest Cubits from Modrinth,
commits and republishes. So a Cubits release (a `vX.Y.Z` tag in the Cubits repo) reaches everyone on its own.

Until Modrinth approves the Cubits project, Cubits is a plain jar in `mods/` instead, and a new version has to be
swapped in by hand (delete the old jar, add the new one, `packwiz refresh`, commit). Once it's approved:

```sh
rm mods/cubits-*.jar
packwiz modrinth add QpFU07jQ
packwiz refresh
```

### Not in the pack

- **Desire Lines** is a datapack (worn paths), so it belongs in the server's world: `world/datapacks/`.
- **Item Collectors** has no 1.21.1 version; it needs a replacement.

### The instance zip

`instance/Gamerflix.zip` is built from `instance/src/Gamerflix` (Prism's `instance.cfg` and `mmc-pack.json`, and the
bootstrap jar in `.minecraft/`). To change the NeoForge version or the memory defaults, edit those files and zip the
`Gamerflix` folder again.
