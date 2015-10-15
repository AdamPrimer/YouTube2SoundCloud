import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Mapping(Base):
    __tablename__ = 'mapping'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    yt_playlist = Column(String(250), nullable=False)
    sc_playlist = Column(String(250), nullable=False)
    album_art = Column(String(250), nullable=True)

class Blacklist(Base):
    __tablename__ = 'blacklist'
    id = Column(Integer, primary_key=True)
    mapping_id = Column(Integer, ForeignKey('mapping.id'))
    yt_id = Column(String(250), nullable=False)

engine = create_engine('sqlite:///db/yt2sc.db')
Base.metadata.create_all(engine)
