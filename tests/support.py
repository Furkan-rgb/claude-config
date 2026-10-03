"""Runs the setup's scripts as a hook or the Lead would: a subprocess in a throwaway project."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOME = Path(__file__).resolve().parent.parent
LEDGER = HOME / "skills" / "task-ledger" / "ledger"
DECISIONS = HOME / "skills" / "lead-playbook" / "decisions"


class ProjectTest(unittest.TestCase):
    """Each test gets an empty project directory and its own runtime dir for the scripts' state."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "project"
        self.root.mkdir()
        runtime = Path(tmp.name) / "runtime"
        runtime.mkdir()
        self.env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.root), "XDG_RUNTIME_DIR": str(runtime)}

    def _run(self, script, args):
        return subprocess.run([str(script), *args], cwd=self.root, env=self.env, stdin=subprocess.DEVNULL,
                              capture_output=True, text=True, timeout=30)

    def run_script(self, script, *args):
        """Its stdout; the test fails if it exits non-zero."""
        ran = self._run(script, args)
        if ran.returncode != 0:
            self.fail(f"{script.name} {' '.join(args)} exited {ran.returncode}: {ran.stderr}")
        return ran.stdout

    def refused(self, script, *args):
        """Its stderr; the test fails if it exits zero."""
        ran = self._run(script, args)
        if ran.returncode == 0:
            self.fail(f"{script.name} {' '.join(args)} was not refused: {ran.stdout}")
        return ran.stderr
