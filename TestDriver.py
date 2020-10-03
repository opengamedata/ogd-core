from realtime.RTServer import RTServer

result = RTServer.getPredictionsBySessID("20070105050890460", "LAKELAND", ["dummySequenceModel"])
print(f"Got this row from dummySequenceModel:\n{result}")