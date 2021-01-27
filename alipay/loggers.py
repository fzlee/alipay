import logging
import logging.config

logging.config.dictConfig({
  "version": 1,
  "disable_existing_loggers": False,
  "formatters": {
      "standard": {
          "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
      },
  },
  "handlers": {
      "console": {
          "level": "DEBUG",
          "formatter": "standard",
          "class": "logging.StreamHandler",
      },
  },
  "loggers": {
      "python-alipay-sdk": {
          "handlers": ["console"],
          "level": "DEBUG",
      }
  }
})
logger = logging.getLogger("python-alipay-sdk")
