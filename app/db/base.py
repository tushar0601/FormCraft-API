from sqlalchemy.orm import declarative_base

Base = declarative_base()

try:
    from app.domain.form.model import Form
    from app.domain.form.model import FormBlock
    from app.domain.response.model import FormResponse
    from app.domain.response.model import BlockResponse
except Exception:
    pass