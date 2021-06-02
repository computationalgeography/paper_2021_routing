# Stuff that might end up in the LUE code
import numpy as np
import timeit


# 1: east,                6
# 2: southeast,           3
# 4: south,               2
# 8: southwest,           1
# 16: west,               4
# 32: northwest,          7
# 64: north.              8
# 128: northeast          9
# 0: river mouth,         5
# -1: inland depression,  wtf?
# -9: undefined (ocean)   255

# Africa dataset:
# 247: no-data
# 0: no-data


nominal_t = np.dtype(np.uint32)
flow_direction_t = np.dtype(np.uint8)
material_t = np.dtype(np.float32)
fraction_t = np.dtype(np.float32)
threshold_t = np.dtype(np.float32)


# def reclassify_flow_direction(
#         flow_direction):
# 
#     flow_direction = lfr.where(flow_direction == 1, 6, flow_direction)
#     flow_direction = lfr.where(flow_direction == 2, 3, flow_direction)
#     flow_direction = lfr.where(flow_direction == 4, 2, flow_direction)
#     flow_direction = lfr.where(flow_direction == 8, 1, flow_direction)
#     flow_direction = lfr.where(flow_direction == 16, 4, flow_direction)
#     flow_direction = lfr.where(flow_direction == 32, 7, flow_direction)
#     flow_direction = lfr.where(flow_direction == 64, 8, flow_direction)
#     flow_direction = lfr.where(flow_direction == 128, 9, flow_direction)
# 
#     flow_direction = lfr.where(flow_direction == 0, 5, flow_direction)
# 
#     flow_direction = lfr.where(flow_direction == 247, 255, flow_direction)
# 
#     flow_direction = lfr.where(flow_direction == -1, 5, flow_direction)
#     flow_direction = lfr.where(flow_direction == -9, 255, flow_direction)
# 
#     # if flow_direction.dtype != flow_direction_t:
# 
#     # Reclassify flow directions to LUE conventions
#     # TODO
# 
#     return flow_direction


def duration(label):
    def decorator(function):
        def decorated_function(*args, **kwargs):
            start_time = timeit.default_timer()
            result = function(*args, **kwargs)
            elapsed = timeit.default_timer() - start_time
            print("duration {}: {:.2}s / {:.2}m".format(label, elapsed, elapsed / 60))
            return result

        return decorated_function
    return decorator
