# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
class BaseSettings:
    """Minimal stand-in for pydantic_settings.BaseSettings."""
    def __init__(self, **values):
        for k, v in values.items():
            setattr(self, k, v)
