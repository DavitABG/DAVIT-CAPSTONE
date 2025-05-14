"""
Endpoints for example_router
"""

from fastapi import APIRouter

from src.schemas.app import SampleRequest, SampleResponse

router = APIRouter(prefix='/example_router', tags=['Example Router'])


@router.post('/example_post')
async def example(request: SampleRequest) -> SampleResponse:
    """
    Sample POST endpoint

    Parameters
    ----------
    request : SampleRequest
        endpoint request

    Returns
    -------
    chat_response : SampleResponse
        response of the endpoint
    """
    user_message = request.message
    response_message = f"Hi {user_message}"
    return SampleResponse(message=response_message)


@router.get('/example_get')
async def another_example() -> SampleResponse:
    """
    This is an example of GET method

    Returns
    -------
    response : SampleResponse
        response of the endpoint
    """
    return SampleResponse(message='Hello World')
