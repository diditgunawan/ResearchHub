from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, Numeric, Date
from datetime import datetime, timezone, date
import uuid
from app.core.database import Base


class Journal(Base):
    __tablename__ = "journals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    openalex_id = Column(String(64), unique=True, nullable=True, index=True)
    issn_l = Column(String(16), nullable=True, index=True)
    issns = Column(JSON, nullable=False, default=list)
    title = Column(String(255), nullable=False, index=True)
    publisher = Column(String(255), nullable=True)
    country = Column(String(64), nullable=True)
    scope_text = Column(Text, nullable=True)
    languages = Column(JSON, nullable=False, default=lambda: ["en"])
    is_oa = Column(Boolean, default=False, nullable=False)
    in_doaj = Column(Boolean, default=False, nullable=False)
    apc_usd = Column(Numeric(10, 2), nullable=True)
    apc_note = Column(String(255), nullable=True)
    scopus_quartile = Column(String(8), nullable=True)  # Q1..Q4
    sinta_rank = Column(String(8), nullable=True)  # S1..S6
    guidelines_url = Column(String(512), nullable=True)
    data_as_of = Column(Date, nullable=False, default=lambda: date.today())
    provenance = Column(JSON, nullable=False, default=dict)  # {field: source, license}
    recent_articles = Column(JSON, nullable=False, default=list)  # [{title, doi, year}]
    keywords = Column(JSON, nullable=False, default=list)
