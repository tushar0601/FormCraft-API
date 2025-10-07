from sqlalchemy.orm import declarative_base

Base = declarative_base()

try:
    from app.domain.form.model import Form
    from app.domain.form.model import FormBlock
    from app.domain.response.model import FormResponse
    from app.domain.response.model import BlockResponse
    from app.domain.analytics.model import FormAnalytics
    from app.domain.analytics.model import BlockAnalytics
except Exception:
    pass