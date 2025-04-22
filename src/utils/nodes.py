import time
import random
import logging
from functools import wraps

from src.langg.models import ExceptionDict

logger = logging.getLogger(__name__)

def notifier_and_define_end(
    exception: ExceptionDict
):
    logger.info("Notifying")

    exception_type = exception["exception_type"]
    exception_node = exception["exception_node"]
    exception_text = exception["exception_text"]
    ended = exception["end"]

    message = f"<b>Node:</b> {exception_node}\n<b>Exception:</b> {exception_type}\n<b>Description:</b> {exception_text}\n<b>Ended:</b> {ended}"
    try:
        logger.error(message)
    except Exception as e:
        logger.error(f"Error sending message to Telegram: {e}")

    return ended


def exponential_backoff(tries, base_delay=1, max_delay=60):
    for n in range(tries):
        yield min(base_delay * (2**n) + random.uniform(0, 1), max_delay)


def required_node(tries=3):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            for delay in exponential_backoff(tries):
                try:
                    return f(self, *args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"Attempt failed: {str(e)}. Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)

                    exception = ExceptionDict(
                        exception_node=f.__name__,
                        exception_type=str(type(e).__name__),
                        exception_text=str(e),
                        end=True,
                    )
            return {"end": notifier_and_define_end(exception)}

        return wrapper

    return decorator


def optional_node(tries=3):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            for delay in exponential_backoff(tries):
                try:
                    return f(self, *args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"Attempt failed: {str(e)}. Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)

                    exception = ExceptionDict(
                        exception_node=f.__name__,
                        exception_type=str(type(e).__name__),
                        exception_text=str(e),
                        end=False,
                    )
            return {"end": notifier_and_define_end(exception)}

        return wrapper

    return decorator