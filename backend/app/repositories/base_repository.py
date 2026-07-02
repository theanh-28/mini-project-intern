
class BaseRepository:
    def __init__(self, model, db):
        self.model = model
        self.db = db
    
    def get_by_id(self, id):
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_page(self, page:int = 1, limit: int = 100):
        skip = (page - 1) * limit
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()