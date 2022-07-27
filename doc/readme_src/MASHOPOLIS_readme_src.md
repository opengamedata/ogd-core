## Data Logging Info:
See https://github.com/fielddaylab/mashopolis

Firebase adds event parameters from https://support.google.com/firebase/answer/7061705?hl=en and https://support.google.com/firebase/answer/9234069?visit_id=637618872033635120-1862140882&rd=1

Columns:
- event_name: The name of the event
- event_params: A repeated record of the parameters associated with this event
- user_id: The user ID set via the setUserId API
- device: A record of device information
- geo: A record of the user's geographic information
- platform: The platform on which the app was built
- session_id: ID for the current play session (from ga_session_id in event_params)
- timestamp: Datetime when the event was logged
