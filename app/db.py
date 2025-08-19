from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///app.db", future=True)


# Ensure SQLite actually enforces FK constraints at every connection
@event.listens_for(engine, "connect") #Listens for every connection request to the engine
def set_sqlite_pragma(dbapi_conn, _):
  dbapi_conn.execute("PRAGMA foreign_keys = ON")


SessionLocal = sessionmaker(engine, expire_on_commit=False)