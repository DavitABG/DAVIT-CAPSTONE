from typing import List

from pydantic import Field, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class MiddlewareSettings(BaseModel):
    """
    Keep middleware settings
    """

    allow_origins: List[str] = ['*']
    allow_methods: List[str] = ['*']
    allow_credentials: bool = True
    allow_headers: List[str] = ['*']


class SwaggerUIParameters(BaseModel):
    """
    Parameters to use when rendering Swagger UI
    """
    model_config = ConfigDict(alias_generator=to_camel)
    display_request_duration: bool = Field(True,
                                           description="Whether to display the request duration in milliseconds")
    filter: str = Field('', description="Allow filtering the endpoints by tags with specified default")
    try_it_out_enabled: bool = Field(False,
                                     description="Whether try it out button should be activated by default")
    request_snippets_enabled: bool = Field(False,
                                           description="Whether request snippets should be enabled by default")
    request_snippets: dict | None = Field(None,
                                          description="Configuration for requests snippets")


class AppSettings(BaseModel):
    """
    Application settings
    """

    description: str = "A template for FastAPI projects"
    title: str = "FASTAPI PROJECT"
    swagger_ui_parameters: SwaggerUIParameters = Field(default_factory=SwaggerUIParameters)
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
