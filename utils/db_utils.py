from config import config
from sqlalchemy import create_engine, Column, Integer, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker  


Base = declarative_base()
class Store(Base):
    __tablename__ = 'hcc_rag_store'
    index_id = Column(Integer, primary_key=True)
    index_name = Column(String)


class ConnectSQL:
    def __init__(self,
    ):   
        username = config['MYSQL_DB_USER']
        password = config['MYSQL_DB_PASSWORD']
        host = config['MYSQL_DB_HOST']
        database = config['MYSQL_DB_NAME']
        
        self.DB_URI = f'mysql+pymysql://{username}:{password}@{host}/{database}'
        self.engine = create_engine(self.DB_URI)
  
    def get_index_id_by_name(self,index_name):
        Session = sessionmaker(bind=self.engine)  
        session = Session()   
        existing_store = session.query(Store).filter_by(index_name=index_name).first()  
        session.close()
        
        if existing_store:  
            return True
        else:  
            return False
    
    def insert_index_name(self,index_name): 
        Session = sessionmaker(bind=self.engine)  
        session = Session()   
        new_store = Store(index_name=index_name)  
        session.add(new_store)  
        session.commit() 
        index_id = session.query(Store).filter_by(index_name=index_name).first().index_id
        session.close()
        return index_id
       
        
    def check_index_id_exists(self,index_id): 
        Session = sessionmaker(bind=self.engine)   
        session = Session()   
        existing_store = session.query(Store).filter_by(index_id=index_id).first()  
        session.close()
        
        if existing_store:  
            return True
        else:  
            return False
        
    def get_all_index_ids(self):
        Session = sessionmaker(bind=self.engine)   
        session = Session()   
        #existing_store = session.query(Store).filter_by(index_id=index_id).first()  
        indices = session.query(Store.index_id, Store.index_name).all() 
        session.close()
        if(len(indices)==0):
            return []
        else:
            indices_json = {"indices":[{"index_id": idx.index_id, "index_name": idx.index_name} for idx in indices]}  
            return indices_json
    
    def delete_index_name(self, index_id):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        session.query(Store).filter_by(index_id=index_id).delete(synchronize_session=False)
        session.commit()
        session.close()