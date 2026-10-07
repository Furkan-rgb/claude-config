"""Protect the configured model hierarchy and Fable's read-only consultation boundary."""
import json
import unittest

from support import HOME


def definition(name):
    frontmatter = (HOME / "agents" / f"{name}.md").read_text().split("---", 2)[1]
    return dict(line.split(":", 1) for line in frontmatter.strip().splitlines())


class Agents(unittest.TestCase):
    def test_existing_roles_keep_their_models_and_high_effort(self):
        for name, model in {
            "orchestrator": "opus", "engineer": "opus", "specialist": "opus",
            "implementer": "sonnet", "reviewer": "opus", "scout": "haiku",
        }.items():
            with self.subTest(agent=name):
                fields = definition(name)
                self.assertEqual(fields["model"].strip(), model)
                self.assertEqual(fields["effort"].strip(), "high")

    def test_fable_variants_only_have_read_and_research_tools(self):
        for name, effort in {"fable": "high", "fable-medium": "medium"}.items():
            with self.subTest(agent=name):
                fields = definition(name)
                self.assertEqual(fields["name"].strip(), name)
                self.assertEqual(fields["model"].strip(), "fable")
                self.assertEqual(fields["effort"].strip(), effort)
                self.assertEqual(fields["omitClaudeMd"].strip(), "true")
                self.assertEqual(
                    {tool.strip() for tool in fields["tools"].split(",")},
                    {"Read", "Grep", "Glob", "WebSearch", "WebFetch"},
                )
                # Inherited skills, MCP tools and persistent memory could bypass the
                # bounded brief or the read-only tool boundary.
                self.assertTrue({"skills", "mcpServers", "memory", "hooks"}.isdisjoint(fields))

    def test_orchestrator_can_dispatch_both_variants_without_changing_workers(self):
        tools = definition("orchestrator")["tools"].strip()
        agent_tools = tools.split("Agent(", 1)[1].split(")", 1)[0]
        self.assertEqual(
            {name.strip() for name in agent_tools.split(",")},
            {"scout", "implementer", "engineer", "specialist", "reviewer", "fable", "fable-medium"},
        )
        settings = json.loads((HOME / "settings.json").read_text())
        self.assertIn("fable", settings["availableModels"])
        for name in ("fable", "fable-medium"):
            self.assertNotIn(f"Agent({name})", settings["permissions"]["deny"])


if __name__ == "__main__":
    unittest.main()
