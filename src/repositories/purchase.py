from sqlalchemy.orm import Session
from src.models.purchase import PurchaseCreate
from src.db.purchase import Purchase


def create_purchase(purchase_info: PurchaseCreate, s: Session):
    purchase = Purchase()
    purchase.user_id = purchase_info.user_id
    purchase.product_id = purchase_info.product_id
    purchase.price = purchase_info.price
    purchase.datetime = purchase_info.datetime
    s.add(purchase)
    try:
        s.commit()
        return purchase
    except Exception as e:
        s.rollback()
        raise e


def cancel_purchase(purchase_id, s: Session):
    purchase = s.query(Purchase).filter(Purchase.id == purchase_id).first()
    purchase.canceled = True
    s.add(purchase)
    try:
        s.commit()
        return purchase
    except:
        s.rollback()


def all_user_purchase(user_id, s: Session):
    return s.query(Purchase).filter(Purchase.user_id == user_id).all()


def all_purchase(limit: int, skip: int, s: Session):
    return s.query(Purchase).limit(limit).offset(skip).all()


def count_user_not_canceled(user_id: int, s: Session):
    return len(list(s.query(Purchase).filter(Purchase.user_id == user_id).filter(Purchase.canceled == False).all()))