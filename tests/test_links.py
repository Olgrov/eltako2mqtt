from pathlib import Path
import tempfile
import unittest

from tools.check_links import check_documents, heading_ids, markdown_links


class LinkContracts(unittest.TestCase):
    def test_heading_ids_cover_unicode_duplicates_and_markdown(self):
        self.assertEqual(
            heading_ids("# Konfiguration\n## Konfiguration\n### **Änderungen** `API`\n"),
            {"konfiguration", "konfiguration-1", "änderungen-api"},
        )

    def test_headings_inside_fences_are_not_valid_targets(self):
        self.assertEqual(
            heading_ids("# Real\n```python\n# Not a heading\n```\n"),
            {"real"},
        )

    def test_setext_and_explicit_html_anchors(self):
        ids = heading_ids("Title\n=====\n<a id=\"legacy-anchor\"></a>\n")
        self.assertEqual(ids, {"title", "legacy-anchor"})

    def test_reference_links_and_images(self):
        links = list(markdown_links("[Doc][ref]\n![Image](icon.png)\n[ref]: guide.md#start\n"))
        self.assertIn((1, "guide.md#start"), links)
        self.assertIn((2, "icon.png"), links)
        self.assertIn((3, "guide.md#start"), links)

    def test_missing_reference_is_reported(self):
        self.assertIn((1, "unresolved-reference:missing"),
                      list(markdown_links("[Doc][missing]")))

    def test_links_inside_fenced_examples_are_ignored(self):
        self.assertEqual(list(markdown_links("```\n[example](missing.md)\n```\n")), [])

    def test_files_and_fragments_are_checked_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text(
                "[Good](docs/guide.md#überblick)\n"
                "[Bad anchor](docs/guide.md#missing)\n"
                "[Bad file](missing.md)\n"
                "[Outside](../outside.md)\n"
                "[External](https://example.invalid/not-requested)\n",
                encoding="utf-8",
            )
            (root / "docs").mkdir()
            (root / "docs/guide.md").write_text("# Überblick\n", encoding="utf-8")
            checked, problems = check_documents(root)
            self.assertEqual(checked, 4)
            self.assertEqual(len(problems), 3)
            self.assertTrue(any("missing anchor" in problem for problem in problems))
            self.assertTrue(any("missing file" in problem for problem in problems))
            self.assertTrue(any("escapes repository" in problem for problem in problems))
