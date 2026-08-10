"""
Standardised API response helpers and a custom DRF exception handler.

All API responses from this project follow a consistent envelope:

Success
-------
{
    "success": true,
    "message": "...",
    "data": { ... },
    "status_code": 200
}

Error
-----
{
    "success": false,
    "message": "...",
    "errors": { ... } | null,
    "status_code": 4xx | 5xx
}
"""

import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------


def success_response(
    data: dict,
    message: str = 'Success',
    status_code: int = 200,
) -> dict:
    """
    Build a standardised success response envelope.

    Parameters
    ----------
    data        : The payload to include under the 'data' key.
    message     : Human-readable status message.
    status_code : HTTP status code (informational — included in the body).

    Returns
    -------
    dict suitable for passing to rest_framework.response.Response(data=...).
    """
    return {
        'success': True,
        'message': message,
        'data': data,
        'status_code': status_code,
    }


def error_response(
    message: str,
    errors: dict = None,
    status_code: int = 400,
) -> dict:
    """
    Build a standardised error response envelope.

    Parameters
    ----------
    message     : Human-readable error description.
    errors      : Optional dict of field-level or detail errors.
    status_code : HTTP status code (informational — included in the body).

    Returns
    -------
    dict suitable for passing to rest_framework.response.Response(data=...).
    """
    return {
        'success': False,
        'message': message,
        'errors': errors,
        'status_code': status_code,
    }


# ---------------------------------------------------------------------------
# Custom DRF exception handler
# ---------------------------------------------------------------------------


def custom_exception_handler(exc, context) -> Response:
    """
    Wrap Django REST Framework exceptions in the project's standard envelope.

    This handler is set as REST_FRAMEWORK['EXCEPTION_HANDLER'] in settings.

    Behaviour
    ---------
    - Known DRF exceptions (ValidationError, NotFound, etc.) are wrapped in
      our error_response envelope while preserving the original status code.
    - Unknown / unhandled exceptions are logged with a full traceback and
      returned as a generic 500 response to avoid leaking internals.

    Parameters
    ----------
    exc     : The raised exception.
    context : DRF context dict (includes 'request', 'view', etc.).

    Returns
    -------
    rest_framework.response.Response
    """
    # Let DRF handle the exception first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF recognised the exception — wrap in our envelope
        original_data = response.data

        # DRF ValidationError surfaces as either a dict or a list
        if isinstance(original_data, dict):
            message = original_data.pop('detail', 'A validation error occurred.')
            # Convert ErrorDetail objects to plain strings if needed
            if hasattr(message, '__str__'):
                message = str(message)
            errors = original_data if original_data else None
        elif isinstance(original_data, list):
            message = 'A validation error occurred.'
            errors = {'non_field_errors': [str(e) for e in original_data]}
        else:
            message = str(original_data)
            errors = None

        response.data = error_response(
            message=message,
            errors=errors,
            status_code=response.status_code,
        )
        return response

    # Unhandled exception — log it and return a safe 500
    logger.exception(
        'Unhandled exception in view %s: %s',
        context.get('view', 'unknown'),
        exc,
        exc_info=True,
    )
    return Response(
        data=error_response(
            message='An internal server error occurred. Please try again later.',
            status_code=500,
        ),
        status=500,
    )
