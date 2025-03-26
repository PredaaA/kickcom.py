import logging
import logging.handlers
import queue


def init_logging(set_debug: bool = False) -> logging.handlers.QueueListener:
    log_queue = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)
    stdout_handler = logging.StreamHandler()
    listener = logging.handlers.QueueListener(
        log_queue, *(stdout_handler,), respect_handler_level=True
    )

    if set_debug is True:
        queue_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[queue_handler],
        format="[{asctime}] [{levelname:^7s}] [{name:^30s}] {message}",
        style="{",
    )

    listener.start()
    return listener
