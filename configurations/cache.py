import json

from dtos.configurations.cache import CacheConfigurationDTO

from start_utils import logger


class CacheConfiguration:
    """
    Singleton loader and manager for cache configuration.
    Loads configuration from config/cache/config.json.
    """
    _instance = None

    def __new__(cls):

        if cls._instance is None:
            cls._instance = super(CacheConfiguration, cls).__new__(cls)
            cls._instance.config = {}
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        """
        Load cache configuration from JSON file.
        Logs if the file is not found or cannot be decoded.
        """
        try:

            with open("config/cache/config.json", "r") as file:
                self.config = json.load(file)
            logger.debug("Cache config loaded successfully.")

        except FileNotFoundError:
            logger.debug("Cache config file not found.")

        except json.JSONDecodeError:
            logger.debug("Error decoding cache config file.")

    def get_config(self):
        """
        Return the cache configuration as a DTO.
        """
        return CacheConfigurationDTO(
            host=self.config.get("host", {}),
            port=self.config.get("port", {}),
            password=self.config.get("password", {}),
        )
