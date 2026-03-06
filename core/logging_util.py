import logging

logger = logging.getLogger(__name__)


def log_business_event(request, message, level="info"):
    """
    Standardized business action logging
    """

    user = request.user.id if request.user.is_authenticated else "Anonymous"
    method = request.method
    path = request.get_full_path()

    log_message = f"{method} {path} | User: {user} | {message}"

    if level == "warning":
        logger.warning(log_message)
    elif level == "error":
        logger.error(log_message)
    else:
        logger.info(log_message)