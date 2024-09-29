import logging
logging.basicConfig(level=logging.INFO)

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.fsm.context import FSMContext
from aiogram.types import (FSInputFile, CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from peft import PeftModel, LoraConfig
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
from predict import predict_answer
import os

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
hf_path = "Eka-Korn/distillbert-qa-tuned-lora_1.01_v2"
token = os.environ.get('BOT_TOKEN')
bot = Bot(token=token)
storage = MemoryStorage()

dp = Dispatcher(storage=storage)
user_dict: dict[int, dict[str, str]] = {}

def init_model(hf_path, device):
	config = LoraConfig.from_pretrained(hf_path)
	model = AutoModelForQuestionAnswering.from_pretrained(config.base_model_name_or_path)
	model = PeftModel.from_pretrained(model, hf_path).to(device)
	tokenizer = AutoTokenizer.from_pretrained(config.base_model_name_or_path, use_fast=True)
	return model, tokenizer

class FSMFillForm(StatesGroup):
	context = State()
	question = State()

@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        'Привет!\nДавай начнём!\n\n'
        'Чтобы узнать как, отправь команду /help'
    )

@dp.message(Command(commands='help'), StateFilter(default_state))
async def process_help_command(message: Message):
    await message.answer(
		'Чтобы начать заново, отправь команду /cancel\n\n'
		'Чтобы начать поиск ответа, отправь команду /answer\n\n'
	)

@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='Отменять нечего'
    )

@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='Чтобы начать поиск ответа, отправь команду /answer\n\n'
    )
    await state.clear()

@dp.message(Command(commands='answer'), StateFilter(default_state))
async def process_answer_command(message: Message, state: FSMContext):
	await message.answer('Пришлите контекст Вашего вопроса')
	await state.set_state(FSMFillForm.context)

@dp.message(StateFilter(FSMFillForm.context), F.text)
async def process_context_sent(message: Message, state: FSMContext):
	await state.update_data(context=message.text)
	await message.answer('Хорошо, теперь пришлите Ваш вопрос')
	await state.set_state(FSMFillForm.question)

@dp.message(StateFilter(FSMFillForm.context))
async def warning_not_context(message: Message):
    await message.answer(
        text='Это не похоже на текст.'
			'Если хотите начать заново, '
            'отправьте команду /cancel'
    )

@dp.message(StateFilter(FSMFillForm.question), F.text)
async def process_question_sent(message: Message, state: FSMContext):
	await state.update_data(question=message.text)
	user_dict[message.from_user.id] = await state.get_data()

	await message.answer('Отлично.\n\n'
						 'Отправьте команду /make_answer')
	
@dp.message(StateFilter(FSMFillForm.question))
async def warning_not_question(message: Message):
    await message.answer(
        text='Это не похоже на текст.'
			'Если вы хотите начать заново, '
            'отправьте команду /cancel'
    )

@dp.message(Command(commands='make_answer'), StateFilter(default_state))
async def make_answer(message: Message, state: FSMContext):
	if message.from_user.id in user_dict:
		await message.answer(text='Пожалуйста, пожождите.')
		context = user_dict[message.from_user.id]['context']
		question = user_dict[message.from_user.id]['question']
		model, tokenizer = init_model(hf_path, device)
		prediction = predict_answer(model, tokenizer, question, context, device)

		await message.answer(text=prediction)
		user_dict.pop(message.from_user.id)
		await state.clear()

	else:
		await message.answer(
            text='Вы еще не отправили контекст или вопрос. Чтобы начать,'
            'отправьте команду /answer'
        )

@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Извините, моя твоя не понимать')

if __name__ == '__main__':
	dp.run_polling(bot)
