import tempfile
import unittest
from pathlib import Path

import convert_audio_to_mp3 as converter


class ConverterTests(unittest.TestCase):
    def test_build_encoder_args_for_music(self) -> None:
        self.assertEqual(
            converter.build_encoder_args(preset="music", quality=None),
            ["-c:a", "libmp3lame", "-q:a", "0"],
        )

    def test_build_encoder_args_for_custom_music_quality(self) -> None:
        self.assertEqual(
            converter.build_encoder_args(preset="music", quality="3"),
            ["-c:a", "libmp3lame", "-q:a", "3"],
        )

    def test_build_encoder_args_for_audiobook(self) -> None:
        self.assertEqual(
            converter.build_encoder_args(preset="audiobook", quality=None),
            ["-c:a", "libmp3lame", "-b:a", "128k"],
        )

    def test_mp3_quality_validation(self) -> None:
        self.assertEqual(converter.mp3_quality("0"), "0")
        self.assertEqual(converter.mp3_quality("9"), "9")
        with self.assertRaises(Exception):
            converter.mp3_quality("10")
        with self.assertRaises(Exception):
            converter.mp3_quality("high")

    def test_iter_audio_files_recurses_and_skips_mp3(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nested = root / "nested"
            nested.mkdir()
            m4a = nested / "track.m4a"
            mp3 = nested / "track.mp3"
            txt = nested / "notes.txt"
            m4a.write_text("m4a")
            mp3.write_text("mp3")
            txt.write_text("txt")

            self.assertEqual(converter.iter_audio_files([root]), [m4a.resolve()])


if __name__ == "__main__":
    unittest.main()
