from rest_framework.views import exception_handler
from django.http import Http404
from rest_framework.exceptions import (
    ValidationError,
    NotFound,
    PermissionDenied,
    NotAuthenticated,
)
import logging
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def get_resource_name(context):
    view = context.get("view")
    request = context.get("request")

    if hasattr(view, "queryset") and view.queryset is not None:
        return view.queryset.model.__name__

    if hasattr(view, "get_queryset"):
        try:
            return view.get_queryset().model.__name__
        except Exception:
            pass

    if request:
        kwargs = getattr(request, "parser_context", {}).get("kwargs", {})
        if "section_id" in kwargs:
            return "Section"
        if "class_id" in kwargs:
            return "Class"
        if "teacher_id" in kwargs:
            return "Teacher"

    return "Resource"


def log_exception(exc, context, level):
    request = context.get("request")

    if request:
        user = request.user.id if request.user.is_authenticated else "Anonymous"
        method = request.method
        path = request.get_full_path()
    else:
        user = "Unknown"
        method = "Unknown"
        path = "Unknown"

    log_message = (
        f"{method} {path} | User: {user} | "
        f"Exception: {exc.__class__.__name__} | {str(exc)}"
    )

    if level == "warning":
        logger.warning(log_message)
    elif level == "info":
        logger.info(log_message)
    elif level == "critical":
        logger.critical(log_message)
    else:
        logger.exception(log_message)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        log_exception(exc, context, level="critical")
        return Response(
        {
            "error": {
                "type": "server_error",
                "code": "internal_error",
                "message": "Internal server error",
                "fields": {},
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    error_type = "unknown_error"
    code = "error"
    message = "Something went wrong"
    fields = {}

    # ---------------- VALIDATION ----------------
    if isinstance(exc, ValidationError):
        error_type = "validation_error"
        code = "invalid_input"
        message = "Validation failed"
        fields = response.data
        log_exception(exc, context, level="warning")

    # ---------------- NOT FOUND ----------------
    elif isinstance(exc, (NotFound, Http404)):
        resource = get_resource_name(context)
        error_type = "not_found"
        code = "resource_not_found"
        message = f"{resource} not found"
        log_exception(exc, context, level="info")

    # ---------------- PERMISSION ----------------
    elif isinstance(exc, (PermissionDenied, NotAuthenticated)):
        error_type = "permission_denied"
        code = "not_allowed"
        message = str(exc)
        log_exception(exc, context, level="warning")

    # ---------------- DEFAULT ----------------
    else:
        message = response.data.get("detail", "Something went wrong")
        log_exception(exc, context, level="error")

    response.data = {
        "error": {
            "type": error_type,
            "code": code,
            "message": message,
            "fields": fields,
        }
    }

    return response