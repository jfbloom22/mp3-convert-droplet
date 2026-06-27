# MP3 Convert Droplet

I built this because I missed the old feeling of making MP3 CDs. As a teenager, I loved fitting a handful of favorite albums onto one disc. My sons now use the same style of setup, and when I looked for software to help them make MP3 CDs in 2026, the options were surprisingly poor: subscription apps, Apple Music workarounds, and tools that were not very pleasant to use.

What they need is simple. They create a folder for a CD, put nested folders inside it as playlists or album groupings, then drag the whole thing onto this app. It asks whether the batch is Music or Audiobook, converts the supported audio files to MP3, and leaves them ready for Roxio Toast or whatever they use to burn the disc. This project was built in a few hours over a weekend with help from AI coding agents.

![MP3 Convert Droplet demo](assets/audio%20to%20mp3.gif)

## What It Does

`MP3 Convert Droplet` is a local macOS drag-and-drop app for recursively converting nested audio folders into MP3 files.

- Drag a folder onto the app icon.
- Pick `Music` for higher quality or `Audiobook` for smaller files.
- Existing `.mp3` files are skipped.
- Originals are moved to Trash after successful conversion.
- Use a separate burning app to make the CD afterward.

The app is intentionally small and local-first. It uses `ffmpeg` for conversion and does not require a subscription or cloud service.

## Install

Install `ffmpeg` first:

```sh
brew install ffmpeg
```

Clone the repo and install the local command and Dock droplet:

```sh
git clone git@github.com:jfbloom22/mp3-convert-droplet.git
cd mp3-convert-droplet
./install_droplet.sh
```

That creates:

- `~/.local/bin/mp3-convert`
- `~/Applications/Convert Audio to MP3.app`

Drag `~/Applications/Convert Audio to MP3.app` to the Dock. Dropping files or folders onto it will recurse through the tree and convert the supported audio files in place.

To uninstall:

```sh
./uninstall_droplet.sh
```

## Why This Exists

This follows the same droplet idea as [Loomify](https://github.com/jfbloom22/Loomify): put files on an app icon and let the app do the boring part. That model feels better than hunting through menus or signing up for another service.

## Usage

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

Production mode moves the original audio to Trash after a successful conversion:

```sh
./convert_audio_to_mp3.py --trash-originals --preset music /path/to/folder
```

Use the audiobook preset for spoken-word material:

```sh
./convert_audio_to_mp3.py --trash-originals --preset audiobook /path/to/folder
```

## Development

Run the tests:

```sh
python3 -m unittest discover -s tests
```

Rebuild the icon:

```sh
./build_icon.sh
```

Reinstall the local app bundle:

```sh
./install_droplet.sh
```

## Implementation Notes

- Inputs: `.aac`, `.aif`, `.aiff`, `.alac`, `.flac`, `.m4a`, `.m4b`, `.ogg`, `.opus`, `.wav`, `.wma`
- Skips existing `.mp3` outputs unless `--overwrite` is passed.
- Music preset uses `libmp3lame` VBR quality `-q:a 0`.
- Audiobook preset uses `libmp3lame` bitrate `-b:a 128k`.
- Preserves source metadata with `-map_metadata 0`.
- Writes through a temporary file before replacing the final `.mp3`.
