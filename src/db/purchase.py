from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from src.db.database import DataBase
from src.db.product import Product
from src.db.user import User


class Purchase(DataBase):
    __tablename__ = 'purchase'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id, ondelete='CASCADE'))
    product_id = Column(Integer, ForeignKey(Product.id, ondelete='CASCADE'))
    price = Column(Integer, nullable=False)
    datetime = Column(DateTime, nullable=False)
    canceled = Column(Boolean, nullable=False, default=False)