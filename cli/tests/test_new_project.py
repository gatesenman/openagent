import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from openagent_cli import write_new_project  # noqa: E402


class TestNewProject(unittest.TestCase):
    def test_writes_manifest_requirements_and_passing_test(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "demo-app"
            manifest = write_new_project(root, "demo-app")
            self.assertEqual(manifest["kind"], "openagent-project")
            data = json.loads((root / "openagent.project.json").read_text(encoding="utf-8"))
            self.assertEqual(data["name"], "demo-app")
            self.assertTrue((root / "requirements.txt").is_file())
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                cwd=root,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
