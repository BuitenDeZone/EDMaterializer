import unittest
from testfixtures import compare

from material_ui import MaterialAlertListSettings
from material_api import *


class TestMaterialAlertListSettings(unittest.TestCase):

    def test_translate_from_settings(self):
        settings = ['As>=30.00', 'Po>=-102.30', 'Zr>=0.00', 'B>=-100.00']
        expected = [
            MaterialAlert(Materials.ARSENIC, 30.0, True),
            MaterialAlert(Materials.POLONIUM, 2.3, False),
            MaterialAlert(Materials.ZIRCONIUM, 0.0, True),
            MaterialAlert(Materials.BORON, 0.0, False)
        ]
        compare(MaterialAlertListSettings.translate_from_settings(settings), expected)
        # self.assertEqual('foo'.upper(), 'FOO')

    def test_translate_to_settings(self):
        alert_list = [
            MaterialAlert(Materials.ARSENIC, 30.0, True),
            MaterialAlert(Materials.POLONIUM, 2.3, False),
            MaterialAlert(Materials.ZIRCONIUM, 0, True),
            MaterialAlert(Materials.BORON, 0.0, False)
        ]
        expected = ['As>=30.00', 'Po>=-102.30', 'Zr>=0.00', 'B>=-100.00']
        compare(MaterialAlertListSettings.translate_to_settings(alert_list), expected)


if __name__ == '__main__':
    unittest.main()