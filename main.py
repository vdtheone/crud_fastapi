from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from typing import List
from pydantic import BaseModel, constr


app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = {"check_same_thread": False})
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
   db = session()
   try:
      yield db
   finally:
      db.close()


class Books(Base):
   __tablename__ = 'book'
   id = Column(Integer, primary_key=True, nullable=False)
   title = Column(String(50))
   author = Column(String(50))
   publisher = Column(String(50))
   Base.metadata.create_all(bind=engine)


class Book(BaseModel):
   id: int
   title: str
   author:str
   publisher: str
   class Config:
      orm_mode = True




@app.post('/add_new', response_model=Book)
def add_book(b1: Book, db: Session = Depends(get_db)):
   
   bk=Books(id=b1.id, title=b1.title, author=b1.author,
            publisher=b1.publisher)
   db.add(bk)
   db.commit()
   db.refresh(bk)
   return Books(**b1.model_dump())


@app.get('/list', response_model=List[Book])
def get_books(db: Session = Depends(get_db)):
   recs = db.query(Books).all()
   return recs


@app.get("/book/{id}")
async def get_book(id: int, db: Session = Depends(get_db)):
   return db.query(Books).filter(Books.id == id).first()


@app.put('/update/{id}', response_model=Book)
def update_book(id:int, book:Book, db: Session = Depends(get_db)):
   b1 = db.query(Books).filter(Books.id == id).first()
   b1.id=book.id
   b1.title=book.title
   b1.author=book.author
   b1.publisher=book.publisher
   db.commit()
   return db.query(Books).filter(Books.id == id).first()


@app.delete("/delete{id}")
async def delete_book(id: int, db: Session = Depends(get_db)):
   try:
      db.query(Books).filter(Books.id == id).delete()
      db.commit()
   except Exception as e:
      raise Exception(e)
   return {"delete status": "success"}



