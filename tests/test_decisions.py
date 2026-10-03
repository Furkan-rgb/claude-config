import json
import unittest

from support import DECISIONS, ProjectTest


class Decisions(ProjectTest):
    def record(self, name, text):
        d = self.root / "docs" / "decisions"
        d.mkdir(parents=True, exist_ok=True)
        (d / name).write_text(text)

    def index(self, *args):
        return self.run_script(DECISIONS, "index", *args)

    def test_index_separates_open_questions_from_decisions(self):
        self.record("0001-hexes.md", "# ADR-0001: Tiles are hexes\n\n- **Status:** Accepted, amended by ADR-0003\n")
        self.record("0002-combat.md", "# ADR-0002: Combat in real time?\n\n- **Status:** Proposed\n"
                                      "- **Blocks:** M2 enemy turns\n")
        self.record("0003-old.md", "# ADR-0003: Square tiles\n\n**Status:** Superseded by ADR-0001\n")
        self.assertEqual(self.index(), "Decisions (docs/decisions): 1 open, 1 accepted\n"
                                       "Open (Proposed):\n  ADR-0002 Combat in real time? · blocks: M2 enemy turns\n"
                                       "Accepted:\n  ADR-0001 Tiles are hexes\n")

    def test_json_carries_status_and_blocks(self):
        self.record("0001-packing.md", "# ADR-0001: `tier_packing` stays\n\n- **Status:** Proposed\n"
                                       "- **Blocks:** <what waits on this>\n")
        [r] = json.loads(self.index("--json"))
        self.assertEqual((r["id"], r["title"], r["status"], r["blocks"]), ("ADR-0001", "tier_packing stays", "proposed", None))

    def test_a_record_without_a_status_is_named(self):
        self.record("0001-draft.md", "# ADR-0001: Draft\n")
        self.assertIn("No recognisable status: ADR-0001", self.index())

    def test_silent_in_a_project_without_records(self):
        self.assertEqual(self.index(), "")
        self.assertEqual(self.index("--json"), "")

    def test_new_numbers_the_next_record_from_the_template(self):
        self.record("0007-earlier.md", "# ADR-0007: Earlier\n\n- **Status:** Accepted\n")
        self.assertIn("ADR-0008 written", self.run_script(DECISIONS, "new", "Saves are versioned"))
        text = (self.root / "docs" / "decisions" / "0008-saves-are-versioned.md").read_text()
        self.assertTrue(text.startswith("# ADR-0008: Saves are versioned"))
        self.assertIn("ADR-0008 Saves are versioned", self.index())

    def test_new_creates_the_folder_in_a_project_without_one(self):
        self.run_script(DECISIONS, "new", "First decision")
        self.assertTrue((self.root / "docs" / "decisions" / "0001-first-decision.md").is_file())


if __name__ == "__main__":
    unittest.main()
