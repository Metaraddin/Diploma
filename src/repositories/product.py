from sqlalchemy.orm import Session
from src.models.product import ProductCreate, ProductEdit
from src.db.product import Product
from src.repositories import purchase
from src.models.purchase import PurchaseCreate
from datetime import datetime


def create_product(manga_id: int, product_info: ProductCreate, s: Session):
    product = Product()
    product.manga_id = manga_id
    product.volume = product_info.volume
    product.chapter = product_info.chapter
    product.description = product_info.description
    product.publisher = product_info.publisher
    product.language = product_info.language
    product.translator = product_info.translator
    product.price_rub = product_info.price_rub
    product.quantity = product_info.quantity
    s.add(product)
    try:
        s.commit()
        return product
    except:
        s.rollback()
        return None


def edit_product(product_id: int, product_info: ProductEdit, s: Session):
    product = s.query(Product).filter(Product.id == product_id).first()
    product_info = product_info.dict(exclude_unset=True)
    if 'volume' in product_info.keys(): product.volume = product_info['volume']
    if 'chapter' in product_info.keys(): product.chapter = product_info['chapter']
    if 'description' in product_info.keys(): product.description = product_info['description']
    if 'publisher' in product_info.keys(): product.publisher = product_info['publisher']
    if 'language' in product_info.keys(): product.language = product_info['language']
    if 'translator' in product_info.keys(): product.translator = product_info['translator']
    if 'price_rub' in product_info.keys(): product.price_rub = product_info['price_rub']
    if 'quantity' in product_info.keys(): product.quantity = product_info['quantity']
    s.add(product)
    try:
        s.commit()
        return product
    except:
        s.rollback()
        return None


def get_product(product_id: int, s: Session):
    return s.query(Product).filter(Product.id == product_id).first()


def get_product_by_manga(manga_id: int, s: Session, limit: int = 100, skip: int = 0):
    return s.query(Product).filter(Product.manga_id == manga_id).limit(limit).offset(skip).all()


def get_all_product(s: Session, limit: int = 100, skip: int = 0):
    return s.query(Product).limit(limit).offset(skip).all()


def delete_product(product_id: int, s: Session):
    product = s.query(Product).filter(Product.id == product_id).first()
    s.delete(product)
    try:
        s.commit()
        return product
    except:
        s.rollback()
        return None


def get_price_from_user(user_id: int, product_id: int, s: Session):
    product_price = s.query(Product).filter(Product.id == product_id).first().price_rub
    user_count = purchase.count_user_not_canceled(user_id=user_id, s=s)
    if user_count < 10:
        return float(product_price) * (1 - (0.02 * user_count))
    else:
        return float(product_price) * 0.8


def buy_product(user_id: int, product_id: int, s: Session):
    product = s.query(Product).filter(Product.id == product_id).first()
    if product.quantity <= 0:
        return None
    product.quantity -= 1
    s.add(product)
    try:
        s.commit()
    except:
        s.rollback()
        return
    pc = PurchaseCreate(
        user_id=user_id,
        product_id=product_id,
        price=get_price_from_user(user_id, product_id, s),
        datetime=datetime.now())
    return purchase.create_purchase(pc, s=s)


def cancel_purchase(purchase_id: int, s: Session):
    product_id = purchase.cancel_purchase(purchase_id=purchase_id, s=s).product_id
    product = s.query(Product).filter(Product.id == product_id).first()
    product.quantity += 1
    s.add(product)
    try:
        s.commit()
        return product.quantity
    except:
        s.rollback()


def add_quantity(id: int, quantity: int, s: Session):
    product = s.query(Product).filter(Product.id == id).first()
    product.quantity += quantity
    s.add(product)
    s.commit()
    return product
