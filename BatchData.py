import typing

# Dumb struct to hold data related to a batch of database data.
# Just here to help keep useful data together for easier passing around.
class BatchData:
    def __init__(self, column_names: typing.List[str], max_level: int, min_level: int, session_ids: typing.List[int]):
        self.column_names = column_names
        self.complex_data_index = column_names.index("event_data_complex")
        self.client_time_index = column_names.index("client_time")
        self.session_id_index = column_names.index("session_id")
        self.event_index = column_names.index("event")
        self.level_index = column_names.index("level")
        self.max_level = max_level
        self.min_level = min_level
        self.session_ids = session_ids