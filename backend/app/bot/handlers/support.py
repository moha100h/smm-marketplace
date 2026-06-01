"""Support handler — tickets."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus, TicketMessage
from app.bot.keyboards.inline import support_kb, back_kb, main_menu_kb
from app.core.i18n import get_text
from app.core.config import settings

router = Router()


class TicketState(StatesGroup):
    subject = State()
    text = State()


@router.callback_query(F.data == "support:main")
async def support_main(cb: CallbackQuery, lang: str):
    admin_links = ", ".join([f"tg://user?id={aid}" for aid in settings.admin_ids_list])
    text = get_text(lang, "support_info", admin_links=admin_links)
    await cb.message.edit_text(text, reply_markup=support_kb(lang).as_markup())
    await cb.answer()


@router.callback_query(F.data == "ticket:new")
async def ticket_new(cb: CallbackQuery, state: FSMContext, lang: str):
    await cb.message.edit_text(get_text(lang, "ticket_subject"))
    await state.set_state(TicketState.subject)
    await cb.answer()


@router.message(TicketState.subject)
async def ticket_subject(msg: Message, state: FSMContext, lang: str):
    await state.update_data(subject=msg.text)
    await msg.answer(get_text(lang, "ticket_text"))
    await state.set_state(TicketState.text)


@router.message(TicketState.text)
async def ticket_text(msg: Message, session: AsyncSession, state: FSMContext, user: User, lang: str):
    data = await state.get_data()
    ticket = Ticket(user_id=user.tg_id, subject=data.get("subject", "بدون موضوع"))
    session.add(ticket)
    await session.flush()

    m = TicketMessage(ticket_id=ticket.id, sender_id=user.tg_id, is_admin=False, text=msg.text)
    session.add(m)
    await session.flush()

    # Notify admins
    for admin_id in settings.admin_ids_list:
        try:
            await msg.bot.send_message(admin_id, f"🎫 تیکت جدید #{ticket.id}\n👤 @{user.tg_id}\n📝 {ticket.subject}\n\n{msg.text}")
        except: pass

    await msg.answer(get_text(lang, "ticket_created", id=ticket.id), reply_markup=main_menu_kb(lang).as_markup())
    await state.clear()
