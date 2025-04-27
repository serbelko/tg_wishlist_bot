import asyncio
import os

from aiogram import Bot, Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from src.repo.db import UserRepository, CeleryRepository, WishListItemRepository, WishListRepository
from config.db_session import SessionLocal
from src.handlers.strings import ALL_TEXT, ALL_BUTTON

db = SessionLocal()
user_db = UserRepository(db)
celery_db = CeleryRepository(db)
wishlist_db = WishListRepository(db)
wishlistitem_db =WishListItemRepository(db)

class PagCount(StatesGroup):
    count = State()





base_router = Router()

@base_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    # Берём текст приветствия для текущего пользователя
    

    # Кнопки тоже берём из словаря
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ALL_BUTTON["create_list"], callback_data="create_list_callback")],
        [InlineKeyboardButton(text=ALL_BUTTON["check_my_list"], callback_data="my_list_callback")],
        [InlineKeyboardButton(text=ALL_BUTTON["check_users"], callback_data="check_users_callback")]
    ])

    new_user = str(message.from_user.id)
    name_user = str(message.from_user.full_name)
    user_db.add_user(new_user, name_user)
    await message.answer(ALL_TEXT['start_text'], reply_markup=markup)
    await state.clear()


@base_router.callback_query(F.data == 'check_users_callback')
async def all_my_users_data(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    scenes = user_db.list_all_users()

    if scenes[0] == 0:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data='back')]
        ])
        no_scenarios_text = "Пользователи не найдены"
        await callback.message.edit_text(no_scenarios_text, reply_markup=markup)
        await callback.answer()
    else:
        # есть сценарии — пагинация
        await state.update_data(count=1)  # первая страница

        data_count = 1
        pages_total = scenes[0] // 3 + 1  # всего страниц

        pag_markup = [[
            InlineKeyboardButton(text="<", callback_data='pag_back'),
            InlineKeyboardButton(text=f"{data_count}/{pages_total}", callback_data='pag_info'),
            InlineKeyboardButton(text=">", callback_data='pag_to')
        ],
        [InlineKeyboardButton(text="Назад", callback_data='back')]]

        keyboard_build = []
        for key in scenes[1][:3]:
            keyboard_build.append(
                [InlineKeyboardButton(text=key[1], callback_data=f"get_pg_{str(key[0])}")]
            )

        all_list = keyboard_build + pag_markup

        choose_scenario = ALL_TEXT["choose_user"]
        await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
        await callback.answer()


@base_router.callback_query(F.data =='pag_to')
async def plus_pag(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']  # текущая страница

    scenes = user_db.list_all_users()
    pages_total = scenes[0] // 3 + 1

    if pages_total <= current_page:
        # уже последняя страница
        no_next_page_text = "Дальше пользователей нет"
        await callback.answer(no_next_page_text, show_alert=True)
    else:
        new_page = current_page + 1
        await state.update_data(count=new_page)

        pag_markup = [[
            InlineKeyboardButton(text="<", callback_data='pag_back'),
            InlineKeyboardButton(text=f"{new_page}/{pages_total}", callback_data='pag_info'),
            InlineKeyboardButton(text=">", callback_data='pag_to')],
            [InlineKeyboardButton(text="Назад", callback_data='back')]
        ]

        keyboard_build = []
        start_idx = 3 * (new_page - 1)
        end_idx = 3 * new_page
        for key in scenes[1][start_idx:end_idx]:
            keyboard_build.append(
                [InlineKeyboardButton(text=key[1], callback_data=f"get_pg_{str(key[0])}")]
            )

        all_list = keyboard_build + pag_markup
        choose_scenario = "Выберите пользователя"
        await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


@base_router.callback_query(F.data =='pag_back')
async def minus_pag(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']

    scenes = user_db.list_all_users()
    pages_total = scenes[0] // 3 + 1

    if current_page <= 1:
        no_prev_page_text = "Уже меньше нуля"
        await callback.answer(no_prev_page_text, show_alert=True)
    else:
        new_page = current_page - 1
        await state.update_data(count=new_page)

        pag_markup = [[
            InlineKeyboardButton(text="<", callback_data='pag_back'),
            InlineKeyboardButton(text=f"{new_page}/{pages_total}", callback_data='pag_info'),
            InlineKeyboardButton(text=">", callback_data='pag_to')],
            [InlineKeyboardButton(text="Назад", callback_data='back')]
        ]

        keyboard_build = []
        start_idx = 3 * (new_page - 1)
        end_idx = 3 * new_page
        for key in scenes[1][start_idx:end_idx]:
            keyboard_build.append(
                [InlineKeyboardButton(text=key[1], callback_data=f"get_pg_{str(key[0])}")]
            )

        all_list = keyboard_build + pag_markup
        choose_scenario = "выбрать "
        await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


@base_router.callback_query(F.data=="back")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ALL_BUTTON["create_list"], callback_data="create_list_callback")],
        [InlineKeyboardButton(text=ALL_BUTTON["check_my_list"], callback_data="my_list_callback")],
        [InlineKeyboardButton(text=ALL_BUTTON["check_users"], callback_data="check_users_callback")]
    ])

    await callback.message.edit_text(ALL_TEXT['start_text'], reply_markup=markup)
    await state.clear()


# @base_router.callback_query(F.data.startswith("get_pg_"))
# async def get_plan_info(callback: CallbackQuery, state: FSMContext):
#     plan_id = str(callback.data).replace("get_pg_", "", 1)
#     data = "pass"
#     if data:
#         text = "pass"
#         user_id = str(callback.from_user.id)

#         markup = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="Назад", callback_data='back_to_pag')],
#                 [InlineKeyboardButton(text="назад", callback_data='back')]
#             ]
#         )
#         await callback.message.edit_text(text, reply_markup=markup)
#         await callback.answer()
#     else:
#         await callback.answer("Сценарий не найден", show_alert=True)


@base_router.callback_query(F.data=="back_to_pag")
async def back_main_pag(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']

    scenes = user_db.list_all_users()
    pages_total = scenes[0] // 3 + 1

    pag_markup = [[
        InlineKeyboardButton(text="<", callback_data='pag_back'),
        InlineKeyboardButton(text=f"{current_page}/{pages_total}", callback_data='pag_info'),
        InlineKeyboardButton(text=">", callback_data='pag_to')],
        [InlineKeyboardButton(text="Назад", callback_data='back')]
    ]

    keyboard_build = []
    start_idx = 3 * (current_page - 1)
    end_idx = 3 * current_page
    for key in scenes[1][start_idx:end_idx]:
        keyboard_build.append(
            [InlineKeyboardButton(text=key[0], callback_data=f"get_pg_{str(key[1])}")]
        )

    all_list = keyboard_build + pag_markup
    choose_scenario = "йоу"
    await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


class FSMcheckusers(StatesGroup):
    usering_id = State()
    page = State()
    new_celery = State()
    user_list = State()


PAGE_SIZE = 5  # Константа для размера страницы
@base_router.callback_query(F.data.startswith("get_pg_"))
async def go_to_the_profile(callback: CallbackQuery, state: FSMContext):
    user = str(callback.data).replace("get_pg_", "", 1)
    await state.set_state(FSMcheckusers.usering_id)
    await state.update_data(usering_id=user)
    await state.update_data(page=1)
    await _render_page(callback.message, user, state)
    await callback.answer()


@base_router.callback_query(F.data == "next_page_prof")
async def on_next_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("page", 1)
    await state.update_data(page=current_page + 1)
    user = data.get("usering_id")
    await _render_page(callback.message, user, state)
    await callback.answer()


@base_router.callback_query(F.data == "prev_page_prof")
async def on_prev_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("page", 1)
    await state.update_data(page=max(1, current_page - 1))
    user = data.get("usering_id")
    await _render_page(callback.message, user, state)
    await callback.answer()


async def _render_page(message: Message, user_id: int, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 1)
    
    try:
        
        repo = WishListRepository(db)
        total = repo.count_wishlists_by_user(user_id)
        max_page = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
        page = max(1, min(page, max_page))
        offset = (page - 1) * PAGE_SIZE

        slice_ = repo.list_wishlists_by_user_page(user_id, PAGE_SIZE, offset)

        # Формирование текста
        text = "Ваши списки:" if slice_ else "У этого пользователя пока нет списков."
        if slice_:
            text = "Вот все списки"

        # Формирование клавиатуры
        inline_keyboard = []
        
        # Кнопки списков
        for wl in slice_:
            inline_keyboard.append([
                InlineKeyboardButton(
                    text=f"📋 {wl['name']}",
                    callback_data=f"wl_p{wl['id']}"
                )
            ])
        
        # Пагинация
        pagination_row = []
        pagination_count = []
        if page > 1:
            pagination_row.append(
                InlineKeyboardButton(text="⬅️", callback_data="prev_page_prof")
            )
        
        pagination_count.append(
            InlineKeyboardButton(
                text=f"{page}/{max_page}",
                callback_data="page_info"
            )
        )
        
        if page < max_page:
            pagination_row.append(
                InlineKeyboardButton(text="➡️", callback_data="next_page_prof")
            )
        
        if pagination_count:
            inline_keyboard.append(pagination_count)
        if pagination_row:
            inline_keyboard.append(pagination_row)
        
        # Основные кнопки
        inline_keyboard.append([
            InlineKeyboardButton(
                text="меню", 
                callback_data="back_menu"
            ),
            InlineKeyboardButton(
                text="Назад", 
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


@base_router.callback_query(F.data.startswith("wl_p"))
async def open_my_wl(callback: CallbackQuery, state: FSMContext):
    wl_id = str(callback.data).replace("wl_p", "", 1)
    await state.update_data(user_list=wl_id)
    wish_list = wishlist_db.get_wishlist_by_id(wl_id)
    texts = f"Вот лист этого пользователя\nНазвание списка: {wish_list['name']}\n\n "
    items = wishlistitem_db.list_items_by_wishlist(wl_id)
    celery_markup = []
    for i in items:
        celerys = celery_db.get_celery_by_id(str(i["celery_id"]))
        celery_name = celerys["label"]

        celery_name = celerys["label"]
        status = i.get("status")
        if status == "оплачено":
            celery_name += f" (✅Оплачено)"
        elif status =="бронировано":
            celery_name += f" (☑️Бронировано)"

        celery_id= celerys["celery_id"]
        celery_markup.append([InlineKeyboardButton(text=f"{celery_name}", callback_data=f"pres_{celery_id}")])
    
    markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")]]
    
    celery_markup += markup
    await callback.message.answer(text=texts, 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=celery_markup))



@base_router.callback_query(F.data.startswith("pres_"))
async def choose_what_to_do(callback: CallbackQuery, state: FSMContext):
    wl_id = str(callback.data).replace("pres_", "", 1)
    await state.update_data(new_celery=wl_id)
    markup = [[InlineKeyboardButton(text="Оплатить", callback_data="pay_for_wish"),
               InlineKeyboardButton(text="Забронировать", callback_data="bron_for_wish")]]
    status = wishlistitem_db.get_status_by_celery_id(wl_id)
    if status != "active":
        await callback.answer(
        text="Нельзя добавить - уже добавлен другим польозвателес",
        show_alert=True  # False для верхнего уведомления
    )
    else:
        new_one = celery_db.get_celery_by_id(wl_id)
        await callback.message.answer_photo(
                photo=new_one['photo'],  # file_id из полученного фото
                caption=f"Новый товар:\n\n"
                        f"Название: {new_one['label']}\n"
                        f"Описание: {new_one['about']}\n"
                        f"Цена: {new_one['cost']}\n"
                        f"Категория: {new_one['category']}", reply_markup=InlineKeyboardMarkup(inline_keyboard=markup)
            )
        await state.update_data(new_selery=wl_id)


@base_router.callback_query(F.data == "pay_for_wish")
async def paying_for_celery(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_id = data.get("new_celery")    
    wishlistitem_db.update_item(item_id=item_id, status="оплачено")
    await callback.message.answer("Оплачено")
    list_id = data.get("user_list")

    wish_list = wishlist_db.get_wishlist_by_id(list_id)
    texts = f"Вот лист этого пользователя\nНазвание списка: {wish_list['name']}\n "
    items = wishlistitem_db.list_items_by_wishlist(list_id)
    celery_markup = []
    for i in items:
        celerys = celery_db.get_celery_by_id(str(i["celery_id"]))
        celery_name = celerys["label"]
        status = i.get("status")
        if status == "оплачено":
            celery_name += f" (✅Оплачено)"
        elif status =="бронировано":
            celery_name += f" (☑️Бронировано)"
        
        celery_id= celerys["celery_id"]
        await callback.message.answer(str(celery_id))
        celery_markup.append([InlineKeyboardButton(text=f"{celery_name}", callback_data=f"pres_{celery_id}")])
    
    markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")]]
    
    celery_markup += markup
    await callback.message.answer(text=texts, 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=celery_markup))




@base_router.callback_query(F.data == "bron_for_wish")
async def paying_for_celery(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    item_id = data.get("new_celery")
    await callback.message.answer(str(item_id))
    wishlistitem_db.update_item(item_id=item_id, status="бронировано")
    await callback.message.answer("Бронировано")
    list_id = data.get("user_list")

    wish_list = wishlist_db.get_wishlist_by_id(list_id)
    texts = f"Вот лист этого пользователя\nНазвание списка: {wish_list['name']}\n "
    items = wishlistitem_db.list_items_by_wishlist(list_id)
    celery_markup = []
    for i in items:
        celerys = celery_db.get_celery_by_id(str(i["celery_id"]))
        celery_name = celerys["label"]
        status = i.get("status")
        if status == "оплачено":
            celery_name += f" (✅Оплачено)"
        elif status =="бронировано":
            celery_name += f" (☑️Бронировано)"
        
        celery_id= celerys["celery_id"]
        celery_markup.append([InlineKeyboardButton(text=f"{celery_name}", callback_data=f"pres_{celery_id}")])
    
    markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")]]
    
    celery_markup += markup
    await callback.message.answer(text=texts, 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=celery_markup))

