from redis import Redis

from start_utils import redis_session, logger


class CacheDependency:
    """
    Dependency provider for Redis cache session.
    Provides the shared Redis session for DI.
    """
    @staticmethod
    def derive() -> Redis:
        """
        Returns the shared Redis session instance.
        Logs when the cache dependency is derived.
        """
        logger.debug("CacheDependency: returning redis_session instance")
        return redis_session
