import ast
from pathlib import Path
import re
import unittest


class RegexLiteralSafetyTests(unittest.TestCase):
    """Catch accidental literal regex escapes such as r"\\\\b" or r"\\\\s"."""

    def test_regex_calls_do_not_use_doubled_standard_escapes(self):
        root = Path(__file__).resolve().parents[1] / "brain" / "logic"
        problems = []
        for path in root.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if not isinstance(node.func.value, ast.Name) or node.func.value.id != "re":
                    continue
                if node.func.attr not in {"search", "sub", "match", "fullmatch", "findall", "finditer"}:
                    continue
                if not node.args:
                    continue
                pattern = node.args[0]
                if not isinstance(pattern, ast.Constant) or not isinstance(pattern.value, str):
                    continue
                if re.search(r"\\\\[bBsSdDwW]", pattern.value):
                    problems.append(f"{path.name}:{node.lineno}: {pattern.value!r}")
        self.assertEqual(problems, [], "Suspicious doubled regex escapes:\n" + "\n".join(problems))


if __name__ == "__main__":
    unittest.main()
