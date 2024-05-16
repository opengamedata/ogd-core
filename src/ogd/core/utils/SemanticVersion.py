# import standard libraries
import logging
import re
from typing import Any, Dict, Optional, List

# import 3rd-party libraries

# import OGD libraries
from ogd.core.utils.Logger import Logger

# import locals

class SemanticVersion:
    def __init__(self, major:Optional[int], minor:Optional[int]=None, fix:Optional[int]=None, suffix:Optional[str]=None, suffix_ver:Optional[int]=None, fallback:Optional[str]=None):
        self._major      : Optional[int] = major
        self._minor      : Optional[int] = minor
        self._fix        : Optional[int] = fix
        self._suffix     : Optional[str] = suffix
        self._suffix_ver : Optional[int] = suffix_ver
        self._fallback   : Optional[str] = fallback

    def __repr__(self) -> str:
        return f"SemanticVersion : {self}"

    def __str__(self) -> str:
        _major      = str(self._major)       if self._major      is not None else None
        _minor      = f".{self._minor}"      if self._minor      is not None else None
        _fix        = f".{self._fix}"        if self._fix        is not None else None
        _suffix     = f"-{self._suffix}"     if self._suffix     is not None else None
        _suffix_ver = f".{self._suffix_ver}" if self._suffix_ver is not None else None

        return f"{_major}{_minor or ''}{_fix or ''}{_suffix or ''}{_suffix_ver or ''}" if _major is not None else str(self._fallback)

    def __eq__(self, other) -> bool:
        if type(other) != type(self):
            if isinstance(other, str):
                return self == SemanticVersion.FromString(other, verbose=False)
            return False
        if self._major is None or other._major is None:
            return False
        if self._major       == other._major  \
        and self._minor      == other._minor  \
        and self._fix        == other._fix    \
        and self._suffix     == other._suffix \
        and self._suffix_ver == other._suffix_ver:
            return True
        return False


    @staticmethod
    def FromString(semver:str, verbose:bool=True) -> 'SemanticVersion':
        pieces = re.split('\.|-', semver)
        if verbose:
            Logger.Log(f"Pieces: {pieces}", logging.DEBUG)

        return SemanticVersion._parseMajor(semver=semver, pieces=pieces, verbose=verbose)

    @staticmethod
    def _parseMajor(semver:str, pieces:List[str], verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _major : int
        try:
            _major = int(pieces[0])
        except ValueError as err:
            _default_ver = semver
            if verbose:
                Logger.Log(f"Could not parse semantic version from {semver}, {pieces[0]} was not an int! Defaulting to version={_default_ver}\nError Details: {err}", level=logging.WARN)
            ret_val = SemanticVersion(major=None, fallback=semver)
        else:
            if len(pieces) > 1:
                ret_val = SemanticVersion._parseMinor(semver=semver, pieces=pieces[1:], major=_major, verbose=verbose)
            else:
                ret_val = SemanticVersion(major=_major)
        finally:
            return ret_val
                

    @staticmethod
    def _parseMinor(semver:str, pieces:List[str], major:int, verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _minor : int
        try:
            _minor = int(pieces[0])
        except ValueError as err:
            _default_ver = str(major)
            if verbose:
                Logger.Log(f"Could not parse semantic version from {semver}, {pieces[0]} was not an int! Defaulting to version={_default_ver}\nError Details: {err}", level=logging.WARN)
            ret_val = SemanticVersion(major=major)
        else:
            if len(pieces) > 1:
                ret_val = SemanticVersion._parseFix(semver=semver, pieces=pieces[1:], major=major, minor=_minor, verbose=verbose)
            else:
                ret_val = SemanticVersion(major=major, minor=_minor)
        finally:
            return ret_val

    @staticmethod
    def _parseFix(semver:str, pieces:List[str], major:int, minor:int, verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _fix : int
        try:
            _fix = int(pieces[0])
        except ValueError as err:
            _default_ver = f"{major}.{minor}"
            if verbose:
                Logger.Log(f"Could not parse semantic version from {semver}, {pieces[0]} was not an int! Defaulting to version={_default_ver}\nError Details: {err}", level=logging.WARN)
            ret_val = SemanticVersion(major=major, minor=minor)
        else:
            if len(pieces) > 1:
                ret_val = SemanticVersion._parseSuffix(semver=semver, pieces=pieces[1:], major=major, minor=minor, fix=_fix, verbose=verbose)
            else:
                ret_val = SemanticVersion(major=major, minor=minor, fix=_fix)
        finally:
            return ret_val

    @staticmethod
    def _parseSuffix(semver:str, pieces:List[str], major:int, minor:int, fix:int, verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _suffix : str
        _suffix = pieces[0]
        if len(pieces) > 1:
            ret_val = SemanticVersion._parseSuffixVersion(semver=semver, pieces=pieces[1:], major=major, minor=minor, fix=fix, suffix=_suffix, verbose=verbose)
        else:
            ret_val = SemanticVersion(major=major, minor=minor, fix=fix, suffix=_suffix)
        return ret_val

    @staticmethod
    def _parseSuffixVersion(semver:str, pieces:List[str], major:int, minor:int, fix:int, suffix:str, verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _suffix_version : int
        try:
            _suffix_version = int(pieces[0])
        except ValueError as err:
            _default_ver = f"{major}.{minor}.{fix}-{suffix}"
            if verbose:
                Logger.Log(f"Could not parse semantic version from {semver}, {pieces[0]} was not an int! Defaulting to version={_default_ver}\nError Details: {err}", level=logging.WARN)
            ret_val = SemanticVersion(major=major, minor=minor, fix=fix, suffix=suffix)
        else:
            ret_val = SemanticVersion(major=major, minor=minor, fix=fix, suffix=suffix, suffix_ver=_suffix_version)
            if len(pieces) > 1 and verbose:
                Logger.Log(f"Semantic version string {semver} had excess parts, reducing to version={ret_val}", level=logging.WARN)
        finally:
            return ret_val