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
from src.repo.db import PlanRepository, UserRepository
from config.db_session import SessionLocal
from src.handlers.strings import get_localized_text

db = SessionLocal()
repo = PlanRepository(db)
language_db = UserRepository(db)

class PagCount(StatesGroup):
    count = State()

base_router = Router()

@base_router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    # Берём текст приветствия для текущего пользователя
    start_text = get_localized_text(user_id, "start_text")

    # Кнопки тоже берём из словаря
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "faq_btn"), callback_data="faq")],
        [InlineKeyboardButton(text=get_localized_text(user_id, "scenarios_btn"), callback_data="scenarios")],
        [InlineKeyboardButton(text="change language", callback_data="change_language")]
    ])
    await message.answer(start_text, reply_markup=markup)
    await state.clear()


@base_router.message(Command("language"))
async def set_language(message: Message, state: FSMContext):
    markup_lang = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Русский', callback_data='set_ru')],
        [InlineKeyboardButton(text='English', callback_data='set_en')],
        
    ])
    await message.answer(text='choose your language', reply_markup=markup_lang)


@base_router.callback_query(F.data =="change_language")
async def set_language(callback: CallbackQuery, state: FSMContext):
    markup_lang = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Русский', callback_data='set_ru')],
        [InlineKeyboardButton(text='English', callback_data='set_en')],
        
    ])
    await callback.message.answer(text='choose your language', reply_markup=markup_lang)
    await callback.answer()


@base_router.callback_query(F.data == "set_ru")
async def put_language(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    language = language_db.add_language(user_id=user_id, language="ru")
    await callback.message.edit_reply_markup(reply_markup=None)

    start_text = get_localized_text(user_id, "start_text")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "faq_btn"), callback_data="faq")],
        [InlineKeyboardButton(text=get_localized_text(user_id, "scenarios_btn"), callback_data="scenarios")],
        [InlineKeyboardButton(text="change language", callback_data="change_language")]
    ])
    await callback.message.edit_text(start_text, reply_markup=markup)
    await callback.answer()
    await state.clear()
    

@base_router.callback_query(F.data == "set_en")
async def put_language(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    language = language_db.add_language(user_id=user_id, language="en")
    await callback.message.edit_reply_markup(reply_markup=None)

    start_text = get_localized_text(user_id, "start_text")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "faq_btn"), callback_data="faq")],
        [InlineKeyboardButton(text=get_localized_text(user_id, "scenarios_btn"), callback_data="scenarios")],
        [InlineKeyboardButton(text="change language", callback_data="change_language")]
    ])
    await callback.message.edit_text(start_text, reply_markup=markup)
    await callback.answer()
    await state.clear()


@base_router.callback_query(F.data == 'faq')
async def ask_and_ques(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    faq_text = get_localized_text(user_id, "faq_text")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]
    ])
    await callback.message.edit_text(faq_text, reply_markup=markup)
    await callback.answer()


@base_router.callback_query(F.data == 'scenarios')
async def my_scenes(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    scenes = await repo.get_plan_by_user_id(user_id)

    # Если нет сценариев
    if scenes[0] == 0:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]
        ])
        no_scenarios_text = get_localized_text(user_id, "no_scenarios_yet")
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
        [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]]

        keyboard_build = []
        for key in scenes[1][:3]:
            keyboard_build.append(
                [InlineKeyboardButton(text=key[0], callback_data=f"get_pg_{str(key[1])}")]
            )

        all_list = keyboard_build + pag_markup

        choose_scenario = get_localized_text(user_id, "choose_scenario")
        await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
        await callback.answer()


@base_router.callback_query(F.data =='pag_to')
async def plus_pag(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']  # текущая страница

    scenes = await repo.get_plan_by_user_id(user_id)
    pages_total = scenes[0] // 3 + 1

    if pages_total <= current_page:
        # уже последняя страница
        no_next_page_text = get_localized_text(user_id, "no_next_page")
        await callback.answer(no_next_page_text, show_alert=True)
    else:
        new_page = current_page + 1
        await state.update_data(count=new_page)

        pag_markup = [[
            InlineKeyboardButton(text="<", callback_data='pag_back'),
            InlineKeyboardButton(text=f"{new_page}/{pages_total}", callback_data='pag_info'),
            InlineKeyboardButton(text=">", callback_data='pag_to')],
            [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]
        ]

        keyboard_build = []
        start_idx = 3 * (new_page - 1)
        end_idx = 3 * new_page
        for key in scenes[1][start_idx:end_idx]:
            keyboard_build.append(
                [InlineKeyboardButton(text=key[0], callback_data=f"get_pg_{str(key[1])}")]
            )

        all_list = keyboard_build + pag_markup
        choose_scenario = get_localized_text(user_id, "choose_scenario")
        await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


@base_router.callback_query(F.data =='pag_back')
async def minus_pag(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']

    scenes = await repo.get_plan_by_user_id(user_id)
    pages_total = scenes[0] // 3 + 1

    if current_page <= 1:
        no_prev_page_text = get_localized_text(user_id, "no_prev_page")
        await callback.answer(no_prev_page_text, show_alert=True)
    else:
        new_page = current_page - 1
        await state.update_data(count=new_page)

        pag_markup = [[
            InlineKeyboardButton(text="<", callback_data='pag_back'),
            InlineKeyboardButton(text=f"{new_page}/{pages_total}", callback_data='pag_info'),
            InlineKeyboardButton(text=">", callback_data='pag_to')],
            [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]
        ]

        keyboard_build = []
        start_idx = 3 * (new_page - 1)
        end_idx = 3 * new_page
        for key in scenes[1][start_idx:end_idx]:
            keyboard_build.append(
                [InlineKeyboardButton(text=key[0], callback_data=f"get_pg_{str(key[1])}")]
            )

        all_list = keyboard_build + pag_markup
        choose_scenario = get_localized_text(user_id, "choose_scenario")
        await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


@base_router.callback_query(F.data=="back")
async def start_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)

    start_text = get_localized_text(user_id, "start_text")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "faq_btn"), callback_data="faq")],
        [InlineKeyboardButton(text=get_localized_text(user_id, "scenarios_btn"), callback_data="scenarios")],
        [InlineKeyboardButton(text=get_localized_text(user_id, "top_users_btn"), callback_data="top_users")]
    ])
    await callback.message.edit_text(start_text, reply_markup=markup)
    await callback.answer()
    await state.clear()


@base_router.callback_query(F.data.startswith("get_pg_"))
async def get_plan_info(callback: CallbackQuery, state: FSMContext):
    plan_id = str(callback.data).replace("get_pg_", "", 1)
    data = await repo.get_plan_by_plan_id(plan_id)
    if data:
        text = data['text']
        user_id = str(callback.from_user.id)

        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back_to_pag')],
                [InlineKeyboardButton(text=get_localized_text(user_id, "main_menu_btn"), callback_data='back')]
            ]
        )
        await callback.message.edit_text(text, reply_markup=markup)
        await callback.answer()
    else:
        await callback.answer("Сценарий не найден", show_alert=True)


@base_router.callback_query(F.data=="back_to_pag")
async def back_main_pag(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']

    scenes = await repo.get_plan_by_user_id(user_id)
    pages_total = scenes[0] // 3 + 1

    pag_markup = [[
        InlineKeyboardButton(text="<", callback_data='pag_back'),
        InlineKeyboardButton(text=f"{current_page}/{pages_total}", callback_data='pag_info'),
        InlineKeyboardButton(text=">", callback_data='pag_to')],
        [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]
    ]

    keyboard_build = []
    start_idx = 3 * (current_page - 1)
    end_idx = 3 * current_page
    for key in scenes[1][start_idx:end_idx]:
        keyboard_build.append(
            [InlineKeyboardButton(text=key[0], callback_data=f"get_pg_{str(key[1])}")]
        )

    all_list = keyboard_build + pag_markup
    choose_scenario = get_localized_text(user_id, "choose_scenario")
    await callback.message.edit_text(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


@base_router.callback_query(F.data.startswith("pag_info"))
async def pag_info(callback: CallbackQuery, state: FSMContext):
    # Это ваш пример с фото (можно вывести что угодно)
    user_id = str(callback.from_user.id)
    await callback.message.delete()

    # Покажем фото, а кнопки тоже берём из словаря
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back_to_pag_photo')],
        [InlineKeyboardButton(text=get_localized_text(user_id, "main_menu_btn"), callback_data='back_photo')]
    ])
    await callback.message.answer_photo(
        photo='AgACAgIAAxkBAAIELmfVMnrsh8Q9Biov2eTyhpbKO-QjAALY9DEbiaeoSnjqNjOW3zCoAQADAgADeAADNgQ',
        reply_markup=markup
    )
    await callback.answer()


@base_router.callback_query(F.data=="back_to_pag_photo")
async def back_main_pag_photo(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    data = await state.get_data()
    current_page = data['count']

    scenes = await repo.get_plan_by_user_id(user_id)
    pages_total = scenes[0] // 3 + 1

    pag_markup = [[
        InlineKeyboardButton(text="<", callback_data='pag_back'),
        InlineKeyboardButton(text=f"{current_page}/{pages_total}", callback_data='pag_info'),
        InlineKeyboardButton(text=">", callback_data='pag_to')],
        [InlineKeyboardButton(text=get_localized_text(user_id, "back_btn"), callback_data='back')]
    ]

    keyboard_build = []
    start_idx = 3 * (current_page - 1)
    end_idx = 3 * current_page
    for key in scenes[1][start_idx:end_idx]:
        keyboard_build.append(
            [InlineKeyboardButton(text=key[0], callback_data=f"get_pg_{str(key[1])}")]
        )

    all_list = keyboard_build + pag_markup
    choose_scenario = get_localized_text(user_id, "choose_scenario")

    await callback.message.delete()
    await callback.message.answer(choose_scenario, reply_markup=InlineKeyboardMarkup(inline_keyboard=all_list))
    await callback.answer()


@base_router.callback_query(F.data=="back_photo")
async def back_photo_callback(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=None)

    start_text = get_localized_text(user_id, "start_text")
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_localized_text(user_id, "faq_btn"), callback_data="faq")],
        [InlineKeyboardButton(text=get_localized_text(user_id, "scenarios_btn"), callback_data="scenarios")],
        [InlineKeyboardButton(text="change language", callback_data="change_language")]
    ])
    await callback.message.delete()
    await callback.message.answer(start_text, reply_markup=markup)
    await callback.answer()
    await state.clear()


@base_router.message(F.photo)
async def sending_photo(message: Message) -> None:
    user_id = str(message.from_user.id)
    photo_data = message.photo[-1]
    text_photo = get_localized_text(user_id, "photo_message")
    await message.answer(f"{text_photo} {photo_data}")