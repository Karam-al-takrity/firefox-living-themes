# Firefox Living Themes

Five animated themes for Firefox, with a palette button to switch between them instantly. All the art and sound is original and generated locally, and nothing loads from the internet.

Built and tested on **Firefox 159 on Windows 11**. Other versions and systems may need small fixes (see [Contributing](CONTRIBUTING.md)).

| Meridian | Manga: Ghoul | Nocturne |
|---|---|---|
| ![Meridian](screenshots/meridian.jpg) | ![Manga: Ghoul](screenshots/manga.jpg) | ![Nocturne](screenshots/nocturne.jpg) |

*These show the new tab artwork rendered outside Firefox. Real screenshots of all five themes are welcome as contributions.*

## The themes

- **Meridian:** a brass astronomical clock on midnight blue. It shows your real time, today's date and calculated planet positions and moon phase, with meshing gears, a soft tick and a music box. *Its clock needs the theme loader (Step 2).*
- **Nocturne:** pastel space and pixel games, with a bookmarks dock that magnifies, a rocket loading bar, a walking pixel critter, 20 colour palettes and a Game Over page when you're offline.
- **Ame:** a rainy neon city seen from a loft window, with a black cat, a passing train and lo-fi rain music.
- **Relics:** a moonlit Japanese room lit by a paper lantern, with nods to favourite shows and games, and koto music.
- **Manga: Ghoul:** a dark manga page inspired by Tokyo Ghoul, with a red eye, spider lilies, a "1000 − 7" countdown and Japanese sound effects on your buttons.

## Setup (Windows)

### Step 1: Install the themes

1. On this page, click **Code → Download ZIP**, then unzip it anywhere.
2. **Close Firefox completely.**
3. Open the unzipped folder, click the address bar at the top of the window, type `powershell` and press Enter.
4. Run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File install.ps1
   ```
5. Start Firefox. You should see Nocturne.

The installer backs up your existing `chrome` folder first and needs no admin rights. It only touches `chrome` and one line in `user.js`.

### Step 2 (optional): Install the theme loader

**Firefox can't run a theme's scripts by itself, so this step is what adds the palette button, Ctrl+Alt+T, the Meridian clock and the music.** Without it, the styles still work and you can switch themes by hand (see below).

> **Security trade-off, please read.** This adds two files to Firefox's program folder that run every theme's `chrome.js` with **full access to Firefox and your files**. The scripts here only build the interface and synthesise music, and you can read them yourself: `loader/theme-loader.cfg` and `chrome/themes/*/chrome.js`. But once the loader is installed, any `chrome.js` placed in those folders will run with that same access, so only add themes you trust.

1. Close Firefox.
2. Open **PowerShell as administrator** and go to the unzipped folder:
   ```powershell
   cd "C:\path\to\the\unzipped\folder"
   ```
3. Run:
   ```powershell
   powershell -ExecutionPolicy Bypass -File loader\install-loader.ps1
   ```
4. Start Firefox. The palette button appears next to the ☰ menu.

### Other systems

macOS and Linux should work but **haven't been tested**, and `install.ps1` is Windows-only. To install by hand:

1. Open `about:support` in Firefox and click **Open Folder** next to *Profile Folder*.
2. Close Firefox, then copy this repo's `chrome` folder and `user.js` into the profile folder. If you already have a `user.js`, add its line to yours instead of replacing it.
3. For the loader, copy `loader/theme-loader.cfg` next to the Firefox program, and `loader/defaults/pref/autoconfig.js` into its `defaults/pref/` folder. On macOS these go inside `Firefox.app/Contents/Resources/`.

## Using it

- **Switch themes:** use the palette button, or press **Ctrl+Alt+T**.
- **Switch without the loader:** in `about:config`, set one of `ame.active`, `relics.active`, `manga.active` or `meridian.active` to true (create it as a Boolean if it's missing). Set them all to false for Nocturne. Keep only one on at a time.
- **Stop the animations:** use **Freeze animations** in the palette menu, or set `<theme>.freeze` to true in `about:config`.
- **Music:** it plays only on the new tab page. Click the button at the end of the tab bar to mute it, and scroll on it to change the volume.
- **Bookmark icons:** bookmarks-bar folders named `AI`, `Social`, `Piracy`, `Tetris`, `TFT`, `Chess`, `Linux` or `Other`, and a bookmark named `Freeze`, get custom icons. Change the names in each theme's CSS to suit your own.

## Good to know

- **New tab page:** themes that draw over the new tab may hide or cover its search box and shortcuts. Search from the address bar.
- **Private windows:** each theme has a private look. Meridian covers the private-browsing page, so search from the address bar there too.
- **Firefox updates** can change internal names and break some styling. Please open an issue if they do.

## Uninstall

1. Close Firefox.
2. In your profile folder, delete `chrome`, or replace it with the `chrome-backup-...` folder the installer made.
3. If you installed the loader, delete `theme-loader.cfg` and `defaults\pref\autoconfig.js` from `C:\Program Files\Mozilla Firefox`.
4. Optional: remove the line this added to `user.js`, then set `toolkit.legacyUserProfileCustomizations.stylesheets` to false in `about:config`.

## Contributing

New themes, fixes and macOS or Linux testing are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Credits and license

Code and original art are under the [MIT License](LICENSE).

This is an unofficial fan project, not affiliated with or endorsed by Mozilla or the creators of the works it nods to. Tokyo Ghoul, The Mentalist and the other referenced titles belong to their respective owners. The artwork here is original and contains no material copied from those works.
