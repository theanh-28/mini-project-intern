
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
    
    def count(self) -> int:
        return self.db.query(self.model).count()

    def get_page(self, page:int = 1, limit: int = 100):
        skip = (page - 1) * limit
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def _apply_filters(self, query, filters: dict):
        if not filters:
            return query

        for field, value in filters.items():
            if value is not None:
                if field.endswith("_from"):
                    base_field = field[:-5]
                    if hasattr(self.model, base_field):
                        query = query.filter(getattr(self.model, base_field) >= value)
                elif field.endswith("_to"):
                    base_field = field[:-3]
                    if hasattr(self.model, base_field):
                        query = query.filter(getattr(self.model, base_field) <= value)
                else:
                    if hasattr(self.model, field):
                        query = query.filter(getattr(self.model, field) == value)
        return query

    def get_page_with_count(
        self,
        page: int = 1,
        limit: int = 100,
        filters: dict = None
    ) -> tuple[list, int]:
        query = self.db.query(self.model)
        query = self._apply_filters(query, filters)

        total = query.count()
        skip = (page - 1) * limit
        items = query.offset(skip).limit(limit).all()
        return items, total
