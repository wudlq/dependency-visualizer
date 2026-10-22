"""Тесты разбора строк зависимостей."""

import unittest

from requirements import (RequirementError, direct_dependencies,
                          normalize_name, parse_requirement)


class ParseRequirementTest(unittest.TestCase):
    """Проверка parse_requirement на разных формах записи."""

    def test_name_only(self):
        """Только имя пакета."""
        requirement = parse_requirement("tzdata")
        self.assertEqual(requirement.name, "tzdata")
        self.assertEqual(requirement.specifier, "")
        self.assertEqual(requirement.marker, "")

    def test_specifier(self):
        """Имя и ограничения версии."""
        requirement = parse_requirement("idna<4,>=2.5")
        self.assertEqual(requirement.name, "idna")
        self.assertEqual(requirement.specifier, "<4,>=2.5")

    def test_specifier_in_parentheses(self):
        """Старая форма записи версии в скобках."""
        requirement = parse_requirement("requests (>=2.0)")
        self.assertEqual(requirement.specifier, ">=2.0")

    def test_extras_and_marker(self):
        """Дополнения в квадратных скобках и маркер окружения."""
        requirement = parse_requirement(
            'uvicorn[standard]>=0.12; python_version < "3.10"')
        self.assertEqual(requirement.name, "uvicorn")
        self.assertEqual(requirement.extras, ["standard"])
        self.assertEqual(requirement.specifier, ">=0.12")
        self.assertEqual(requirement.marker, 'python_version < "3.10"')

    def test_optional(self):
        """Зависимость только для дополнения."""
        requirement = parse_requirement('PySocks>=1.5.6; extra == "socks"')
        self.assertTrue(requirement.is_optional())
        self.assertFalse(parse_requirement("idna").is_optional())

    def test_bad_requirements(self):
        """Строки без имени и с незакрытой скобкой."""
        with self.assertRaises(RequirementError):
            parse_requirement(">=1.0")
        with self.assertRaises(RequirementError):
            parse_requirement("pkg[extra>=1.0")

    def test_str(self):
        """Строка для вывода."""
        text = 'numpy >=2.0 ; python_version < "3.14"'
        self.assertEqual(str(parse_requirement(
            'numpy>=2.0; python_version < "3.14"')), text)

    def test_normalize_name(self):
        """Нормализация имени по PEP 503."""
        self.assertEqual(normalize_name("Foo_Bar.baz"), "foo-bar-baz")


class DirectDependenciesTest(unittest.TestCase):
    """Проверка отбора обязательных прямых зависимостей."""

    def test_skip_extras(self):
        """Зависимости для дополнений пропускаются, порядок сохраняется."""
        result, bad = direct_dependencies([
            "charset_normalizer<4,>=2",
            'PySocks!=1.5.7,>=1.5.6; extra == "socks"',
            "certifi>=2017.4.17",
        ])
        self.assertEqual([r.name for r in result],
                         ["charset_normalizer", "certifi"])
        self.assertEqual(bad, [])

    def test_bad_lines(self):
        """Неразборчивые строки возвращаются отдельно."""
        result, bad = direct_dependencies(["six", "???"])
        self.assertEqual([r.name for r in result], ["six"])
        self.assertEqual(bad, ["???"])

    def test_empty(self):
        """Пакет без зависимостей."""
        self.assertEqual(direct_dependencies([]), ([], []))


if __name__ == "__main__":
    unittest.main()
