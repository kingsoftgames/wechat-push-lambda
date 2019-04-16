class RetryPolicy:

    def __init__(self, max_retry_count):
        self.max_retry_count = max_retry_count
        self.retried_count = 0

    def increment_retry_count(self, count=1):
        self.retried_count += count

    def exceeded_max_retry(self):
        return (self.max_retry_count <= self.retried_count)


def get_retry_policy():
    return RetryPolicy(3)
