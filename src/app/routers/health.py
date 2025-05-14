"""
Endpoints for checking API health and connections.
"""

from fastapi import APIRouter, Response, status

# Instantiate router object
router = APIRouter(prefix='/health', tags=['Health Check'])


@router.get('/check_status')
async def check_status() -> Response:
    """
    Check API status
    Returns
    -------
        response : fastapi.Response
            response model
    """
    return Response(status_code=status.HTTP_200_OK)
