from typing import List, Optional
from uuid import uuid4
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update, func, create_engine
from sqlalchemy.orm import sessionmaker

from src.models import User, Celery, WishList, WishListItem, Base

def init_db(engine):
    Base.metadata.create_all(bind=engine)

class CeleryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_celery(self, photo: str, category: str, label: str, about: str, cost: float) -> dict:
        celery_id = str(uuid4())
        new_celery = Celery(
            celery_id=celery_id,
            photo=photo,
            category=category,
            label=label,
            about=about,
            cost=cost
        )
        self.db.add(new_celery)
        self.db.commit()
        self.db.refresh(new_celery)
        return new_celery.to_dict()
    
    def list_celery_by_category(self, category: str) -> List[dict]:
        """
        Возвращает товары указанной категории.
        Если category пустая строка или None - возвращает все товары.
        """
        query = self.db.query(Celery)
        
        if category:  # Фильтруем только если указана категория
            query = query.filter(Celery.category == category)
            
        items = query.all()
        if items is None:
            return []
        return [item.to_dict() for item in items]

    def get_celery_by_id(self, celery_id: str) -> Optional[dict]:
        try:
            uuid.UUID(celery_id)
        except ValueError:
            return None

        celery_item = self.db.query(Celery).filter(Celery.celery_id == celery_id).first()
        return celery_item.to_dict() if celery_item else None

    def list_celery(self) -> List[dict]:
        return [item.to_dict() for item in self.db.query(Celery).all()]

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_user(self, user_id: str, name: str) -> dict:
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if user:
                return user.to_dict()
            
            new_user = User(user_id=user_id, name=name)
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user.to_dict()
        except Exception as e:
            self.db.rollback()
            raise e

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        user = self.db.query(User).filter(User.user_id == user_id).first()
        return user.to_dict() if user else None
    

    

    
    def list_users_page(self, page: int, size: int) -> List[dict]:
        # Вычисляем смещение
        offset = page * size
        
        # Выполняем запрос с пагинацией
        result = self.db.query(User) \
                    .offset(offset) \
                    .limit(size) \
                    .all()
                    
        return [user.to_dict() for user in result]
    
    def count_users(self):
        return self.db.query(func.count(User.user_id)).scalar()
    
    def list_all_users(self) -> List[dict]:
        """Возвращает список всех пользователей в виде словарей"""
        users = self.db.query(User).all()
        plan_lst = [[plan.user_id, plan.name] for plan in users]
        return [len(plan_lst), plan_lst]

class WishListRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_wishlist(self, user_id: str, name: str, list_type: str) -> dict:
        wishlist_id = str(uuid4())
        new_wl = WishList(
            id=wishlist_id,
            user_id=user_id,
            name=name,
            list_type=list_type
        )
        self.db.add(new_wl)
        self.db.commit()
        self.db.refresh(new_wl)
        return new_wl.to_dict()

    def get_wishlist_by_id(self, wishlist_id: str) -> Optional[dict]:
        wl = self.db.query(WishList).filter(WishList.id == wishlist_id).first()
        return wl.to_dict() if wl else None

    def list_wishlists_by_user(self, user_id: str) -> List[dict]:
        return [wl.to_dict() for wl in self.db.query(WishList)
                             .filter(WishList.user_id == user_id)
                             .all()]

    def update_wishlist(self, wishlist_id: str, 
                      name: Optional[str] = None, 
                      list_type: Optional[str] = None) -> Optional[dict]:
        values = {}
        if name: values['name'] = name
        if list_type: values['list_type'] = list_type
        
        if not values:
            return None

        self.db.query(WishList).filter(WishList.id == wishlist_id).update(values)
        self.db.commit()
        wl = self.db.query(WishList).get(wishlist_id)
        return wl.to_dict() if wl else None

    def delete_wishlist(self, wishlist_id: str) -> bool:
        result = self.db.query(WishList).filter(WishList.id == wishlist_id).delete()
        self.db.commit()
        return result > 0
    
    def count_wishlists_by_user(self, user_id: str) -> int:
        return self.db.query(func.count()).filter(WishList.user_id == user_id).scalar()

    def list_wishlists_by_user_page(self, user_id: str, 
                                 limit: int, offset: int) -> List[dict]:
        return [wl.to_dict() for wl in self.db.query(WishList)
                                .filter(
                                    WishList.user_id == user_id,
                                    WishList.list_type != 'private_choose'
                                )
                                .limit(limit)
                                .offset(offset)
                                .all()]

class WishListItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_item(self, wishlist_id: str, celery_id: str, 
               status: str = "active", count: int = 1) -> dict:
        new_item = WishListItem(
            wishlist_id=wishlist_id,
            celery_id=celery_id,
            status=status,
            count=count
        )
        self.db.add(new_item)
        self.db.commit()
        self.db.refresh(new_item)
        return new_item.to_dict()

    def remove_item(self, item_id: str) -> bool:
        try:
            uuid.UUID(item_id)
        except ValueError:
            return None
        result = self.db.query(WishListItem).filter(WishListItem.celery_id == item_id).delete()
        self.db.commit()
        return result > 0

    def update_item(self, item_id: str, 
                status: Optional[str] = None, 
                count: Optional[int] = None) -> Optional[dict]:
        
        uuid.UUID(item_id)
        filter_condition = WishListItem.celery_id == item_id

        values = {}
        if status is not None:  # Явная проверка на None
            values['status'] = status
        if count is not None:   # Явная проверка на None
            values['count'] = count
            
        if not values:
            return None

        # Обновляем запись
        self.db.query(WishListItem) \
            .filter(filter_condition) \
            .update(values)
        self.db.commit()

        # Получаем обновлённую запись
        item = self.db.query(WishListItem).filter(filter_condition).first()
        return item.to_dict() if item else None

    def list_items_by_wishlist(self, wishlist_id: str) -> List[dict]:
        return [item.to_dict() for item in self.db.query(WishListItem)
                                .filter(WishListItem.wishlist_id == wishlist_id)
                                .all()]


    def get_status_by_celery_id(self, celery_id: str) -> Optional[str]:
        """
        Возвращает статус элемента вишлиста по celery_id.
        Возвращает None, если запись не найдена или celery_id невалиден.
        """
        try:
            # Проверяем валидность UUID (если требуется)
            uuid.UUID(celery_id)
        except ValueError:
            return None

        item = self.db.query(WishListItem) \
            .filter(WishListItem.celery_id == celery_id) \
            .first()

        return item.status if item else None