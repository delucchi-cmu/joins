"""An example module containing simplistic functions."""


def join(left_frame, right_frame):
    """empty"""
    joined = left_frame.join(right_frame, how="left")
    print(joined)
