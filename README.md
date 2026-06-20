# MP3 Convert

Recursive drag-and-drop audio conversion for macOS, backed by `ffmpeg`.

## Install on a Mac

Install `ffmpeg` first:

```sh
brew install ffmpeg
```

Then install the local command and Dock droplet:

```sh
./install_droplet.sh
```

This creates:

- `~/.local/bin/mp3-convert`
- `~/Applications/Convert Audio to MP3.app`

Drag `~/Applications/Convert Audio to MP3.app` to the Dock. Drop audio files or folders onto it to convert recursively. In droplet mode, originals are moved to the macOS Trash after successful conversion.

To uninstall:

```sh
./uninstall_droplet.sh
```

## Local Test Mode

By default, the script writes `.mp3` files beside the originals and leaves the source files in place:

```sh
./convert_audio_to_mp3.py sample
```

Preview work without converting:

```sh
./convert_audio_to_mp3.py --dry-run sample
```

Replace existing MP3 outputs during repeated tests:

```sh
./convert_audio_to_mp3.py --overwrite sample
```

## Production Mode

After a successful conversion, move the original non-MP3 audio file to the macOS Trash:

```sh
./convert_audio_to_mp3.py --trash-originals /path/to/folder
```

Use `--overwrite` too if existing `.mp3` files should be replaced:

```sh
./convert_audio_to_mp3.py --trash-originals --overwrite /path/to/folder
```

## Drag-and-Drop Dock App

The installer builds the droplet locally on each Mac with `osacompile`, so there is no downloaded unsigned app bundle to distribute. The app calls `~/.local/bin/mp3-convert --trash-originals` for dropped files and folders.

Automator runs with a minimal shell environment, so it may not inherit Homebrew's `PATH`. The converter handles this by checking common ffmpeg locations like `/opt/homebrew/bin/ffmpeg` and `/usr/local/bin/ffmpeg`.

## Conversion Defaults

- Inputs: `.aac`, `.aif`, `.aiff`, `.alac`, `.flac`, `.m4a`, `.m4b`, `.ogg`, `.opus`, `.wav`, `.wma`
- Skips existing `.mp3` outputs unless `--overwrite` is passed.
- Uses `libmp3lame` VBR quality `-q:a 2`.
- Preserves source metadata with `-map_metadata 0`.
- Writes through a temporary file before replacing the final `.mp3`.
