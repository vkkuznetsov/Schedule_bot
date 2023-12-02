import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.types.force_reply import ForceReply
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from keyboards import builder1, get_keyboard, get_schedule, return_from_schedule, get_profile, get_numbers, friend_add, \
    friend_menu, get_schedule_from_friends, return_from_schedule_friends, confirm_delete_friends

from main import login_to_modeus, modeus_cont
from reload_events import reload_profile_events
from weather import get_forecast
from bd_connect import show_profile, show_events_this_week, show_events_today, \
    show_events_tomorrow, show_events_next_week, reset_user_info, reset_database, show_friends, delete_all_friends, \
    show_friend_by_index, show_events_today_friend, show_events_tomorrow_friend, show_events_this_week_friend, \
    show_events_next_week_friend, reset_user_info_all_events, reset_name_certain

from config import token, token_weather, token_test

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token_test)
dp = Dispatcher()


class Form(StatesGroup):
    waiting_for_name = State()
    wait_input = State()
    synced_name = State()
    waiting_for_friend = State()
    working_borwser = State()


@dp.message(Command('start'))
async def menu(message: types.Message, state: FSMContext):
    await state.set_state(Form.wait_input)
    await message.answer('Добро пожаловать! Добавьте свое ФИО для загрузки расписания', reply_markup=ForceReply())


@dp.message(Command("menu"))
@dp.message(F.text.lower() == 'меню')
async def menu(message: types.Message):
    await message.answer('Вот ваше Меню!\nКлавиатура указана снизу⏬', reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("menu_"))
async def callbacks_num(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "additional":
        await callback.answer(
            text=f"ну покав разработке",
            show_alert=True
        )
    elif action == "profile":
        user_id, name, index, second_name, secon_index = await show_profile(user_id=callback.message.chat.id)

        friends_list, count = await show_friends(callback.message.chat.id)
        names = [i[1] for i in friends_list]
        formatted_names = "\n".join(f"{index + 1}. {name}" for index, name in enumerate(names))
        await callback.message.edit_text(
            f'<strong>Профиль:</strong>\n\nID: {user_id}\nВаше ФИО: {name}\n\nДополнительный профиль {second_name}\n\nСписок друзей:\n{formatted_names}\n\nУведомления:',
            reply_markup=get_profile(), parse_mode='HTML')

    elif action == "friends":
        friends_list, count = await show_friends(callback.message.chat.id)
        names = [i[1] for i in friends_list]
        if count > 0:
            formatted_names = "\n".join(f"{index + 1}. {name}" for index, name in enumerate(names))
            await callback.message.edit_text(
                f"Список друзей:\n{formatted_names}", reply_markup=friend_menu(count)
            )
        elif count == 0:
            await callback.message.edit_text(
                f'Не найдено ни одного друга! \nДобавьте его для того чтобы всегда знать его расписание с помощью кнопки ниже🔽',
                reply_markup=friend_add())
    elif action == 'schedule':
        profile_id, name, index, second_name, second_index = await show_profile(callback.message.chat.id)
        await callback.message.edit_text(f'Расписание <u><strong>{name}</strong></u>', reply_markup=get_schedule(),
                                         parse_mode='HTML')


@dp.callback_query(F.data.startswith('friend_'))
async def adding_friend(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == 'add':
        await state.set_state(Form.waiting_for_friend)
        await callback.message.answer('Введите ФИО друга', reply_markup=ForceReply())
    elif action == 'deleteAll':

        await callback.message.edit_text('Вы уверены что хотите удалить всех друзей?',
                                         reply_markup=confirm_delete_friends())
    elif action.isdigit():
        name_friend, index_friend = await show_friend_by_index(callback.message.chat.id, int(action))
        await callback.message.edit_text(f'Выбран {name_friend} {index_friend}',
                                         reply_markup=get_schedule_from_friends())
        await state.update_data(name=name_friend, index=index_friend)


@dp.callback_query(F.data.startswith('confirmation_'))
async def deleting_friend_list(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == 'yes':
        await delete_all_friends(callback.message.chat.id)
        await callback.message.edit_text(f'Список друзей очищен!', reply_markup=get_keyboard())
    elif action == 'no':
        await callback.message.edit_text('Вот ваше Меню!\nКлавиатура указана снизу⏬', reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith('scheduleFriends_'))
async def schedule_for_friend(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    data = await state.get_data()
    name = data.get('name')
    index = data.get('index')

    if action == "today":
        await callback.message.edit_text(f'{await show_events_today_friend(name, index)}',
                                         reply_markup=return_from_schedule_friends(), parse_mode="HTML")
    elif action == "tomorrow":
        await callback.message.edit_text(f'{await show_events_tomorrow_friend(name, index)}',
                                         reply_markup=return_from_schedule_friends(), parse_mode="HTML")
    elif action == "this":
        await callback.message.edit_text(
            f'{await show_events_this_week_friend(name, index)}',
            reply_markup=return_from_schedule_friends(), parse_mode="HTML")
    elif action == 'next':
        await callback.message.edit_text(
            f'{await show_events_next_week_friend(name, index)}',
            reply_markup=return_from_schedule_friends(), parse_mode="HTML")
    elif action == "prev":
        await callback.message.edit_text('Вот ваше Меню!\nКлавиатура указана снизу⏬', reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("schedule_"))
async def callbacks_num(callback: types.CallbackQuery):
    action = callback.data.split("_")[1]

    if action == "today":
        await callback.message.edit_text(f'{await show_events_today(callback.message.chat.id)}',
                                         reply_markup=return_from_schedule(), parse_mode="HTML")
    elif action == "tomorrow":
        await callback.message.edit_text(f'{await show_events_tomorrow(callback.message.chat.id)}',
                                         reply_markup=return_from_schedule(), parse_mode="HTML")
    elif action == "this":
        await callback.message.edit_text(
            f'{await show_events_this_week(callback.message.chat.id)}',
            reply_markup=return_from_schedule(), parse_mode="HTML")
    elif action == 'next':
        await callback.message.edit_text(
            f'{await show_events_next_week(callback.message.chat.id)}',
            reply_markup=return_from_schedule(), parse_mode="HTML")
    elif action == "prev":
        await callback.message.edit_text('Вот ваше Меню!\nКлавиатура указана снизу⏬', reply_markup=get_keyboard())


@dp.callback_query(F.data.startswith("profile_"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]

    if action == "changeName":
        await state.set_state(Form.wait_input)
        await reset_user_info(callback.message.chat.id)

        await callback.message.answer('Введите ФИО для изменения', reply_markup=ForceReply())

    elif action == "changeFriends":
        await callback.message.edit_text('Список дурзей:')

    elif action == "reload":
        await state.set_state(Form.working_borwser)

        profile_id, name, index, second_name, second_index = await show_profile(user_id=callback.message.chat.id)
        await callback.message.edit_text(f'Ожидайте...')

        # удаляем старые записи

        await reset_user_info_all_events(user_id=profile_id)

        # добавляем пользоватея с новыми записями
        await reload_profile_events(FIO=name, id_telegram=profile_id, index_student=index)

        await callback.message.edit_text(f'Готово!', reply_markup=get_keyboard())

        await state.set_state(Form.synced_name)

    elif action == "notifications":
        await callback.message.edit_text('УВЕДОМЛЕНИЯ:\n')


@dp.message(F.text.lower() == 'пары сегодня')
async def profile(message: types.Message):
    await message.answer(f'{await show_events_today(message.chat.id)}', parse_mode="HTML")


@dp.message(F.text.lower() == 'пары завтра')
async def profile(message: types.Message):
    await message.answer(f'{await show_events_tomorrow(message.chat.id)}', parse_mode="HTML")


@dp.message(F.text.lower() == 'пара неделя')
async def profile(message: types.Message):
    await message.answer(f'{await show_events_this_week(message.chat.id)}', parse_mode="HTML")


@dp.message(F.text.lower() == 'пары след неделя')
async def profile(message: types.Message):
    await message.answer(f'{await show_events_next_week(message.chat.id)}', parse_mode="HTML")


@dp.message(F.text.lower() == 'погода')
async def menu(message: types.Message):
    await message.answer(f'{get_forecast(token_weather)}', reply_markup=builder1.as_markup(resize_keyboard=True))


@dp.message(F.text.lower() == 'ресет')
async def menu(message: types.Message):
    await message.answer(f'{await reset_database()}', reply_markup=builder1.as_markup(resize_keyboard=True))


@dp.message(F.text.lower() == 'профиль')
async def profile(message: types.Message):
    await message.answer(f'Профиль\n{await show_profile(message.chat.id)}')


@dp.message(F.text.lower() == 'старт')
async def profile(message: types.Message, state: FSMContext):
    await state.set_state(Form.wait_input)
    await message.answer('Добро пожаловать! Добавьте свое ФИО для загрузки расписания', reply_markup=ForceReply())


@dp.message(Form.wait_input)
async def process_user_input(message: types.Message, state: FSMContext):
    await state.set_state(Form.synced_name)
    full_name = message.text

    await message.answer(f'Загрузка...🔄!\nОна будет длиться 15-20 секунд.')

    str_output, answer_code, page = await login_to_modeus(message.text, message.from_user.id, 1)

    if answer_code == 0:
        await message.answer(f'Ни одного пользователя {full_name} не найдено!')
    elif answer_code == 1:
        ans = f'✅Готово, {full_name}! Ваше ФИО было успешно добавлено.'
        await message.answer(ans,
                             reply_markup=builder1.as_markup(resize_keyboard=True))
    else:

        await message.answer(f'Выберите профиль который вы ищите{str_output}', parse_mode="HTML",
                             reply_markup=get_numbers(answer_code))

        await state.update_data(full_name=full_name, user_id=message.from_user.id, page=page,
                                insert_table_code=1)


@dp.message(Form.waiting_for_friend)
async def process_user_input(message: types.Message, state: FSMContext):
    await state.set_state(Form.synced_name)
    full_name = message.text

    await message.answer(f'Загрузка...🔄!\nОна будет длиться 15-20 секунд.')

    str_output, answer_code, page = await login_to_modeus(message.text, message.from_user.id, 2)

    if answer_code == 0:
        await message.answer(f'Ни одного пользователя {full_name} не найдено!')

    elif answer_code == 1:
        ans = f'✅Готово, друг {full_name} был добавлен!'
        await message.answer(ans,
                             reply_markup=get_keyboard())
    else:
        await message.answer(f'Выберите профиль который вы ищите{str_output}', parse_mode="HTML",
                             reply_markup=get_numbers(answer_code))
        await state.update_data(full_name=full_name, user_id=message.from_user.id, page=page,
                                insert_table_code=2)


@dp.callback_query(F.data.startswith("many_"))
async def callbacks_num(callback: types.CallbackQuery, state: FSMContext):
    action = int(callback.data.split("_")[1])

    data = await state.get_data()
    full_name = data.get('full_name')
    user_id = data.get('user_id')
    page = data.get('page')
    insert_table_code = data.get('insert_table_code')
    await callback.message.edit_text(f'Загрузка профиля {full_name}')
    await modeus_cont(page, full_name, user_id, insert_table_code, action)
    await callback.message.edit_text(f'✅Готово, ФИО {full_name} добавлено', reply_markup=get_keyboard())


@dp.message(Form.synced_name)
async def cmd_start(message: types.Message):
    await message.answer(
        f'❌Команда не найдена❌ \nИспользуйте /menu', reply_markup=builder1.as_markup(resize_keyboard=True))


@dp.message()
async def menu(message: types.Message):
    await message.answer(f'Добавьте ваше ФИО для корректной работы бота',
                         reply_markup=builder1.as_markup(resize_keyboard=True))


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
