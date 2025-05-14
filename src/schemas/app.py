"""
Application schemas
"""

from pydantic import BaseModel, Field


class SampleRequest(BaseModel):
    message: str = Field(description='message field', examples=['bxdo'])


class SampleResponse(BaseModel):
    message: str = Field(description='message field', examples=['Hi bxdo'])
