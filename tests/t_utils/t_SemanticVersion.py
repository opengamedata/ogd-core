# import libraries
from typing import Final, List
from unittest import TestCase, main
# import locals
from ogd.core.utils.SemanticVersion import SemanticVersion

class t_SemanticVersion_eq(TestCase):
    def RunAll(self):
        self.test_EqualInvalids()
        self.test_UnequalInvalids()
        print("Ran all t_SemanticVersion_eq tests.")

    def test_EqualInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a == b)
    def test_UnequalInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Not Valid")
        self.assertFalse(a == b)

    def test_EqualMajorsOnly(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("1")
        self.assertTrue(a == b)
    def test_UnequalMajorsOnly(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("2")
        self.assertFalse(a == b)

if __name__ == '__main__':
    main()
