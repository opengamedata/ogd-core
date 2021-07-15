Custom event parameters at https://github.com/fielddaylab/aqualab#firebase-telementry-events

Default event parameters from https://support.google.com/firebase/answer/7061705?hl=en and https://support.google.com/firebase/answer/9234069?visit_id=637618872033635120-1862140882&rd=1
- ga_session_id: Unique session identifier (based on the timestamp of the session_start event) associated with each event that occurs within a session
- ga_session_number: Monotonically increasing identifier (starting with 1) of the ordinal position of a session as it relates to a user (e.g., a user's 1st or 5th session) associated with each event that occurs in a session
- page_location: page URL
- page_referrer: previous page URL

Columns:
- event_name: The name of the event
- event_params: "A repeated record of the parameters associated with this event
- user_id: The user ID set via the setUserId API
- device: A record of device information
- geo: A record of the user's geographic information
- platform: The platform on which the app was built
- session_id: ID for the current play session (from ga_session_id in event_params)
- timestamp: Datetime when the event was logged
