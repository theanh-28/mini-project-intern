
class BaseRepository:
    def __init__(self, model, db):
        self.model = model
        self._db = db

    @property
    def db(self):
        if callable(self._db):
            return self._db()
        return self._db
    
    def get_by_id(self, id):
        return self.db.get(self.model, id)
    
    def get_page(self, page:int = 1, limit: int = 100):
        skip = (page - 1) * limit
        return self.db.query(self.model).offset(skip).limit(limit).all()
