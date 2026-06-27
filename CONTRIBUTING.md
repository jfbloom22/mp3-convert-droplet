# Contributing

This project is intentionally small and local-first.

## What to keep in mind

- Keep the drag-and-drop workflow simple.
- Prefer standard macOS and `ffmpeg` APIs over custom workarounds.
- Avoid adding subscriptions, cloud dependencies, or extra moving parts.
- Preserve the recursive folder workflow and the Music/Audiobook presets.

## Local checks

```sh
python3 -m unittest discover -s tests
./build_icon.sh
./install_droplet.sh
```

## Pull requests

- Describe the user-facing change.
- Call out any macOS permission, install, or packaging impact.
- Include the commands you ran to verify the change.
