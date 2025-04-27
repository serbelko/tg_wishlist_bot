# create_handlers.py

import asyncio
import os

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from dotenv import load_dotenv


from src.services.creation_scenario import get_get_gpt_info
from src.repo.db import WishListRepository, UserRepository
from config.db_session import SessionLocal
from src.handlers.strings import ALL_TEXT, ALL_BUTTON, LIST_TYPES

db = SessionLocal()
wishlist_db = WishListRepository(db)
user_db = UserRepository(db)
router = Router()

class UserInfo(StatesGroup):
    school_lesson = State()
    school_class = State()
    description = State()
    type_lesson = State()
    lesson_level = State()
    extra_time = State()
    text = State()


class ListCreation(StatesGroup):
    name = State()
    list_type = State()


@router.callback_query(F.data=="create_list_callback")
async def start_create_scenario(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(ALL_TEXT["creation_text"])
    await state.set_state(ListCreation.name)
    await callback.answer()
    

@router.message(ListCreation.name)
async def choose_list_type(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ListCreation.list_type)
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Приватный", callback_data="private_choose"),
        InlineKeyboardButton(text="Общедоступный", callback_data="for_all_choose"),

    ]])
    await message.answer(text="Выбери тип твоего вишлиста", reply_markup=markup)


@router.callback_query(F.data=="private_choose")
async def end_creation(callback: CallbackQuery, state: FSMContext):
    await state.update_data(list_type=str(callback.data))
    fsm_data = await state.get_data()
    user_id = str(callback.from_user.id)
    user_name = str(callback.from_user.full_name)
    user_db.add_user(user_id, name=user_name)
    name = fsm_data.get('name')
    type = fsm_data.get('list_type')
    callback.answer()
    wish_list = wishlist_db.create_wishlist(user_id=user_id, name=name, list_type=type)
    markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")],
              [InlineKeyboardButton(text="Добавить товары", callback_data=f"get_celery_for_id_{wish_list["id"]}")]]
    await callback.message.answer(text=f"Вот твой лист\nИмя: {name}\nТип: {LIST_TYPES[type]}\n", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=markup))
    await state.clear()


@router.callback_query(F.data=="for_all_choose")
async def end_creation(callback: CallbackQuery, state: FSMContext):
    await state.update_data(list_type=str(callback.data))
    fsm_data = await state.get_data()
    user_id = str(callback.from_user.id)
    user_name = str(callback.from_user.full_name)
    user_db.add_user(user_id, name=user_name)
    name = fsm_data.get('name')
    type = fsm_data.get('list_type')
    callback.answer()
    wish_list = wishlist_db.create_wishlist(user_id=user_id, name=name, list_type=type)
    markup = [[InlineKeyboardButton(text="В меню", callback_data="back_menu")],
              [InlineKeyboardButton(text="Добавить товары", callback_data=f"get_celery_for_id_{wish_list["id"]}")]]
    await callback.message.answer(text=f"Вот твой лист\nИмя: {name}\nТип: {LIST_TYPES[type]}\n", 
                         reply_markup=InlineKeyboardMarkup(inline_keyboard=markup))
    await state.clear()



@router.callback_query(F.data=="back_menu")
async def start_back(callback: CallbackQuery, state: FSMContext):
    
    # Берём текст приветствия для текущего пользователя
    

    # Кнопки тоже берём из словаря
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ALL_BUTTON["create_list"], callback_data="create_list_callback")],
        [InlineKeyboardButton(text=ALL_BUTTON["check_my_list"], callback_data="my_list_callback")],
        [InlineKeyboardButton(text=ALL_BUTTON["check_users"], callback_data="check_users_callback")]])
    await callback.message.answer(ALL_TEXT['start_text'], reply_markup=markup)
    await state.clear()
    await callback.answer()

# @router.message(Command('create'))
# async def start_create_scenario(message: types.Message, state: FSMContext):
#     user_id = str(message.from_user.id)
    

#     bot_message = await message.answer(subject_question)
#     await state.update_data(bot_message_id=bot_message.message_id)
#     await state.set_state(UserInfo.school_lesson)





# @router.message(UserInfo.school_lesson)
# async def choose_class(message: Message, state: FSMContext):
#     user_id = str(message.from_user.id)
#     await state.update_data(school_lesson=message.text)

#     data = await state.get_data()
#     old_bot_message_id = data.get("bot_message_id")

#     # Удаляем предыдущие сообщения (по возможности)
#     if old_bot_message_id:
#         try:
#             await message.bot.delete_message(chat_id=message.chat.id, message_id=old_bot_message_id)
#         except Exception as e:
#             print(f"Ошибка удаления сообщения бота: {e}")
#     try:
#         await message.delete()
#     except Exception as e:
#         print(f"Ошибка удаления сообщения пользователя: {e}")

#     # Подтверждаем выбор предмета
#     chosen_subject_text = get_localized_text(user_id, "you_chose_subject", subject=message.text)
#     await message.answer(chosen_subject_text)

#     # Предлагаем выбрать класс
#     class_question = get_localized_text(user_id, "class_question")

#     back_subject_btn = get_localized_text(user_id, "back_subject_btn")
#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=str(i), callback_data=f"class_{i}") for i in range(1, 7)],
#         [InlineKeyboardButton(text=str(i), callback_data=f"class_{i}") for i in range(7, 12)],
#         [InlineKeyboardButton(text=back_subject_btn, callback_data="back_school_lesson")]
#     ])

#     bot_message = await message.answer(class_question, reply_markup=markup)
#     await state.update_data(bot_message_id=bot_message.message_id)
#     await state.set_state(UserInfo.school_class)


# @router.callback_query(F.data == "back_school_lesson")
# async def back_to_school_lesson(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     subject_question = get_localized_text(user_id, "subject_question")

#     await callback.message.edit_reply_markup(reply_markup=None)
#     await callback.message.edit_text(subject_question)
#     await state.set_state(UserInfo.school_lesson)


# @router.callback_query(F.data.startswith("class_"))
# async def choose_theme(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     school_class = callback.data.split("_")[1]
#     await state.update_data(school_class=school_class)

#     chosen_class_text = get_localized_text(user_id, "you_chose_class", school_class=school_class)
#     await callback.message.edit_text(chosen_class_text)

#     # Кнопка назад
#     back_class_btn = get_localized_text(user_id, "back_class_btn")
#     theme_question = get_localized_text(user_id, "theme_question")
#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=back_class_btn, callback_data='back_class')]
#     ])
#     bot_message = await callback.message.answer(theme_question, reply_markup=markup)
#     await state.update_data(bot_message_id=bot_message.message_id)
#     await state.set_state(UserInfo.type_lesson)


# @router.callback_query(F.data == 'back_class')
# async def back_to_class(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     class_question = get_localized_text(user_id, "class_question")
#     back_subject_btn = get_localized_text(user_id, "back_subject_btn")

#     await callback.message.edit_reply_markup(reply_markup=None)

#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=str(i), callback_data=f"class_{i}") for i in range(1, 7)],
#         [InlineKeyboardButton(text=str(i), callback_data=f"class_{i}") for i in range(7, 12)],
#         [InlineKeyboardButton(text=back_subject_btn, callback_data="back_school_lesson")]
#     ])
#     await callback.message.edit_text(class_question, reply_markup=markup)
#     await state.set_state(UserInfo.school_class)


# @router.message(UserInfo.type_lesson)
# async def choose_level(message: Message, state: FSMContext):
#     user_id = str(message.from_user.id)
#     await state.update_data(type_lesson=message.text)

#     data = await state.get_data()
#     old_bot_message_id = data.get("bot_message_id")
#     if old_bot_message_id:
#         try:
#             await message.bot.delete_message(chat_id=message.chat.id, message_id=old_bot_message_id)
#         except Exception as e:
#             print(f"Ошибка удаления сообщения бота: {e}")
#     try:
#         await message.delete()
#     except Exception as e:
#         print(f"Ошибка удаления сообщения пользователя: {e}")

#     chosen_theme_text = get_localized_text(user_id, "you_chose_theme", theme=message.text)
#     await message.answer(chosen_theme_text)

#     level_question = get_localized_text(user_id, "level_question")
#     level_base_btn = get_localized_text(user_id, "level_base_btn")
#     level_profile_btn = get_localized_text(user_id, "level_profile_btn")
#     back_theme_btn = get_localized_text(user_id, "back_theme_btn")

#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=level_base_btn, callback_data="level_base"),
#          InlineKeyboardButton(text=level_profile_btn, callback_data="level_profiled")],
#         [InlineKeyboardButton(text=back_theme_btn, callback_data="back_type")]
#     ])
#     await message.answer(level_question, reply_markup=markup)
#     await state.set_state(UserInfo.lesson_level)


# @router.callback_query(F.data == "back_type")
# async def back_to_type(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     theme_question = get_localized_text(user_id, "theme_question")

#     await callback.message.edit_reply_markup(reply_markup=None)
#     await callback.message.edit_text(theme_question)
#     await state.set_state(UserInfo.type_lesson)


# @router.callback_query(F.data.startswith("level_"))
# async def choose_time(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     if callback.data == "level_base":
#         chosen_level = get_localized_text(user_id, "level_base_btn")  # "Базовый" / "Basic"
#     else:
#         chosen_level = get_localized_text(user_id, "level_profile_btn")  # "Профильный" / "Advanced"

#     await state.update_data(lesson_level=chosen_level)

#     you_chose_level = get_localized_text(user_id, "you_chose_level", level=chosen_level)
#     await callback.message.edit_text(you_chose_level)

#     time_question = get_localized_text(user_id, "time_question")
#     back_level_btn = get_localized_text(user_id, "back_level_btn")
#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=back_level_btn, callback_data='back_level')]
#     ])
#     bot_message = await callback.message.answer(time_question, reply_markup=markup)
#     await state.update_data(bot_message_id=bot_message.message_id)
#     await state.set_state(UserInfo.extra_time)


# @router.callback_query(F.data == "back_level")
# async def back_to_level(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     level_question = get_localized_text(user_id, "level_question")
#     level_base_btn = get_localized_text(user_id, "level_base_btn")
#     level_profile_btn = get_localized_text(user_id, "level_profile_btn")
#     back_theme_btn = get_localized_text(user_id, "back_theme_btn")

#     await callback.message.edit_reply_markup(reply_markup=None)

#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=level_base_btn, callback_data="level_base"),
#          InlineKeyboardButton(text=level_profile_btn, callback_data="level_profiled")],
#         [InlineKeyboardButton(text=back_theme_btn, callback_data="back_type")]
#     ])
#     await callback.message.edit_text(level_question, reply_markup=markup)
#     await state.set_state(UserInfo.lesson_level)


# @router.message(UserInfo.extra_time)
# async def choose_desc(message: Message, state: FSMContext):
#     user_id = str(message.from_user.id)
#     await state.update_data(extra_time=message.text)

#     data = await state.get_data()
#     old_bot_message_id = data.get("bot_message_id")
#     if old_bot_message_id:
#         try:
#             await message.bot.delete_message(chat_id=message.chat.id, message_id=old_bot_message_id)
#         except Exception as e:
#             print(f"Ошибка удаления сообщения бота: {e}")
#     try:
#         await message.delete()
#     except Exception as e:
#         print(f"Ошибка удаления сообщения пользователя: {e}")

#     chosen_time_text = get_localized_text(user_id, "you_chose_time", time=message.text)
#     await message.answer(chosen_time_text)

#     desc_question = get_localized_text(user_id, "desc_question")
#     back_time_btn = get_localized_text(user_id, "back_time_btn")
#     markup = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=back_time_btn, callback_data='back_time')]
#     ])
#     bot_message = await message.answer(desc_question, reply_markup=markup)
#     await state.update_data(bot_message_id=bot_message.message_id)
#     await state.set_state(UserInfo.description)


# @router.callback_query(F.data == "back_time")
# async def back_to_time(callback: CallbackQuery, state: FSMContext):
#     user_id = str(callback.from_user.id)
#     time_question = get_localized_text(user_id, "time_question")

#     await callback.message.edit_reply_markup(reply_markup=None)
#     await callback.message.edit_text(time_question)
#     await state.set_state(UserInfo.extra_time)


# @router.message(UserInfo.description)
# async def finalize_scenario(message: Message, state: FSMContext):
#     user_id = str(message.from_user.id)
#     data = await state.update_data(description=message.text)
#     data = await state.get_data()

#     old_bot_message_id = data.get("bot_message_id")
#     if old_bot_message_id:
#         try:
#             await message.bot.delete_message(chat_id=message.chat.id, message_id=old_bot_message_id)
#         except Exception as e:
#             print(f"Ошибка удаления сообщения бота: {e}")
#     try:
#         await message.delete()
#     except Exception as e:
#         print(f"Ошибка удаления сообщения пользователя: {e}")

#     chosen_desc_text = get_localized_text(user_id, "you_chose_desc", desc=message.text)
#     await message.answer(chosen_desc_text)

#     # "Загрузка..." (процесс генерации)
#     generating_text = get_localized_text(user_id, "scenario_generating")
#     user_id = str(message.from_user.id)
#     language = language_db.get_language_by_id(user_id)
#     bot_msg = await message.answer(generating_text)

#     # Генерация сценария
#     text = get_get_gpt_info(
#         subject=data["school_lesson"],
#         class_int=data["school_class"],
#         description=data["description"],
#         theme=data["type_lesson"],
#         hard=data["lesson_level"],
#         time_lesson=data["extra_time"],
#         tests=False,
#         homework=False,
#         language = language
#     )

#     await bot_msg.delete()

#     # Высылаем финальный текст
#     await message.answer(text)

#     # Добавляем в БД
#     plan = repo.add_plan(user_id, text=text, label=f"""{data["school_lesson"]},{data["type_lesson"]}""")  # label можно тоже формировать
#     scenario_created_text = get_localized_text(user_id, "scenario_created")
#     await message.answer(scenario_created_text)

#     await state.clear()
