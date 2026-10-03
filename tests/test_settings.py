"""settings.json is what every session starts from: a command or folder it names that is missing
fails silently at session start, so it is checked here instead."""
import json
import os
import shlex
import unittest
from pathlib import Path

from support import HOME

SETTINGS = json.loads((HOME / "settings.json").read_text())


def local_path(text):
    """A path the settings name, with `~` meaning this config folder's home, as on any machine."""
    return HOME.parent / text[2:] if text.startswith("~/") else Path(text)


class Settings(unittest.TestCase):
    def assertRunnable(self, command):
        program = local_path(shlex.split(command)[0])
        self.assertTrue(program.is_file() and os.access(program, os.X_OK), f"{command}: {program} is not executable")

    def test_every_hook_command_is_runnable(self):
        for event, groups in SETTINGS.get("hooks", {}).items():
            for group in groups:
                for hook in group["hooks"]:
                    with self.subTest(event=event, command=hook["command"]):
                        self.assertRunnable(hook["command"])

    def test_the_status_line_is_runnable(self):
        self.assertRunnable(SETTINGS["statusLine"]["command"])

    def test_every_plugin_dir_is_a_plugin_named_portably(self):
        dirs = SETTINGS["env"]["CLAUDE_CODE_PLUGIN_DIRS"].split(os.pathsep)
        for d in dirs:
            with self.subTest(dir=d):
                self.assertFalse(d.startswith("/home/"), "use ~ so the path holds on another machine")
                self.assertTrue((local_path(d) / ".claude-plugin" / "plugin.json").is_file())

    def test_the_theme_exists(self):
        theme = SETTINGS.get("theme", "")
        if theme.startswith("custom:"):
            self.assertTrue((HOME / "themes" / f"{theme[7:]}.json").is_file())


if __name__ == "__main__":
    unittest.main()
