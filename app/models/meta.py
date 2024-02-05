from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

metadata = MetaData(schema='publication')
Base = declarative_base(metadata=metadata)
