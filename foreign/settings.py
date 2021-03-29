try:
    import base_config
except ImportError:
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import base_config
# import common
# from target import upsert_many as callback
# get_data((LAT, LON))
# exit(0)
# 61.664112, 50.791889
#
ROUND = 4
#
LAT_EPSILON = 0.07
LON_EPSILON = 0.07
# TEST
LAT_EPSILON = 0.005
LON_EPSILON = 0.005
#
DELTA = 0.02
#
LAT = 59.980312
LON = 30.329998
#
LAT_AXIS = [LAT, ]
LAT_CURRENT_P = LAT
LAT_CURRENT_M = LAT
while LAT_CURRENT_P < LAT + LAT_EPSILON:
    LAT_CURRENT_P += DELTA
    LAT_CURRENT_P = round(LAT_CURRENT_P, ROUND)
    LAT_CURRENT_M -= DELTA
    LAT_CURRENT_M = round(LAT_CURRENT_M, ROUND)
    LAT_AXIS.extend([LAT_CURRENT_P, LAT_CURRENT_M])
#
LON_AXIS = [LON, ]
LON_CURRENT_P = LON
LON_CURRENT_M = LON
while LON_CURRENT_P < LON + LON_EPSILON:
    LON_CURRENT_P += DELTA
    LON_CURRENT_P = round(LON_CURRENT_P, ROUND)
    LON_CURRENT_M -= DELTA
    LON_CURRENT_M = round(LON_CURRENT_M, ROUND)
    LON_AXIS.extend([LON_CURRENT_P, LON_CURRENT_M])
#
AXIS_POINTS = []
for lon in LON_AXIS:
    for lat in LAT_AXIS:
        AXIS_POINTS.append((lon, lat,))
#
# AXIS_POINTS_WITH_CALLBACK = []
# for AXIS_POINT in AXIS_POINTS:
#     AXIS_POINTS_WITH_CALLBACK.append((*AXIS_POINT, callback))
