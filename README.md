<p align="center">
  <img src="https://raw.githubusercontent.com/xuefei-wang/aloud/main/banner.png" alt="aloud — words, spoken.">
</p>

<p align="center">
  <strong>Text in, speech out.</strong> Free text-to-speech CLI — no API key needed.
  <br>
  Linux · macOS · Windows
</p>

## Install

```bash
uv tool install aloud
```

Or with pip:

```bash
pip install aloud
```

### System dependencies

- **mpv** — audio playback
- **ffprobe** — episode durations, publish mode only
- **git** — feed publishing
- **Clipboard** (for `aloud -c`): pbpaste (macOS), xclip/xsel/wl-paste (Linux)

Install on Linux: `sudo apt install mpv ffmpeg git`
Install on macOS: `brew install mpv ffmpeg git`
Install on Windows: `winget install mpv ffmpeg git`

## Usage

```bash
aloud article.txt              # play locally
aloud -c                       # read from clipboard
cat notes.md | aloud           # read from stdin
aloud -s "+80%" paper.md       # custom speed
aloud -v "en-US-JennyNeural"   # different voice
```

Press **q** to quit. Space = pause, Left/Right = skip 5s.

### Options

| Flag | Description |
|------|-------------|
| `-c`, `--clipboard` | Read from clipboard instead of file |
| `-o`, `--output` | Publish to podcast feed (no playback) |
| `-s`, `--speed` | TTS speed (default: `+20%`) |
| `-v`, `--voice` | TTS voice (default: `en-US-AndrewMultilingualNeural`) |

### Subcommands

| Command | Description |
|---------|-------------|
| `aloud feed` | Regenerate RSS feed and git push |
| `aloud config` | Interactive setup wizard |

## Configuration

Run `aloud config` to set up. Config is stored in `~/.config/aloud/config.json`.

Playback works immediately — no config needed. Publishing requires the setup below.

## Publishing setup

`aloud -o` publishes episodes to a self-hosted podcast feed via a git repo served with GitHub Pages. One-time setup:

**1. Create the feed repo:**

```bash
gh repo create my-podcast-feed --public --clone
cd my-podcast-feed
mkdir episodes
git add . && git commit -m "init" && git push
```

**2. Enable GitHub Pages:**

Go to the repo's **Settings > Pages**, set source to **Deploy from a branch**, branch **main**, folder **/ (root)**.

Your feed will be served at `https://<username>.github.io/<repo-name>`.

**3. Configure aloud:**

```bash
aloud config
```

Enter the local repo path and the GitHub Pages URL when prompted.

**4. Publish an episode:**

```bash
aloud -o article.txt     # synthesize, copy to feed repo, regenerate RSS, git push
```

Subscribe to the feed in any podcast app using `https://<username>.github.io/<repo-name>/feed.xml`.

## License

GPL-3.0-or-later
