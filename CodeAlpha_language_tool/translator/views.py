"""
API views for the translator app.

Endpoints
---------
POST /translate/   — TranslateAPIView
GET  /health/      — HealthCheckView
GET  /languages/   — SupportedLanguagesView
"""

import logging

from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    TranslationAPIError,
    TranslationError,
    TranslationTimeoutError,
    TranslationValidationError,
)
from .serializers import TranslationRequestSerializer, TranslationResponseSerializer
from .services import TranslationServiceFactory
from .utils.response import error_response, success_response

logger = logging.getLogger(__name__)


class TranslateAPIView(APIView):
    """
    POST /translate/

    Accepts a JSON body with `text`, `source_language`, and `target_language`,
    forwards the request to the configured translation service, and returns
    the translated text.

    Request body
    ------------
    {
        "text": "Hello, world!",
        "source_language": "en",
        "target_language": "fr"
    }

    Success response (200)
    ----------------------
    {
        "success": true,
        "message": "Translation successful.",
        "data": {
            "translated_text": "Bonjour le monde!",
            "source_language": "en",
            "target_language": "fr",
            "detected_language": null,
            "characters_translated": 13
        },
        "status_code": 200
    }
    """

    def post(self, request) -> Response:
        # ----------------------------------------------------------------
        # 1. Log the incoming request (never log raw text for privacy)
        # ----------------------------------------------------------------
        logger.info(
            'Incoming translation request | source=%s target=%s',
            request.data.get('source_language', 'unknown'),
            request.data.get('target_language', 'unknown'),
        )

        # ----------------------------------------------------------------
        # 2. Validate input
        # ----------------------------------------------------------------
        request_serializer = TranslationRequestSerializer(data=request.data)
        if not request_serializer.is_valid():
            logger.warning(
                'Translation request validation failed: %s',
                request_serializer.errors,
            )
            return Response(
                data=error_response(
                    message='Invalid request data.',
                    errors=request_serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated = request_serializer.validated_data
        text: str = validated['text']
        source_language: str = validated['source_language']
        target_language: str = validated['target_language']

        # ----------------------------------------------------------------
        # 3. Perform translation
        # ----------------------------------------------------------------
        try:
            service = TranslationServiceFactory.get_service()
            result = service.translate(text, source_language, target_language)

        except TranslationTimeoutError as exc:
            logger.error(
                'Translation timed out | source=%s target=%s | %s',
                source_language,
                target_language,
                exc.message,
            )
            return Response(
                data=error_response(
                    message='Translation service timed out. Please try again.',
                    status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                ),
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )

        except TranslationValidationError as exc:
            logger.warning(
                'Translation validation error | source=%s target=%s | %s',
                source_language,
                target_language,
                exc.message,
            )
            return Response(
                data=error_response(
                    message=exc.message,
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                ),
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        except TranslationAPIError as exc:
            logger.error(
                'Translation API error | source=%s target=%s | %s',
                source_language,
                target_language,
                exc.message,
            )
            return Response(
                data=error_response(
                    message=exc.message,
                    status_code=status.HTTP_502_BAD_GATEWAY,
                ),
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except TranslationError as exc:
            logger.error(
                'Translation error | source=%s target=%s | %s',
                source_language,
                target_language,
                exc.message,
            )
            return Response(
                data=error_response(
                    message=exc.message,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        except Exception as exc:  # noqa: BLE001
            logger.exception(
                'Unexpected error during translation | source=%s target=%s',
                source_language,
                target_language,
                exc_info=True,
            )
            return Response(
                data=error_response(
                    message='An unexpected error occurred. Please try again later.',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ----------------------------------------------------------------
        # 4. Serialize and return the result
        # ----------------------------------------------------------------
        response_serializer = TranslationResponseSerializer(data=result)
        response_serializer.is_valid(raise_exception=True)

        return Response(
            data=success_response(
                data=response_serializer.data,
                message='Translation successful.',
                status_code=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class HealthCheckView(APIView):
    """
    GET /health/

    Returns the operational status of the translation service.
    Useful for load balancers, uptime monitors, and CI pipelines.

    Success response (200)
    ----------------------
    {
        "success": true,
        "message": "Service is healthy.",
        "data": {
            "service": "libretranslate",
            "status": "healthy",
            "version": "1.0.0"
        },
        "status_code": 200
    }
    """

    def get(self, request) -> Response:
        try:
            service = TranslationServiceFactory.get_service()
            available = service.is_available
        except Exception as exc:  # noqa: BLE001
            logger.error('Health check failed: %s', exc)
            return Response(
                data=error_response(
                    message='Translation service is unavailable.',
                    errors={'status': 'unhealthy'},
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                ),
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if not available:
            logger.warning('Health check: service reported as unavailable.')
            return Response(
                data=error_response(
                    message='Translation service is not configured.',
                    errors={'status': 'unhealthy'},
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                ),
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            data=success_response(
                data={
                    'service': service.service_name,
                    'status': 'healthy',
                    'version': '1.0.0',
                },
                message='Service is healthy.',
                status_code=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class SupportedLanguagesView(APIView):
    """
    GET /languages/

    Returns the list of language pairs supported by the active translation
    service backend.

    Success response (200)
    ----------------------
    {
        "success": true,
        "message": "Supported languages retrieved successfully.",
        "data": {
            "languages": [
                {"code": "en", "name": "English"},
                {"code": "fr", "name": "French"},
                ...
            ],
            "count": 30
        },
        "status_code": 200
    }
    """

    def get(self, request) -> Response:
        try:
            service = TranslationServiceFactory.get_service()
            languages = service.get_supported_languages()
        except TranslationError as exc:
            logger.error('Failed to fetch supported languages: %s', exc.message)
            return Response(
                data=error_response(
                    message=exc.message,
                    status_code=status.HTTP_502_BAD_GATEWAY,
                ),
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception('Unexpected error fetching supported languages.', exc_info=True)
            return Response(
                data=error_response(
                    message='Failed to retrieve supported languages.',
                    status_code=status.HTTP_502_BAD_GATEWAY,
                ),
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            data=success_response(
                data={
                    'languages': languages,
                    'count': len(languages),
                },
                message='Supported languages retrieved successfully.',
                status_code=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class IndexView(TemplateView):
    """
    GET /

    Renders the main 3D language translation interface.
    The frontend fetches /languages/ and /translate/ via JavaScript.
    """
    template_name = 'translator/index.html'
