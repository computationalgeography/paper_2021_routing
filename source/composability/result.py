class Result(object):

    def __init__(self,
            partition_shape,
            synchronize,
            duration):
        self.partition_shape = partition_shape
        self.synchronize = synchronize
        self.duration = duration


    def __repr__(self):
        return "Result(partition_shape={}, synchronize={}, duration={})".format(
            self.partition_shape, self.synchronize, self.duration)
