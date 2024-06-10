# import standard libraries
import logging
import math
import re
from typing import Any, Dict, Optional, List

# import 3rd-party libraries

# import OGD libraries
from ogd.core.utils.Logger import Logger

# import locals

class SemanticVersion:

    # *** BUILT-INS & PROPERTIES ***

    def __init__(self, major:Optional[int], minor:Optional[int]=None, patch:Optional[int]=None, suffix:Optional[str]=None, suffix_ver:Optional[int]=None, fallback:Optional[str]=None):
        """
        Constructor for a SemanticVersion.

        Any parameter may be set to None; if nothing at all is given, the version will be treated as 0.0.0.

        :param major: The major version number
        :type major: Optional[int]
        :param minor: The minor version number, defaults to None
        :type minor: Optional[int], optional
        :param patch: The patch version number, defaults to None
        :type patch: Optional[int], optional
        :param suffix: An optional suffix for the version, such as 'alpha' or 'beta', defaults to None
        :type suffix: Optional[str], optional
        :param suffix_ver: An optional suffix version, allowing for overall suffixes such as 'alpha1' or 'beta2', defaults to None
        :type suffix_ver: Optional[int], optional
        :param fallback: _description_, defaults to None
        :type fallback: Optional[str], optional
        """
        self._major      : Optional[int] = max(0, major) if major is not None else None
        self._minor      : Optional[int] = max(0, minor) if minor is not None else None
        self._patch      : Optional[int] = max(0, patch) if patch is not None else None
        self._suffix     : Optional[str] = suffix
        self._suffix_ver : Optional[int] = max(0, suffix_ver) if suffix_ver is not None else None
        self._fallback   : Optional[str] = fallback

    def __repr__(self) -> str:
        return f"SemanticVersion : {self}"

    def __str__(self) -> str:
        _major      = str(self._major)      if self._major      is not None else None
        _minor      = f".{self._minor}"     if self._minor      is not None else None
        _patch      = f".{self._patch}"     if self._patch      is not None else None
        _suffix     = f"-{self._suffix}"    if self._suffix     is not None else None
        _suffix_ver = f"{self._suffix_ver}" if self._suffix_ver is not None else None

        return f"{_major}{_minor or ''}{_patch or ''}{_suffix or ''}{_suffix_ver or ''}" if self.IsValid else str(self._fallback)

    def __eq__(self, RHS:Any) -> bool:
        """
        _summary_

        :param RHS: _description_
        :type RHS: Any
        :raises TypeError: _description_
        :raises TypeError: _description_
        :raises TypeError: _description_
        :return: _description_
        :rtype: bool
        """
    # 1. Handle cases where RHS is not a SemanticVersion.
        if not isinstance(RHS, SemanticVersion):
            if isinstance(RHS, str):
                RHS = SemanticVersion.FromString(RHS, verbose=False)
            elif isinstance(RHS, int):
                RHS = SemanticVersion(major=RHS)
            else:
                return False
        if self.IsValid and RHS.IsValid:
    # 2. Handle general case, where we're just comparing each piece
            return  self._CompMajor  == RHS._CompMajor  \
                and self._CompMinor  == RHS._CompMinor  \
                and self._CompPatch  == RHS._CompPatch  \
                and self._suffix     == RHS._suffix     \
                and self._suffix_ver == RHS._suffix_ver
        else:
            return str(self) == str(RHS)

    def __gt__(self, RHS:Any) -> bool:
    # 1. Handle cases where RHS is not a SemanticVersion, or self is not a valid SemVer string.
        # a. If we're not valid, we're not bigger
        if not self.IsValid:
            return False
        # b. If they're not SemVer, convert
        if not isinstance(RHS, SemanticVersion):
            if isinstance(RHS, str):
                RHS = SemanticVersion.FromString(RHS, verbose=False)
            elif isinstance(RHS, int):
                RHS = SemanticVersion(major=RHS)
            else:
                raise TypeError(f"'>' not supported between instances '{type(self)}' and '{type(RHS)}'")
        # c. If they're not valid, but we are, we're bigger
        if not RHS.IsValid:
            return True
    # 2. Handle general case, where we're just comparing each piece
        # a. If our major is bigger, we're bigger
        if self._CompMajor > RHS._CompMajor:
            return True
        # b. If majors are equal, compare minors
        elif self._CompMajor == RHS._CompMajor:
        # c. If our minor is bigger, we're bigger
            if self._CompMinor > RHS._CompMinor:
                return True
        # d. If minors are equal, compare patches
            elif self._CompMinor == RHS._CompMinor:
        # e. If our patch is bigger, we're bigger
                if self._CompPatch > RHS._CompPatch:
                    return True
        # f. Otherwise, we're not bigger.
        return False

    def __ge__(self, RHS:Any):
    # 1. Handle cases where RHS is not a SemanticVersion, or self is not a valid SemVer string.
        # a. If we're not valid, we're not bigger, so return whether we're equal
        if not self.IsValid:
            return self == RHS
        # b. If they're not SemVer, convert
        if not isinstance(RHS, SemanticVersion):
            if isinstance(RHS, str):
                RHS = SemanticVersion.FromString(RHS, verbose=False)
            elif isinstance(RHS, int):
                RHS = SemanticVersion(major=RHS)
            else:
                raise TypeError(f"'>=' not supported between instances '{type(self)}' and '{type(RHS)}'")
        # c. If they're not valid, but we are, we're bigger
        if not RHS.IsValid:
            return True
    # 2. Handle general case, where we're just comparing each piece
        # a. If our major is bigger, we're bigger
        if self._CompMajor > RHS._CompMajor:
            return True
        # b. If majors are equal, compare minors
        elif self._CompMajor == RHS._CompMajor:
        # c. If our minor is bigger, we're bigger
            if self._CompMinor > RHS._CompMinor:
                return True
        # d. If minors are equal, compare patches
            elif self._CompMinor == RHS._CompMinor:
        # e. If our patch is bigger, we're bigger
                if self._CompPatch > RHS._CompPatch:
                    return True
        # d. If patches are equal, check if we're totally equal.
                elif self._CompPatch == RHS._CompPatch:
                    return self._suffix == RHS._suffix and self._suffix_ver == RHS._suffix_ver
        # f. Otherwise, we're not bigger.
        return False

    def __lt__(self, RHS:Any) -> bool:
    # 1. Handle cases where RHS is not a SemanticVersion, or self is not a valid SemVer string.
        # a. If we're not valid, we're smaller
        if not self.IsValid:
            return True
        # b. If they're not SemVer, convert
        if not isinstance(RHS, SemanticVersion):
            if isinstance(RHS, str):
                RHS = SemanticVersion.FromString(RHS, verbose=False)
            elif isinstance(RHS, int):
                RHS = SemanticVersion(major=RHS)
            else:
                raise TypeError(f"'<' not supported between instances '{type(self)}' and '{type(RHS)}'")
        # c. If they're not valid, but we are, we're not smaller
        if not RHS.IsValid:
            return False
    # 2. Handle general case, where we're just comparing each piece
        # a. If our major is smaller, we're smaller
        if self._CompMajor < RHS._CompMajor:
            return True
        # b. If majors are equal, compare minors
        elif self._CompMajor == RHS._CompMajor:
        # c. If our minor is smaller, we're smaller
            if self._CompMinor < RHS._CompMinor:
                return True
        # d. If minors are equal, compare patches
            elif self._CompMinor == RHS._CompMinor:
        # e. If our patch is smaller, we're smaller
                if self._CompPatch < RHS._CompPatch:
                    return True
        # f. Otherwise, we're not smaller.
        return False

    def __le__(self, RHS:Any):
    # 1. Handle cases where RHS is not a SemanticVersion, or self is not a valid SemVer string.
        # a. If we're not valid, we're smaller (or equal)
        if not self.IsValid:
            return True
        # b. If they're not SemVer, convert
        if not isinstance(RHS, SemanticVersion):
            if isinstance(RHS, str):
                RHS = SemanticVersion.FromString(RHS, verbose=False)
            elif isinstance(RHS, int):
                RHS = SemanticVersion(major=RHS)
            else:
                raise TypeError(f"'<=' not supported between instances '{type(self)}' and '{type(RHS)}'")
        # c. If they're not valid, but we are, we're not smaller
        if not RHS.IsValid:
            return False
    # 2. Handle general case, where we're just comparing each piece
        # a. If our major is smaller, we're smaller
        if self._CompMajor < RHS._CompMajor:
            return True
        # b. If majors are equal, compare minors
        elif self._CompMajor == RHS._CompMajor:
        # c. If our minor is smaller, we're smaller.
            if self._CompMinor < RHS._CompMinor:
                return True
        # d. If minors are equal, compare patches
            elif self._CompMinor == RHS._CompMinor:
        # e. If our patch is smaller, we're smaller
                if self._CompPatch < RHS._CompPatch:
                    return True
        # d. If patches are equal, check if we're totally equal.
                elif self._CompPatch == RHS._CompPatch:
                    return self._suffix == RHS._suffix and self._suffix_ver == RHS._suffix_ver
        # f. Otherwise, we're not bigger.
        return False

    # *** PUBLIC STATICS ***

    @staticmethod
    def FromString(semver:str, verbose:bool=True) -> 'SemanticVersion':
        pieces = re.split('\.|-', semver)
        if verbose:
            Logger.Log(f"Pieces: {pieces}", logging.DEBUG)

        return SemanticVersion._parseMajor(semver=semver, pieces=pieces, verbose=verbose)

    # *** PUBLIC METHODS ***

    # *** PROPERTIES ***

    @property
    def IsValid(self) -> bool:
        return self._major is not None

    @property
    def _CompMajor(self) -> int:
        return self._major or 0

    @property
    def _CompMinor(self) -> int:
        return self._minor or 0

    @property
    def _CompPatch(self) -> int:
        return self._patch or 0

    @staticmethod
    def _parseMajor(semver:str, pieces:List[str], verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _major : int
        try:
            _major = max(0, int(pieces[0]))
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
            _minor = max(0, int(pieces[0]))
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
            _fix = max(0, int(pieces[0]))
        except ValueError as err:
            _default_ver = f"{major}.{minor}"
            if verbose:
                Logger.Log(f"Could not parse semantic version from {semver}, {pieces[0]} was not an int! Defaulting to version={_default_ver}\nError Details: {err}", level=logging.WARN)
            ret_val = SemanticVersion(major=major, minor=minor)
        else:
            if len(pieces) > 1:
                ret_val = SemanticVersion._parseSuffix(semver=semver, pieces=pieces[1:], major=major, minor=minor, fix=_fix, verbose=verbose)
            else:
                ret_val = SemanticVersion(major=major, minor=minor, patch=_fix)
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
            ret_val = SemanticVersion(major=major, minor=minor, patch=fix, suffix=_suffix)
        return ret_val

    @staticmethod
    def _parseSuffixVersion(semver:str, pieces:List[str], major:int, minor:int, fix:int, suffix:str, verbose:bool) -> 'SemanticVersion':
        ret_val : 'SemanticVersion'

        _suffix_version : int
        try:
            _suffix_version = max(0, int(pieces[0]))
        except ValueError as err:
            _default_ver = f"{major}.{minor}.{fix}-{suffix}"
            if verbose:
                Logger.Log(f"Could not parse semantic version from {semver}, {pieces[0]} was not an int! Defaulting to version={_default_ver}\nError Details: {err}", level=logging.WARN)
            ret_val = SemanticVersion(major=major, minor=minor, patch=fix, suffix=suffix)
        else:
            ret_val = SemanticVersion(major=major, minor=minor, patch=fix, suffix=suffix, suffix_ver=_suffix_version)
            if len(pieces) > 1 and verbose:
                Logger.Log(f"Semantic version string {semver} had excess parts, reducing to version={ret_val}", level=logging.WARN)
        finally:
            return ret_val