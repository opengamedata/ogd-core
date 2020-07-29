## Data Logging Info:
See https://github.com/fielddaylab/usda/blob/master/README.md

Lakeland "levels" (features with the prefix lvln_, where n is a nonnegative integer) are realtime windows defined in the lakeland schema's config subobject. 
Level windows are "WINDOW_SIZE_SECONDS" (currently 300s) long, with each subsequent level starting "WINDOW_OVERLAP_SECONDS" (currently 30s) before the previous level ends. Lastly, because this theoretically could give infinite levels, "MAX_SESSION_SECONDS" (currently 2700s) is defined to stop taking logs after a given number of seconds.

Thus the current levels are as follows (as of 7/29/2020):
lvl0: 0s-300s (0:00-5:00)
lvl1: 270s-570s (4:30-9:30)
lvl2: 540s-840s (9:00-14:00)
lvl3: 810s-1110s
lvl4: 1080s-1380s
lvl5: 1350s-1650s
lvl6: 1620s-1920s
lvl7: 1890s-2190s
lvl8: 2160s-2460s
lvl9: 2430s-2700s (40:30-45:00)
