"""Tests."""

import unittest
from testfixtures import compare

from material_ui import MaterialFilterListConfigTranslator
from material_api import MaterialFilter, Materials


class TestMaterialAlertListSettings(unittest.TestCase):
    """Test cases for MaterialFilterListConfigTranslator helpers."""

    def test_translate_from_settings(self):  # pylint: disable=no-self-use
        """Translate from settings test."""

        settings = ['As>=30.00', 'Po>=-102.30', 'Zr>=0.00', 'B>=-100.00']
        expected = [
            MaterialFilter(Materials.ARSENIC, 30.0, True),
            MaterialFilter(Materials.POLONIUM, 2.3, False),
            MaterialFilter(Materials.ZIRCONIUM, 0.0, True),
            MaterialFilter(Materials.BORON, 0.0, False)
        ]
        compare(MaterialFilterListConfigTranslator.translate_from_settings(settings), expected)
        # self.assertEqual('foo'.upper(), 'FOO')

    def test_translate_to_settings(self):  # pylint: disable=no-self-use
        """Translate to settings test."""

        alert_list = [
            MaterialFilter(Materials.ARSENIC, 30.0, True),
            MaterialFilter(Materials.POLONIUM, 2.3, False),
            MaterialFilter(Materials.ZIRCONIUM, 0, True),
            MaterialFilter(Materials.BORON, 0.0, False)
        ]
        expected = ['As>=30.00', 'Po>=-102.30', 'Zr>=0.00', 'B>=-100.00']
        compare(MaterialFilterListConfigTranslator.translate_to_settings(alert_list), expected)


if __name__ == '__main__':
    unittest.main()
