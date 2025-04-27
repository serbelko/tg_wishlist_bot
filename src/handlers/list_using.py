

from typing import List, Dict, Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from config.db_session import engine, SessionLocal
from src.models import User
from src.repo.db import CeleryRepository, WishListRepository, UserRepository, WishListItemRepository  # синхронный репозиторий
from src.handlers.strings import ALL_TEXT, ALL_BUTTON

# DEBUG: какие таблицы есть
db = SessionLocal()

wishlist_db = WishListRepository(db)
wishlistitem_db = WishListItemRepository(db)
celery_db = CeleryRepository(db)
inspector = inspect(engine)
print("→ TABLES IN DB:", inspector.get_table_names())

router = Router()
PAGE_SIZE = 5  # сколько вишлистов показываем за страницу

class ListCreation(StatesGroup):
    name = State()
    list_type = State()

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from typing import Optional, List, Dict

PAGE_SIZE = 5  # Константа для размера страницы

@router.callback_query(F.data == "my_list_callback")
async def show_my_lists(callback: CallbackQuery, state: FSMContext):
    await state.update_data(page=1)
    await _render_page(callback.message, callback.from_user.id, state)
    await callback.answer()

@router.callback_query(F.data == "next_page")
async def on_next_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("page", 1)
    await state.update_data(page=current_page + 1)
    await _render_page(callback.message, callback.from_user.id, state)
    await callback.answer()

@router.callback_query(F.data == "prev_page")
async def on_prev_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("page", 1)
    await state.update_data(page=max(1, current_page - 1))
    await _render_page(callback.message, callback.from_user.id, state)
    await callback.answer()

async def _render_page(message: Message, tg_user_id: int, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 1)
    
    db: Session = SessionLocal()
    try:
        user_db = UserRepository(db)
        user: Optional[User] = db.query(User).filter(User.user_id == str(tg_user_id)).first()
        if not user:
            new_user = str(message.from_user.id)
            name_user = str(message.from_user.full_name)
            user_db.add_user(new_user, name_user)
            user: Optional[User] = db.query(User).filter(User.user_id == str(tg_user_id)).first()

        repo = WishListRepository(db)
        total = repo.count_wishlists_by_user(user.user_id)
        max_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        page = max(1, min(page, max_page))
        offset = (page - 1) * PAGE_SIZE

        slice_ = repo.list_wishlists_by_user_page(user.user_id, PAGE_SIZE, offset)

        # Формирование текста
        text = "Ваши списки:" if slice_ else "У вас пока нет созданных списков."
        if slice_:
            text = "Вот твои списки"

        # Формирование клавиатуры
        inline_keyboard = []
        
        # Кнопки списков
        for wl in slice_:
            inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"📋 {wl['name']} ({wl['list_type']})",
                    callback_data=f"wl_{wl['id']}"
                )
            ])
        
        # Пагинация
        pagination_row = []
        pagination_count = []
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton(text="⬅️", callback_data="prev_page")
            )
        
        pagination_count.append(
            InlineKeyboardButton(
                text=f"{page}/{max_page}",
                callback_data="page_info"
            )
        )
        
        if page < max_page:
            pagination_row.append(
                InlineKeyboardButton(text="➡️", callback_data="next_page")
            )
        
        if pagination_count:
            inline_keyboard.append(pagination_count)
        if pagination_row:
            inline_keyboard.append(pagination_row)
        
        # Основные кнопки
        inline_keyboard.append([
            InlineKeyboardButton(
                text=ALL_BUTTON["create_list"], 
                callback_data="create_list_callback"
            ),
            InlineKeyboardButton(
                text=ALL_BUTTON["check_users"], 
                callback_data="check_users_callback"
            )
        ])

        markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        # Редактирование сообщения
        try:
            await message.edit_text(text, reply_markup=markup)
        except:
            await message.answer(text, reply_markup=markup)

    except Exception as e:
        await message.answer("Произошла ошибка при загрузке списков")
    finally:
        db.close()

class FSMwishlist(StatesGroup):
    my_wl = State()


@router.callback_query(F.data.startswith("wl_"))
async def open_my_wl(callback: CallbackQuery, state: FSMContext):
    wl_id = str(callback.data).replace("wl_", "", 1)
    await state.set_state(FSMwishlist.my_wl)
    await state.update_data(my_wl=wl_id)
    wish_list = wishlist_db.get_wishlist_by_id(wl_id)
    texts = f"Вот виш-лист\nИмя: {wish_list['name']}\n"
    items = wishlistitem_db.list_items_by_wishlist(wl_id)
    celery_markup = []
    for i in items:
        celerys = celery_db.get_celery_by_id(str(i["celery_id"]))
        celery_name = celerys["label"]
        celery_id= celerys["celery_id"]
        celery_markup.append([InlineKeyboardButton(text=f"{celery_name}", callback_data=f"check_in_my_{celery_id}")])
    
    markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")],
              [InlineKeyboardButton(text="Добавить товары", callback_data=f"get_celery_for_id_{wish_list["id"]}")]]
 
    
    celery_markup += markup
    await callback.message.answer(text=texts, 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=celery_markup))




@router.callback_query(F.data.startswith('check_in_my_'))
async def checking_my_goods(callback: CallbackQuery, state: FSMContext):
    celery_id = str(callback.data).replace("check_in_my_", "", 1)
    data = celery_db.get_celery_by_id(celery_id=celery_id)
    new_data_wow = await state.get_data()
    wl_id = new_data_wow["my_wl"]
    if data:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Удалить товар", callback_data=f"del_sel{celery_id}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"wl_{wl_id}")]
        ])
        await callback.message.answer_photo(
            photo=data['photo'],  # file_id из полученного фото
            caption=f"Ваш товар товар:\n\n"
                    f"Название: {data['label']}\n"
                    f"Описание: {data['about']}\n"
                    f"Цена: {data['cost']}\n"
                    f"Категория: {data['category']}",
            reply_markup=markup
        )


@router.callback_query(F.data.startswith('del_sel'))
async def del_my_good_from_lenta(callback: CallbackQuery, state: FSMContext):
    celery_id = str(callback.data).replace("del_sel", "", 1)
    data = await state.get_data()
    wl_id = data["my_wl"]
    status = wishlistitem_db.get_status_by_celery_id(celery_id)
    if status != "active":
        await callback.answer(
        text="Не советуем его удалять (намек)",
        show_alert=True  # False для верхнего уведомления
    )

    else:
        wishlistitem_db.remove_item(celery_id)
        wish_list = wishlist_db.get_wishlist_by_id(wl_id)
        texts = f"Вот виш-лист\nИмя: {wish_list['name']}\n\n"
        items = wishlistitem_db.list_items_by_wishlist(wl_id)
        celery_markup = []
        for i in items:
            celerys = celery_db.get_celery_by_id(str(i["celery_id"]))
            celery_name = celerys["label"]
            celery_id= celerys["celery_id"]
            celery_markup.append([InlineKeyboardButton(text=f"{celery_name}", callback_data=f"check_in_my_{celery_id}")])
        
        markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")],
                [InlineKeyboardButton(text="Добавить товары", callback_data=f"get_celery_for_id_{wish_list["id"]}")]]
    
        
        celery_markup += markup
        await callback.message.answer(text=texts, 
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=celery_markup))
        await state.clear()

    