# app/models.py
from sqlalchemy import Column, Integer, Text

from .db import Base


class Document(Base):
    """
    SQLAlchemy ORM model for the 'documents' table.

    Fields:
    - id: integer primary key
    - title: text column (required)
    - content: text column (required)
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
