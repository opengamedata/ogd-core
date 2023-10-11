import logging
from typing import Any, List

from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData
from utils.Logger import Logger



class InSchoolSessions(SessionFeature):
    """A feature that determines whether a session started in school or not."""

import pandas as pd
import pytz
import json
import string
from geopy.geocoders import Nominatim
from datetime import datetime
from timezonefinder import TimezoneFinder

##############################

#FOR LOCALTIME TRIAL with colab code trying:

class PlayLocations(SessionFeature):
    # a session started in school or not.

      # *** IMPLEMENT ABSTRACT FUNCTIONS ***
    @classmethod
    def _getEventDependencies(cls, mode:ExtractionMode) -> List[str]:
        return ["all_events"]

    @classmethod
    def _getFeatureDependencies(cls, mode:ExtractionMode) -> List[str]:
        return []
    
    def _extractFromFeatureData(self, feature:FeatureData):
        return

    def _extractFromEvent(self, event:Event) -> None:
        if not event.SessionID in self._seen_sessions:
            self._seen_sessions.add(event.SessionID)
            # Step 1: calculate local time
            lat_long = self.calculate_coordinates(event=event)
            local_time = PlayLocations.calculate_local_time_by_coordinates(
            utc_time=event.Timestamp, latitude=lat_long.get('latitude'), longitude=lat_long.get('longitude'))
            # Step 2: check if local time was a school time or not, and add to lists
            self._session_times.append(local_time)
            # Step 3: Check if local time is on a weekday and between 9 AM and 3 PM
            is_weekday = local_time.weekday() < 5  # Monday to Friday is 0 to 4
            is_school_hours = 9 <= local_time.hour < 15
                
            in_school = is_weekday and is_school_hours
            self._in_school_sessions.append(in_school)

            
    def _getFeatureValues(self) -> List[Any]:
        # Sessions that started in school
        return [self._in_school_sessions, self._session_times]

    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)

        # sessions that have been seen before.
        self._seen_sessions = set()
        # sessions that started in school.
        self._in_school_sessions = []
        self._session_times = []
        # geolocater
        self.geolocator = Nominatim(user_agent="timezone_converter")

    # *** Optionally override public functions. ***
    def Subfeatures(self) -> List[str]:
        return ["LocalTime"]

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]

    # *** private helper functions ***

    def calculate_coordinates(self, event:Event):
        region = event.UserData.get("region")
        
        # You can continue with the geolocation code
        location_geocoded = self.geolocator.geocode(region, timeout=10) if region else None

        # Latitude and longitude from the geocoded
        latitude  = location_geocoded.latitude  if location_geocoded else None
        longitude = location_geocoded.longitude if location_geocoded else None

        # Filter rows where latitude is not NaN
        return {'latitude':latitude, 'longitude':longitude}


    @staticmethod
    def calculate_local_time_by_coordinates(utc_time, latitude, longitude):
        if latitude is None or longitude is None:
            return None    
        
        tz_finder = TimezoneFinder()
        timezone_str = tz_finder.timezone_at(lng=longitude, lat=latitude)

        if timezone_str:
            local_timezone = pytz.timezone(timezone_str)
            localized_time = pytz.timezone('UTC').localize(utc_time)
            local_time     = localized_time.astimezone(local_timezone)
            return local_time
        else:
            Logger.Log(f"Could not get timezone string, defaulting to datetime.min with UTC timezone", level=logging.WARN)
            return datetime.min.replace(tzinfo=pytz.UTC)  # Default value 




