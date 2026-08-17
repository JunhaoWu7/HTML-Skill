import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build  # noqa: E402


class BuildTests(unittest.TestCase):
    def test_default_config_is_complete_and_safe(self):
        config = build.load_config()
        self.assertEqual(config["preview"]["bind"], "127.0.0.1")
        self.assertIn("HTML展示", config["agent"]["trigger_phrases"])

    def test_frontmatter(self):
        meta, body = build.parse_frontmatter("---\ntitle: 测试\nstatus: 完成\n---\n正文")
        self.assertEqual(meta["title"], "测试")
        self.assertEqual(body, "正文")

    def test_markdown_components(self):
        markdown = """## 结论

:::metrics
完成率 | 90% | +10%
:::

:::progress
设计 | 80 | 正常
:::

:::feedback
positive | 很清楚 | 用户
:::
"""
        rendered, toc = build.render_markdown(markdown)
        self.assertIn('class="metrics"', rendered)
        self.assertIn('style="width:80%"', rendered)
        self.assertIn('class="feedback positive"', rendered)
        self.assertEqual(toc, [("结论", "section-1")])

    def test_full_build(self):
        count = build.build()
        self.assertGreaterEqual(count, 1)
        self.assertTrue((build.PUBLIC_DIR / "index.html").is_file())
        manifest = json.loads((build.PUBLIC_DIR / "reports.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["title"], "HTML 汇报工作流已就绪")


if __name__ == "__main__":
    unittest.main()
