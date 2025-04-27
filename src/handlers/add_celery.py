# create_handlers.py

import asyncio
import os

from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from dotenv import load_dotenv

print("йоу")
from src.services.creation_scenario import get_get_gpt_info
from src.repo.db import WishListRepository, UserRepository, CeleryRepository, WishListItemRepository
from config.db_session import SessionLocal
from src.handlers.strings import ALL_TEXT, ALL_BUTTON

db = SessionLocal()
wishlist_db = WishListRepository(db)
user_db = UserRepository(db)
celery_db = CeleryRepository(db)
router = Router()
wishlistitems_db = WishListItemRepository(db)
class CeleryFSM(StatesGroup):
    cost = State()
    label = State()
    about = State()
    photo = State()
    category = State()


class ListFSM(StatesGroup):
    list_id = State()


@router.callback_query(F.data.startswith("get_celery_for_id_"))
async def choose_option(callback: CallbackQuery, state: FSMContext):
    list_id = str(callback.data).replace("get_celery_for_id_", "", 1)
    await state.set_state(ListFSM.list_id)
    await state.update_data(list_id=list_id)
    markup = [[InlineKeyboardButton(text="Одежда", callback_data="cat_clothes")],
              [InlineKeyboardButton(text="Обувь", callback_data="cat_shoes")],
              [InlineKeyboardButton(text="Косметика", callback_data="cat_cosmetics")],
              [InlineKeyboardButton(text="В меню", callback_data="back")]

            #   [InlineKeyboardButton(text="Электроника", callback_data="cat_electronics"),],
            #   [InlineKeyboardButton(text="Спорт", callback_data="cat_sports")],
            #   [InlineKeyboardButton(text="Для детей", callback_data="cat_for_children")],
            #   [InlineKeyboardButton(text="Аксессуары", callback_data="cat_aksessuars")],
            #   [InlineKeyboardButton(text="Для дома", callback_data="cat_for_home")]
    ]
    await callback.message.answer(text='Выберите категорию', reply_markup=InlineKeyboardMarkup(inline_keyboard=markup))


@router.callback_query(F.data.startswith("cat_"))
async def get_clothes_category(callback: CallbackQuery, state: FSMContext):
        category = str(callback.data).replace("cat_", "", 1)
        all_clothes = celery_db.list_celery_by_category(category)
        new_file = await state.get_data()
        list_id = new_file.get("list_id")
        markup = []
        for key in all_clothes:
                markup.append([InlineKeyboardButton(
                        text=f"{key['label']}", callback_data=f"get_info_ad{key['celery_id']}")])
            
        
        markup.append([InlineKeyboardButton(text=f"Назад в категории", callback_data=f"get_celery_for_id_{list_id}")])

        await callback.message.answer(text="Вот товары по данной категории", reply_markup=InlineKeyboardMarkup(inline_keyboard=markup))



@router.callback_query(F.data.startswith("get_info_ad"))
async def get_plan_info(callback: CallbackQuery):
    celery_id = str(callback.data).replace("get_info_ad", "", 1)
    data = celery_db.get_celery_by_id(celery_id=celery_id)
    if data:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добавить", callback_data=f"add_celery_{celery_id}")],
            [InlineKeyboardButton(text="Назад", callback_data=f"go_back_to_c{data['category']}")]
        ])
        await callback.message.answer_photo(
            photo=data['photo'],  # file_id из полученного фото
            caption=f"Новый товар:\n\n"
                    f"Название: {data['label']}\n"
                    f"Описание: {data['about']}\n"
                    f"Цена: {data['cost']}\n"
                    f"Категория: {data['category']}",
            reply_markup=markup
        )
        
    else:
        await callback.message.answer('Непредвиденная ошибка')


@router.callback_query(F.data.startswith("go_back_to_c"))
async def return_data_choose(callback: CallbackQuery, state: FSMContext):
    category = str(callback.data).replace("go_back_to_c", "", 1)
    all_clothes = celery_db.list_celery_by_category(category)
    new_file = await state.get_data()
    list_id = new_file.get("list_id")
    markup = []
    for key in all_clothes:
            markup.append([InlineKeyboardButton(
                    text=f"{key['label']}", callback_data=f"get_info_ad{key['celery_id']}")])
        
    
    markup.append([InlineKeyboardButton(text=f"Назад в категории", callback_data=f"get_celery_for_id_{list_id}")])

    await callback.message.answer(text="Вот товары по данной категории", reply_markup=InlineKeyboardMarkup(inline_keyboard=markup))


@router.callback_query(F.data.startswith("add_celery_"))
async def add_new_celery_for_user(callback: CallbackQuery, state: FSMContext):

    celery_id = str(callback.data).replace("add_celery_", "", 1)
    data = await state.get_data()
    list_id = data["list_id"]
    wishlistitems_db.add_item(wishlist_id=list_id, celery_id=celery_id)

    await callback.answer(text="Добавлено", show_alert=True)
    await callback.answer()

    celery = celery_db.get_celery_by_id(celery_id)
    all_clothes = celery_db.list_celery_by_category(celery["category"])

    if all_clothes == []:
        print("Начало работы 2")
        await callback.message.answer(text="Данная категория пуста")
    
    else:
        markup = []
        for key in all_clothes:
            
            markup.append([InlineKeyboardButton(
                    text=f"{key["label"]}", callback_data=f"get_info_ad{key["celery_id"]}")])
            

        markup.append([InlineKeyboardButton(text=f"Назад в категории", callback_data=f"get_celery_for_id_{list_id}")])
        

        await callback.message.answer(text="Вот товары по данной категории", reply_markup=InlineKeyboardMarkup(markup))

















@router.message(Command('create_celery'))
async def new_celery_create(message: Message, state: FSMContext):
    await message.answer("Введите название")
    await state.set_state(CeleryFSM.label)


@router.message(CeleryFSM.label)
async def celery_label_add(message: Message, state: FSMContext):
    await state.update_data(label=message.text)
    await state.set_state(CeleryFSM.about)
    await message.answer('Введите описание')



@router.message(CeleryFSM.about)
async def celery_about_add(message: Message, state: FSMContext):
    await state.update_data(about=message.text)
    await state.set_state(CeleryFSM.photo)
    await message.answer('Пришлите фото')



@router.message(CeleryFSM.photo)
async def celery_photo_add(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1])
    await state.set_state(CeleryFSM.cost)
    await message.answer('Введите цену')




@router.message(CeleryFSM.cost)
async def celery_cost_add(message: Message, state: FSMContext):
    await state.update_data(cost=message.text)
    await state.set_state(CeleryFSM.category)
    await message.answer('Введите категорию')


from aiogram.types import InputMediaPhoto, Message
from aiogram.fsm.context import FSMContext


@router.message(CeleryFSM.category)
async def celery_category_add(message: Message, state: FSMContext):
    # Получаем все данные из состояния
    await state.update_data(category=message.text)

    data = await state.get_data()
    
    
    try:
        # Отправляем фото с подписью
        await message.answer_photo(
            photo=data['photo'].file_id,  # file_id из полученного фото
            caption=f"Новый товар:\n\n"
                    f"Название: {data['label']}\n"
                    f"Описание: {data['about']}\n"
                    f"Цена: {data['cost']}\n"
                    f"Категория: {data['category']}"
        )
        
        # Сохраняем в базу
        new = celery_db.add_celery(
            photo=data['photo'].file_id,
            category=data['category'],
            label=data['label'],
            about=data['about'],
            cost=float(data['cost'])
        )
        
        print(new["celery_id"])
        await message.answer("Товар успешно добавлен!")

        new_one = celery_db.get_celery_by_id(new["celery_id"])
        await message.answer_photo(
            photo=new_one['photo'],  # file_id из полученного фото
            caption=f"Новый товар:\n\n"
                    f"Название: {new_one['label']}\n"
                    f"Описание: {new_one['about']}\n"
                    f"Цена: {new_one['cost']}\n"
                    f"Категория: {new_one['category']}"
        )
        
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")
    finally:
        await state.clear()