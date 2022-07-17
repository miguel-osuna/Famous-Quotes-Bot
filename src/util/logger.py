import logging
import logging.handlers as handlers


def generate_logger(module_name):
    """Generates a custom logger."""

    # Create custom logger
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.DEBUG)

    # Create handlers
    console_handler = logging.StreamHandler()

    # Create formatter and add it to handler
    formatter = logging.Formatter(
        "[Line: {lineno}] [{asctime}] [{levelname}] {name}: {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)

    return logger
