from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TOKEN
from random import randint

storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)

class Game(StatesGroup):
    guesser_wait = State()
    guesser_answer = State()
    riddler_begin = State()
    riddler = State()


async def start_polling():
    await dp.start_polling()

@dp.message_handler(commands=['start']) #подпрограмма старта бота/инструкция к боту
async def cmd_start(message: types.Message):
    await message.answer('Если вы хотите отгадать число, то напишите команду /guesser\n Если вы хотите загадать число, то напишите /riddler')


@dp.message_handler(commands=['guesser']) #подпрограмма начала игры, в которой пользователь отгадывает загаданное компьютером число
async def guess_num(message: types.Message, state: FSMContext):
    await message.answer("Отгадайте число от 1 до 100")
    await state.set_state(Game.guesser_wait.state)


@dp.message_handler(state=Game.guesser_wait)#подпрограмма для загадывания числа ботом
async def input(message: types.Message, state: FSMContext):
    await state.update_data(randomchislo=randint(1, 100))
    await state.set_state(Game.guesser_answer.state)
    await moreless(message, state)


@dp.message_handler(state=Game.guesser_answer)#проверка числа, которое ввел пользователь, бот отвечает больше/меньше чем его число или пользователь угадал число, которое загадал бот
async def moreless(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():  # проверяем число ли сообщение
        if data['randomchislo'] < int(message.text):
            await message.answer('Меньше')
        elif data['randomchislo'] > int(message.text):
            await message.answer('Больше')
        else:
            await message.reply('Вы отгадали загаданное число')
            await state.finish()
    else:
        await message.answer('Ошибка: вы ввели не число!')


@dp.message_handler(commands=['riddler'])#подпрограмма страрта игры, в которой пользователь загадывает число, в подпрограмме задаются значения от которых бот угадывает число
async def riddlermain(message: types.Message, state: FSMContext):
    await message.answer("Если бот угадал число напишите 'угадал', если число меньше/больше загаданного, то напишите 'меньше'/'больше' ")
    await state.update_data(min=1)
    await state.update_data(max=100)
    await state.set_state(Game.riddler.state)
    await riddlerrand(message, state)


async def riddlerrand(message: types.Message, state: FSMContext):#подпрограмма в которой бот создает случайное число в определенном интервале
    data = await state.get_data()
    if data['min'] >= data['max']:
        await message.answer("вы меня обманули! Игра окончена")
        await state.finish()
        return
    sluchaenoechislo = randint(data['min'], data['max'])
    await state.update_data(sluchaen=sluchaenoechislo)
    await message.answer(sluchaenoechislo)
    await state.set_state(Game.riddler.state)


@dp.message_handler(state=Game.riddler)#подпрограмма в которой пользователь изменяет интервал создания случайного числа командами больше/меньше
async def riddlertry(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if(message.text=="больше" or message.text== "меньше" or message.text=="угадал"):
        if message.text == "больше":
            await state.update_data(min=data["sluchaen"]+1)
            await riddlerrand(message, state)
        elif message.text == "меньше":
            await state.update_data(max=data["sluchaen"]-1)
            await riddlerrand(message, state)
        elif message.text == "угадал":
            await message.answer("Я угадал число, игра окончена")
            await state.finish()
    else:
        await message.answer("введите корректную команду")
