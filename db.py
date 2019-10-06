from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///wiki.db')
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


class Urls(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    depth = Column(Integer)


class Connections(Base):
    __tablename__ = 'connections'
    id = Column(Integer, primary_key=True)
    from_page_id = Column(Integer, ForeignKey('urls.id'))
    link_id = Column(Integer, ForeignKey('urls.id'))
    page = relationship("Urls", foreign_keys=[from_page_id])
    link = relationship("Urls", foreign_keys=[link_id])


Base.metadata.create_all(engine)


