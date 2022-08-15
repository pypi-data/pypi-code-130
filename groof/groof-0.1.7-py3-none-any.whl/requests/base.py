from ..objects.tg_objects import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, ForceReply
from ..objects.new import InlineKeyboard

ReplyMarkupT = ReplyKeyboardMarkup | InlineKeyboardMarkup | ReplyKeyboardRemove | ForceReply | InlineKeyboard
