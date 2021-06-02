## @class Event
#  Completely dumb struct that enforces a particular structure for the data we get from a source.
#  Basically, whenever we fetch data, the TableSchema will be used to map columns to the required elements of an Event.
#  Then the extractors etc. can just access columns in a direct manner.
class Event:
    def __init__(self, id, app_id, app_id_fast, app_version,
                 session_id, persistent_session_id, player_id,
                 level, event, event_custom, event_data_simple, event_data_complex,
                 client_time, client_time_ms, server_time,
                 remote_addr, req_id, session_n, http_user_agent):
        self.id = id
        self.app_id = app_id
        self.app_id_fast = app_id_fast
        self.app_version = app_version
        self.session_id  = session_id
        self.persistent_session_id  = persistent_session_id
        self.player_id  = player_id
        self.level      = level
        self.event      = event
        self.event_custom = event_custom
        self.event_data_simple = event_data_simple
        self.event_data_complex = event_data_complex
        self.client_time = client_time
        self.client_time_ms = client_time_ms
        self.server_time = server_time
        self.remote_addr = remote_addr
        self.req_id = req_id
        self.session_n  = session_n
        self.http_user_agent  = http_user_agent
