import os


def get_env(key, default=None, required=False) -> str:
    """Wrapper for gathering env vars."""
    if required:
        assert key in os.environ, "Missing Environment Variable: %s" % key
    return str(os.environ.get(key, default))


class Config:
    """Wrap application configurations

    Attributes
    ----------
    DATA_PATH : str
        The path where to store any resources (default: ./)
    OPENAI_API_KEY : str
        OpenAI API Key - Required
    """

    CHROMA_DATA_PATH: str = get_env("CHROMA_DATA_PATH", required=False)
    HOME_ASSISTANT_API_KEY: str = get_env("HOME_ASSISTANT_API_KEY", required=False)
    HOME_ASSISTANT_URL: str = get_env("HOME_ASSISTANT_URL", required=False)
    OPENAI_API_KEY: str = get_env("OPENAI_API_KEY", required=True)
