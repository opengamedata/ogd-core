from typing import Any, List

from extractors.Extractor import ExtractorParameters
from extractors.features.SessionFeature import SessionFeature
from schemas.Event import Event
from schemas.ExtractionMode import ExtractionMode
from schemas.FeatureData import FeatureData



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
        return

    def __init__(self, params: ExtractorParameters):
        super().__init__(params=params)

        # sessions that have been seen before.
        self._seen_sessions = []
        # sessions that started in school.
        self._in_school_sessions = []

        # geolocater
        self.geolocator = Nominatim(user_agent="timezone_converter")

    @classmethod
    def AvailableModes(cls) -> List[ExtractionMode]:
        return [ExtractionMode.PLAYER]

    def calculate_coordinates ():
        df['region'] = df['event'].apply(lambda event: event.UserData.get("region") if 'event' in event else None)
        
        geolocator = Nominatim(user_agent="my_app")
        # You can continue with the geolocation code
        df['location_geocoded'] = df['region'].apply(lambda x: geolocator.geocode(x, timeout=10) if x else None)

        # Latitude and longitude from the geocoded
        df['latitude'] = df['location_geocoded'].apply(lambda x: x.latitude if x else None)
        df['longitude'] = df['location_geocoded'].apply(lambda x: x.longitude if x else None)

        # Filter rows where latitude is not NaN
        df = df[df['latitude'].notna()]


    def calculate_local_time_by_coordinates(self, utc_time_str, latitude, longitude):
        tz_finder = TimezoneFinder()
        timezone_str = tz_finder.timezone_at(lng=longitude, lat=latitude)

        if timezone_str:
            local_timezone = pytz.timezone(timezone_str)
            utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S.%f %Z")
            utc_time = pytz.timezone('UTC').localize(utc_time)
            local_time = utc_time.astimezone(local_timezone)
            return local_time
        else:
            return datetime.min.replace(tzinfo=pytz.UTC)  # Default value 

    def _getFeatureValues(self) -> List[bool]:
        # Sessions that started in school
        return [is_in_school for is_in_school in self._in_school_sessions]




