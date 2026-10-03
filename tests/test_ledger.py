import json
import unittest

from support import LEDGER, ProjectTest


class LedgerTest(ProjectTest):
    def setUp(self):
        super().setUp()
        self.ledger("init", "local")

    def ledger(self, *args):
        return self.run_script(LEDGER, *args)

    def item(self, title, status="Backlog", milestone=None, parent=None):
        ref = self.ledger("create", "--title", title, "--status", status).split()[0].lstrip("#")
        if milestone:
            self.ledger("milestone", "set", ref, milestone)
        if parent:
            self.ledger("parent", ref, parent)
        return ref


class Items(LedgerTest):
    def test_writes_read_their_status_back(self):
        self.assertEqual(self.ledger("create", "--title", "Grid draws", "--status", "Next"), "#1 [Next] Grid draws\n")
        self.assertEqual(self.ledger("move", "1", "in progress"), "#1 now In progress\n")
        self.assertEqual(self.ledger("status", "1"), "In progress\n")

    def test_an_unknown_status_is_refused(self):
        self.item("Grid draws")
        self.assertIn("unknown status", self.refused(LEDGER, "move", "1", "Doing"))

    def test_list_puts_work_in_progress_first(self):
        self.item("Later", "Next")
        self.item("Now", "In progress")
        self.assertEqual(self.ledger("list").splitlines()[0], "#2 [In progress] Now")


class Milestones(LedgerTest):
    def test_closing_the_last_exit_announces_the_goal(self):
        self.ledger("milestone", "create", "--title", "M1 Movement works")
        a = self.item("Grid draws", "Next", "M1")
        b = self.item("Units move", "Next", "M1")
        self.item("Path cost", "Next", parent=b)
        self.assertNotIn("Goal complete", self.ledger("close", a, "--text", "done"))
        self.assertIn("Goal complete: M1 Movement works", self.ledger("close", b, "--text", "done"))

    def test_rename_reorders_the_roadmap_and_keeps_items(self):
        self.ledger("milestone", "create", "--title", "M1 First")
        self.ledger("milestone", "create", "--title", "M2 Second")
        self.item("Exit of first", "Next", "M1")
        self.ledger("milestone", "rename", "M1", "--title", "M3 First")
        tree = json.loads(self.ledger("progress", "--json"))
        self.assertEqual([m["title"] for m in tree], ["M2 Second", "M3 First"])
        self.assertEqual(tree[1]["exits"][0]["title"], "Exit of first")

    def test_rename_to_an_existing_title_is_refused(self):
        self.ledger("milestone", "create", "--title", "M1 First")
        self.ledger("milestone", "create", "--title", "M2 Second")
        self.assertIn("already exists", self.refused(LEDGER, "milestone", "rename", "M1", "--title", "M2 Second"))

    def test_progress_counts_exits_and_tasks(self):
        self.ledger("milestone", "create", "--title", "M1 Movement works")
        e = self.item("Units move", "Next", "M1")
        t = self.item("Path cost", "Next", parent=e)
        self.ledger("close", t, "--text", "done")
        self.assertIn("M1 Movement works  exits 0/1 · tasks 1/1", self.ledger("progress"))


class Brief(LedgerTest):
    def brief(self):
        return self.ledger("brief").splitlines()

    def roadmap(self):
        """M1 done, M2 current with two open exits and one done, M3 later with plenty of work."""
        for title in ("M1 Grid", "M2 Combat loop playable", "M3 Save and load"):
            self.ledger("milestone", "create", "--title", title)
        self.ledger("close", self.item("Grid draws", "Next", "M1"), "--text", "done")
        self.ledger("close", self.item("Attacks resolve", "Next", "M2"), "--text", "done")
        self.current_exit = self.item("Enemies act", "Next", "M2")
        self.item("Turn order shown", "Backlog", "M2")
        self.task = self.item("Enemy picks a target", "In progress", parent=self.current_exit)
        self.later = [self.item(f"Save slot {n}", "Next", "M3") for n in range(1, 31)]
        self.elsewhere = self.item("Save format chosen", "In progress", "M3")
        self.item("Blocked on art", "Blocked", "M3")

    def test_leads_with_the_roadmap_and_the_current_goal(self):
        self.roadmap()
        lines = self.brief()
        self.assertEqual(lines[0], "Milestones: M1 1/1 exits · ▶ M2 1/3 exits · M3 0/32 exits")
        self.assertEqual(lines[1], "Current goal: M2 Combat loop playable")

    def test_lists_the_current_goals_open_exits_and_all_work_in_progress(self):
        self.roadmap()
        text = "\n".join(self.brief())
        self.assertIn(f"#{self.current_exit} [Next] Enemies act", text)
        self.assertIn("[Backlog] Turn order shown", text)
        self.assertIn(f"#{self.task} [In progress] Enemy picks a target", text)
        self.assertIn(f"#{self.elsewhere} [In progress] Save format chosen", text)
        self.assertNotIn("Attacks resolve", text)

    def test_counts_rather_than_lists_work_under_later_goals(self):
        self.roadmap()
        text = "\n".join(self.brief())
        self.assertNotIn("Save slot", text)
        self.assertIn("Not shown: 30 Next, 1 Blocked", text)

    def test_size_follows_the_goal_not_the_board(self):
        self.roadmap()
        before = len(self.brief())
        for n in range(40):
            self.item(f"More later work {n}", "Next", "M3")
        self.assertEqual(len(self.brief()), before)

    def test_names_unplaced_items(self):
        self.roadmap()
        loose = self.item("Nobody's task", "Next")
        self.assertIn(f"Unplaced: #{loose}.", "\n".join(self.brief()))

    def test_a_board_without_goals_lists_its_open_work(self):
        self.item("Grid draws", "In progress")
        self.item("Units move", "Next")
        self.item("Waiting", "Blocked")
        self.assertEqual(self.brief()[:4], ["Board (open items):", "#1 [In progress] Grid draws",
                                            "#2 [Next] Units move", "+1 Blocked (`ledger list --limit 100` shows them)"])

    def test_changes_mode_prints_only_what_changed(self):
        self.item("Grid draws", "Next")
        self.ledger("brief", "--changes")
        self.assertEqual(self.ledger("brief", "--changes"), "")
        self.ledger("move", "1", "In progress")
        self.assertEqual(self.ledger("brief", "--changes"),
                         "Board changes since the last brief:\n#1 [In progress] Grid draws\n")

    def test_never_fails_outside_a_project(self):
        (self.root / ".ledger" / "config.json").unlink()
        self.assertEqual(self.ledger("brief"), "")


if __name__ == "__main__":
    unittest.main()
