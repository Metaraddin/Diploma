from sqlalchemy.orm import Session
from src.models.product import ProductCreate, ProductEdit
from src.db.product import Product


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