class LabCompleteCount:
    def __init__(self):
        self.complete_count = 0

    def track_event(self, event_data):
        if event_data is not None and event_data.get("percent_complete", 0) >= 100:
            self.complete_count += 1

    def get_count(self):
        return self.complete_count
