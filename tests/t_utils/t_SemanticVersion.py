# import libraries
import logging
import os, sys
from pathlib import Path
from typing import Final, List
from unittest import TestCase, main
# import locals
_path = Path(os.getcwd()) / "src"
sys.path.insert(0, str(_path.absolute()))
from ogd.common.utils.SemanticVersion import SemanticVersion

def setUpModule():
    from ogd.common.utils.Logger import Logger
    Logger.InitializeLogger(level=logging.ERROR, use_logfile=False)

# TODO : need to test cases where we're comparing directly to a string, and directly to an int.
# TODO : need to test cases where one semver has more points than the other, e.g. 1.1 vs 1.1.1
class t_SemanticVersion_eq(TestCase):
    """
    Tests for equality operator on SemanticVersions.
    """
    def RunAll(self):
        self.test_EqualInvalids()
        self.test_UnequalInvalids()
        self.test_LeftInvalid()
        self.test_RightInvalid()
        print("Ran all t_SemanticVersion_eq tests.")

    def test_EqualInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a == b)
    def test_UnequalInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Not Valid")
        self.assertFalse(a == b)
    def test_LeftInvalid(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("1.2.3")
        self.assertFalse(a == b)
    def test_RightInvalid(self):
        a = SemanticVersion.FromString("1.2.3")
        b = SemanticVersion.FromString("Invalid")
        self.assertFalse(a == b)

    def test_MajorsOnly_Equal(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("1")
        self.assertTrue(a == b)
    def test_MajorsOnly_UnequalMajor(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("2")
        self.assertFalse(a == b)

    def test_MajorMinor_Equal(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a == b)
    def test_MajorMinor_UnequalMajor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("2.10")
        self.assertFalse(a == b)
    def test_MajorMinor_UnequalMinor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.20")
        self.assertFalse(a == b)

    def test_MajorMinorPatch_Equal(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a == b)
    def test_MajorMinorPatch_UnequalMajor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("2.10.101")
        self.assertFalse(a == b)
    def test_MajorMinorPatch_UnequalMinor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.20.101")
        self.assertFalse(a == b)
    def test_MajorMinorPatch_UnequalPatch(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.201")
        self.assertFalse(a == b)

    def test_MajorMinorPatchSuffix_Equal(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a == b)
    def test_MajorMinorPatchSuffix_UnequalMajor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("2.10.101-foo")
        self.assertFalse(a == b)
    def test_MajorMinorPatchSuffix_UnequalMinor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.20.101-foo")
        self.assertFalse(a == b)
    def test_MajorMinorPatchSuffix_UnequalPatch(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.201-foo")
        self.assertFalse(a == b)
    def test_MajorMinorPatchSuffix_UnequalSuffix(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-bar")
        self.assertFalse(a == b)

class t_SemanticVersion_gt(TestCase):
    def RunAll(self):
        self.test_EqualInvalids()
        self.test_UnequalInvalids()
        print("Ran all t_SemanticVersion_eq tests.")

    def test_EqualInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Invalid")
        self.assertFalse(a > b)
    def test_UnequalInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Not Valid")
        self.assertFalse(a > b)
    def test_LeftInvalid(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("1.2.3")
        self.assertFalse(a > b)
    def test_RightInvalid(self):
        a = SemanticVersion.FromString("1.2.3")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a > b)

    def test_MajorsOnly_Equal(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("1")
        self.assertFalse(a > b)
    def test_MajorsOnly_LesserMajor(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("2")
        self.assertFalse(a > b)
    def test_MajorsOnly_GreaterMajor(self):
        a = SemanticVersion.FromString("2")
        b = SemanticVersion.FromString("1")
        self.assertTrue(a > b)

    def test_MajorMinor_Equal(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.10")
        self.assertFalse(a > b)
    def test_MajorMinor_LesserMajor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("2.10")
        self.assertFalse(a > b)
    def test_MajorMinor_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a > b)
    def test_MajorMinor_LesserMinor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.20")
        self.assertFalse(a > b)
    def test_MajorMinor_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a > b)

    def test_MajorMinorPatch_Equal(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a > b)
    def test_MajorMinorPatch_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("2.10.101")
        self.assertFalse(a > b)
    def test_MajorMinorPatch_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a > b)
    def test_MajorMinorPatch_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.20.101")
        self.assertFalse(a > b)
    def test_MajorMinorPatch_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a > b)
    def test_MajorMinorPatch_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.201")
        self.assertFalse(a > b)
    def test_MajorMinorPatch_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a > b)

    def test_MajorMinorPatchSuffix_Equal(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a > b)
    def test_MajorMinorPatchSuffix_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("2.10.101-foo")
        self.assertFalse(a > b)
    def test_MajorMinorPatchSuffix_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a > b)
    def test_MajorMinorPatchSuffix_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.20.101-foo")
        self.assertFalse(a > b)
    def test_MajorMinorPatchSuffix_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a > b)
    def test_MajorMinorPatchSuffix_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.201-foo")
        self.assertFalse(a > b)
    def test_MajorMinorPatchSuffix_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a > b)
    def test_MajorMinorPatchSuffix_UnequalSuffix(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-bar")
        self.assertFalse(a > b)

class t_SemanticVersion_ge(TestCase):
    def RunAll(self):
        self.test_EqualInvalids()
        self.test_UnequalInvalids()
        print("Ran all t_SemanticVersion_eq tests.")

    def test_EqualInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a >= b)
    def test_UnequalInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Not Valid")
        self.assertFalse(a >= b)
    def test_LeftInvalid(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("1.2.3")
        self.assertFalse(a >= b)
    def test_RightInvalid(self):
        a = SemanticVersion.FromString("1.2.3")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a >= b)

    def test_MajorsOnly_Equal(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("1")
        self.assertTrue(a >= b)
    def test_MajorsOnly_LesserMajor(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("2")
        self.assertFalse(a >= b)
    def test_MajorsOnly_GreaterMajor(self):
        a = SemanticVersion.FromString("2")
        b = SemanticVersion.FromString("1")
        self.assertTrue(a >= b)

    def test_MajorMinor_Equal(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a >= b)
    def test_MajorMinor_LesserMajor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("2.10")
        self.assertFalse(a >= b)
    def test_MajorMinor_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a >= b)
    def test_MajorMinor_LesserMinor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.20")
        self.assertFalse(a >= b)
    def test_MajorMinor_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a >= b)

    def test_MajorMinorPatch_Equal(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a >= b)
    def test_MajorMinorPatch_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("2.10.101")
        self.assertFalse(a >= b)
    def test_MajorMinorPatch_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a >= b)
    def test_MajorMinorPatch_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.20.101")
        self.assertFalse(a >= b)
    def test_MajorMinorPatch_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a >= b)
    def test_MajorMinorPatch_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.201")
        self.assertFalse(a >= b)
    def test_MajorMinorPatch_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a >= b)

    def test_MajorMinorPatchSuffix_Equal(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a >= b)
    def test_MajorMinorPatchSuffix_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("2.10.101-foo")
        self.assertFalse(a >= b)
    def test_MajorMinorPatchSuffix_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a >= b)
    def test_MajorMinorPatchSuffix_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.20.101-foo")
        self.assertFalse(a >= b)
    def test_MajorMinorPatchSuffix_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a >= b)
    def test_MajorMinorPatchSuffix_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.201-foo")
        self.assertFalse(a >= b)
    def test_MajorMinorPatchSuffix_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a >= b)
    def test_MajorMinorPatchSuffix_UnequalSuffix(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-bar")
        self.assertFalse(a >= b)

class t_SemanticVersion_lt(TestCase):
    def RunAll(self):
        self.test_EqualInvalids()
        self.test_UnequalInvalids()
        print("Ran all t_SemanticVersion_eq tests.")

    def test_EqualInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a < b)
    def test_UnequalInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Not Valid")
        self.assertTrue(a < b)
    def test_LeftInvalid(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("1.2.3")
        self.assertTrue(a < b)
    def test_RightInvalid(self):
        a = SemanticVersion.FromString("1.2.3")
        b = SemanticVersion.FromString("Invalid")
        self.assertFalse(a < b)

    def test_MajorsOnly_Equal(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("1")
        self.assertFalse(a < b)
    def test_MajorsOnly_LesserMajor(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("2")
        self.assertTrue(a < b)
    def test_MajorsOnly_GreaterMajor(self):
        a = SemanticVersion.FromString("2")
        b = SemanticVersion.FromString("1")
        self.assertFalse(a < b)

    def test_MajorMinor_Equal(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.10")
        self.assertFalse(a < b)
    def test_MajorMinor_LesserMajor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("2.10")
        self.assertTrue(a < b)
    def test_MajorMinor_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10")
        b = SemanticVersion.FromString("1.10")
        self.assertFalse(a < b)
    def test_MajorMinor_LesserMinor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.20")
        self.assertTrue(a < b)
    def test_MajorMinor_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20")
        b = SemanticVersion.FromString("1.10")
        self.assertFalse(a < b)

    def test_MajorMinorPatch_Equal(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a < b)
    def test_MajorMinorPatch_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("2.10.101")
        self.assertTrue(a < b)
    def test_MajorMinorPatch_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a < b)
    def test_MajorMinorPatch_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.20.101")
        self.assertTrue(a < b)
    def test_MajorMinorPatch_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a < b)
    def test_MajorMinorPatch_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.201")
        self.assertTrue(a < b)
    def test_MajorMinorPatch_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a < b)

    def test_MajorMinorPatchSuffix_Equal(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a < b)
    def test_MajorMinorPatchSuffix_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("2.10.101-foo")
        self.assertTrue(a < b)
    def test_MajorMinorPatchSuffix_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a < b)
    def test_MajorMinorPatchSuffix_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.20.101-foo")
        self.assertTrue(a < b)
    def test_MajorMinorPatchSuffix_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a < b)
    def test_MajorMinorPatchSuffix_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.201-foo")
        self.assertTrue(a < b)
    def test_MajorMinorPatchSuffix_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a < b)
    def test_MajorMinorPatchSuffix_UnequalSuffix(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-bar")
        self.assertFalse(a < b)

class t_SemanticVersion_le(TestCase):
    def RunAll(self):
        self.test_EqualInvalids()
        self.test_UnequalInvalids()
        print("Ran all t_SemanticVersion_eq tests.")

    def test_EqualInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Invalid")
        self.assertTrue(a <= b)
    def test_UnequalInvalids(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("Not Valid")
        self.assertTrue(a <= b)
    def test_LeftInvalid(self):
        a = SemanticVersion.FromString("Invalid")
        b = SemanticVersion.FromString("1.2.3")
        self.assertTrue(a <= b)
    def test_RightInvalid(self):
        a = SemanticVersion.FromString("1.2.3")
        b = SemanticVersion.FromString("Invalid")
        self.assertFalse(a <= b)

    def test_MajorsOnly_Equal(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("1")
        self.assertTrue(a <= b)
    def test_MajorsOnly_LesserMajor(self):
        a = SemanticVersion.FromString("1")
        b = SemanticVersion.FromString("2")
        self.assertTrue(a <= b)
    def test_MajorsOnly_GreaterMajor(self):
        a = SemanticVersion.FromString("2")
        b = SemanticVersion.FromString("1")
        self.assertFalse(a <= b)

    def test_MajorMinor_Equal(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.10")
        self.assertTrue(a <= b)
    def test_MajorMinor_LesserMajor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("2.10")
        self.assertTrue(a <= b)
    def test_MajorMinor_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10")
        b = SemanticVersion.FromString("1.10")
        self.assertFalse(a <= b)
    def test_MajorMinor_LesserMinor(self):
        a = SemanticVersion.FromString("1.10")
        b = SemanticVersion.FromString("1.20")
        self.assertTrue(a <= b)
    def test_MajorMinor_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20")
        b = SemanticVersion.FromString("1.10")
        self.assertFalse(a <= b)

    def test_MajorMinorPatch_Equal(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertTrue(a <= b)
    def test_MajorMinorPatch_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("2.10.101")
        self.assertTrue(a <= b)
    def test_MajorMinorPatch_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a <= b)
    def test_MajorMinorPatch_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.20.101")
        self.assertTrue(a <= b)
    def test_MajorMinorPatch_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a <= b)
    def test_MajorMinorPatch_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101")
        b = SemanticVersion.FromString("1.10.201")
        self.assertTrue(a <= b)
    def test_MajorMinorPatch_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201")
        b = SemanticVersion.FromString("1.10.101")
        self.assertFalse(a <= b)

    def test_MajorMinorPatchSuffix_Equal(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertTrue(a <= b)
    def test_MajorMinorPatchSuffix_LesserMajor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("2.10.101-foo")
        self.assertTrue(a <= b)
    def test_MajorMinorPatchSuffix_GreaterMajor(self):
        a = SemanticVersion.FromString("2.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a <= b)
    def test_MajorMinorPatchSuffix_LesserMinor(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.20.101-foo")
        self.assertTrue(a <= b)
    def test_MajorMinorPatchSuffix_GreaterMinor(self):
        a = SemanticVersion.FromString("1.20.101-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a <= b)
    def test_MajorMinorPatchSuffix_LesserPatch(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.201-foo")
        self.assertTrue(a <= b)
    def test_MajorMinorPatchSuffix_GreaterPatch(self):
        a = SemanticVersion.FromString("1.10.201-foo")
        b = SemanticVersion.FromString("1.10.101-foo")
        self.assertFalse(a <= b)
    def test_MajorMinorPatchSuffix_UnequalSuffix(self):
        a = SemanticVersion.FromString("1.10.101-foo")
        b = SemanticVersion.FromString("1.10.101-bar")
        self.assertFalse(a <= b)

if __name__ == '__main__':
    main()
