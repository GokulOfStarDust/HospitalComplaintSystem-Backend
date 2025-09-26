from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, NotAuthenticated):
        # Always return 401 for NotAuthenticated
        return Response({'detail': str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

    # If DRF's default exception handler returns None, handle it as a generic 500 error
    if response is None:
        return Response({'detail': 'A server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # If the response is not a DRF Response object (e.g., a Django HttpResponse), convert it
    if not isinstance(response, Response):
        return Response({'detail': response.content.decode() if response.content else 'A server error occurred.'}, status=response.status_code)

    return response
