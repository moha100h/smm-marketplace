"""Admin handler — stats, deposits, orders, users, tickets, management."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus, Transaction, TransactionType
from app.models.ticket import Ticket, TicketStatus, TicketMessage
from app.core.i18n import get_text
from app.core.config import settings
from app.bot.keyboards.inline import admin_menu_kb, back_kb

router = Router()


class AdminState(StatesGroup):
    add_balance = State()
    ticket_reply = State()


def fmt(n: float) -> str:
    return f"{n:,.0f}"


def is_admin(user: User) -> bool:
    return user.is_admin or user.tg_id in settings.admin_ids_list


@router.callback_query(F.data == "admin:stats")
async def admin_stats(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    total_users = await session.scalar(select(func.count(User.id)))
    total_orders = await session.scalar(select(func.count(Order.id)))
    total_revenue = await session.scalar(select(func.sum(Order.total_cost)) or 0)
    pending_dep = await session.scalar(select(func.count(Payment.id)).where(Payment.status == PaymentStatus.SUBMITTED))

    text = get_text(lang, "admin_stats",
        users=total_users or 0,
        orders=total_orders or 0,
        revenue=fmt(total_revenue),
        pending=pending_dep or 0,
    )
    await cb.message.edit_text(text, reply_markup=back_kb(lang, "admin:main").as_markup())
    await cb.answer()


# ── Deposits ──
@router.callback_query(F.data == "admin:deposits")
async def admin_deposits(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    r = await session.execute(
        select(Payment).where(Payment.status == PaymentStatus.SUBMITTED).order_by(desc(Payment.created_at)).limit(20)
    )
    deps = r.scalars().all()
    if not deps:
        text = get_text(lang, "no_pending_deposits")
    else:
        lines = ["\U0001f4b3 <b>درخواست\u200cهای واریز</b>\n"]
        for d in deps:
            lines.append(f"\U0001f539 #{d.id} | {fmt(d.amount)} | <code>{d.user_id}</code> | {d.method.value}")
        text = "\n".join(lines)

    kb = InlineKeyboardBuilder()
    for d in deps:
        kb.row(
            InlineKeyboardButton(text=f"\u2705 #{d.id}", callback_data=f"admin:dep:approve:{d.id}"),
            InlineKeyboardButton(text=f"\u274c #{d.id}", callback_data=f"admin:dep:reject:{d.id}"),
        )
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:main"))

    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:dep:"))
async def admin_deposit_action(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    parts = cb.data.split(":")
    action, pid = parts[2], int(parts[3])
    payment = await session.get(Payment, pid)
    if not payment:
        await cb.answer("\u274c یافت نشد", show_alert=True)
        return

    r = await session.execute(select(User).where(User.tg_id == payment.user_id))
    target = r.scalar_one_or_none()
    if not target:
        await cb.answer("\u274c کاربر یافت نشد", show_alert=True)
        return

    if action == "approve":
        payment.status = PaymentStatus.CONFIRMED
        target.wallet_balance += payment.amount
        tx = Transaction(user_id=target.tg_id, type=TransactionType.DEPOSIT, amount=payment.amount,
                         balance_before=target.wallet_balance - payment.amount, balance_after=target.wallet_balance,
                         description="Deposit approved")
        session.add(tx)
        try:
            await cb.bot.send_message(target.tg_id, get_text(lang, "deposit_approved", amount=fmt(payment.amount), balance=fmt(target.wallet_balance)))
        except: pass
        await cb.message.edit_text(f"\u2705 واریز #{pid} تأیید شد.")
    else:
        payment.status = PaymentStatus.REJECTED
        try:
            await cb.bot.send_message(target.tg_id, get_text(lang, "deposit_rejected", amount=fmt(payment.amount)))
        except: pass
        await cb.message.edit_text(f"\u274c واریز #{pid} رد شد.")
    await session.flush()
    await cb.answer()


# ── Orders ──
@router.callback_query(F.data == "admin:orders")
async def admin_orders(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    r = await session.execute(select(Order).order_by(desc(Order.created_at)).limit(20))
    orders = r.scalars().all()
    lines = ["\U0001f4e6 <b>سفارشات اخیر</b>\n"]
    for o in orders:
        lines.append(f"\U0001f539 #{o.id} | {o.status.value} | {fmt(o.total_cost)} | <code>{o.user_id}</code>")
    text = "\n".join(lines)

    kb = InlineKeyboardBuilder()
    for o in orders:
        kb.row(InlineKeyboardButton(text=f"\U0001f4cb #{o.id}", callback_data=f"admin:ord:view:{o.id}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:main"))

    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:ord:view:"))
async def admin_order_view(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    oid = int(cb.data.split(":")[3])
    order = await session.get(Order, oid)
    if not order:
        await cb.answer("\u274c", show_alert=True)
        return
    text = (
        f"\U0001f4e6 <b>سفارش #{order.id}</b>\n\n"
        f"\U0001f464 کاربر: <code>{order.user_id}</code>\n"
        f"\U0001f6d2 سرویس: <code>{order.service_id}</code>\n"
        f"\U0001f522 تعداد: {order.quantity}\n"
        f"\U0001f4b0 هزینه: {fmt(order.total_cost)}\n"
        f"\U0001f4ca وضعیت: {order.status.value}\n"
        f"\U0001f4dd داده: {order.form_data or '-'}"
    )
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="\u2705 تکمیل", callback_data=f"admin:ord:completed:{oid}"),
        InlineKeyboardButton(text="\U0001f504 پردازش", callback_data=f"admin:ord:processing:{oid}"),
    )
    kb.row(
        InlineKeyboardButton(text="\u274c رد", callback_data=f"admin:ord:rejected:{oid}"),
        InlineKeyboardButton(text="\u21a9\ufe0f بازگشت", callback_data=f"admin:ord:refunded:{oid}"),
    )
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:orders"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:ord:"))
async def admin_order_action(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    parts = cb.data.split(":")
    action, oid = parts[2], int(parts[3])
    order = await session.get(Order, oid)
    if not order: return

    try:
        new_status = OrderStatus(action)
        order.status = new_status
    except ValueError:
        await cb.answer("\u274c", show_alert=True)
        return

    if action in ("rejected", "refunded"):
        refund = order.total_cost - order.refunded_amount
        if refund > 0:
            r = await session.execute(select(User).where(User.tg_id == order.user_id))
            target = r.scalar_one_or_none()
            if target:
                target.wallet_balance += refund
                order.refunded_amount += refund
                tx = Transaction(user_id=target.tg_id, type=TransactionType.REFUND, amount=refund,
                                 balance_before=target.wallet_balance - refund, balance_after=target.wallet_balance,
                                 description=f"Refund for order #{oid}")
                session.add(tx)
                try:
                    await cb.bot.send_message(target.tg_id, f"\u21a9\ufe0f سفارش #{oid} رد/بازگشت شد.\nمبلغ بازگشتی: {fmt(refund)} تومان")
                except: pass

    await session.flush()
    await cb.message.edit_text(f"\u2705 وضعیت سفارش #{oid} به {action} تغییر کرد.")
    await cb.answer()


# ── Users ──
@router.callback_query(F.data == "admin:users")
async def admin_users(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    r = await session.execute(select(User).order_by(desc(User.registered_at)).limit(20))
    users = r.scalars().all()
    lines = ["\U0001f465 <b>کاربران اخیر</b>\n"]
    for u in users:
        lines.append(f"\U0001f539 <code>{u.tg_id}</code> | {u.full_name or '-'} | {fmt(u.wallet_balance)} | {u.loyalty_level.value}")
    text = "\n".join(lines)
    kb = InlineKeyboardBuilder()
    for u in users:
        kb.row(InlineKeyboardButton(text=f"\U0001f464 {u.tg_id}", callback_data=f"admin:usr:view:{u.tg_id}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:main"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:usr:view:"))
async def admin_user_view(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    tid = int(cb.data.split(":")[3])
    r = await session.execute(select(User).where(User.tg_id == tid))
    target = r.scalar_one_or_none()
    if not target: return
    text = (
        f"\U0001f464 <b>کاربر {target.tg_id}</b>\n\n"
        f"\U0001f4db نام: {target.full_name or '-'}\n"
        f"\U0001f4b0 موجودی: {fmt(target.wallet_balance)}\n"
        f"\U0001f4ca کل خرید: {fmt(target.total_spent)}\n"
        f"\u2b50 سطح: {target.loyalty_level.value}\n"
        f"\U0001f522 سفارشات: {target.total_orders}"
    )
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="\U0001f4b3 افزودن موجودی", callback_data=f"admin:usr:addbal:{tid}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:users"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:usr:addbal:"))
async def admin_add_balance_start(cb: CallbackQuery, state: FSMContext, lang: str):
    tid = int(cb.data.split(":")[3])
    await state.update_data(target_id=tid)
    await cb.message.edit_text("\U0001f4b3 مبلغ افزایش موجودی را وارد کنید:")
    await state.set_state(AdminState.add_balance)
    await cb.answer()


@router.message(AdminState.add_balance)
async def admin_add_balance_process(msg: Message, session: AsyncSession, state: FSMContext, lang: str):
    try:
        amount = int(msg.text.replace(",", ""))
        data = await state.get_data()
        tid = data.get("target_id")
        r = await session.execute(select(User).where(User.tg_id == tid))
        target = r.scalar_one_or_none()
        if not target: return
        target.wallet_balance += amount
        tx = Transaction(user_id=tid, type=TransactionType.DEPOSIT, amount=amount,
                         balance_before=target.wallet_balance - amount, balance_after=target.wallet_balance,
                         description="Admin manual deposit")
        session.add(tx)
        await session.flush()
        await msg.answer(f"\u2705 موجودی کاربر <code>{tid}</code> به میزان {fmt(amount)} افزایش یافت.", reply_markup=back_kb(lang, "admin:main").as_markup(), parse_mode="HTML")
        await state.clear()
    except:
        await msg.answer("\u26a0\ufe0f عدد معتبر وارد کنید.")


# ── Tickets ──
@router.callback_query(F.data == "admin:tickets")
async def admin_tickets(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    r = await session.execute(select(Ticket).where(Ticket.status != TicketStatus.CLOSED).order_by(desc(Ticket.updated_at)).limit(20))
    tickets = r.scalars().all()
    lines = ["\U0001f3ab <b>تیکت\u200cهای باز</b>\n"]
    for t in tickets:
        lines.append(f"\U0001f539 #{t.id} | {t.subject} | <code>{t.user_id}</code> | {t.status.value}")
    text = "\n".join(lines)
    kb = InlineKeyboardBuilder()
    for t in tickets:
        kb.row(InlineKeyboardButton(text=f"\U0001f3ab #{t.id}", callback_data=f"admin:tkt:view:{t.id}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:main"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:tkt:view:"))
async def admin_ticket_view(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    tid = int(cb.data.split(":")[3])
    ticket = await session.get(Ticket, tid)
    if not ticket: return
    r = await session.execute(select(TicketMessage).where(TicketMessage.ticket_id == tid).order_by(TicketMessage.created_at))
    msgs = r.scalars().all()
    lines = [f"\U0001f3ab <b>تیکت #{tid}: {ticket.subject}</b>\n"]
    for m in msgs:
        sender = "\U0001f451 ادمین" if m.is_admin else f"\U0001f464 {m.sender_id}"
        lines.append(f"{sender}: {m.text}")
    text = "\n".join(lines)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="\U0001f4dd پاسخ", callback_data=f"admin:tkt:reply:{tid}"))
    kb.row(InlineKeyboardButton(text="\u2705 بستن", callback_data=f"admin:tkt:close:{tid}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:tickets"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("admin:tkt:reply:"))
async def admin_ticket_reply_start(cb: CallbackQuery, state: FSMContext, lang: str):
    tid = int(cb.data.split(":")[3])
    await state.update_data(ticket_id=tid)
    await cb.message.edit_text("\U0001f4dd متن پاسخ را وارد کنید:")
    await state.set_state(AdminState.ticket_reply)
    await cb.answer()


@router.message(AdminState.ticket_reply)
async def admin_ticket_reply_process(msg: Message, session: AsyncSession, state: FSMContext, lang: str):
    data = await state.get_data()
    tid = data.get("ticket_id")
    if not tid: return
    ticket = await session.get(Ticket, tid)
    if not ticket: return
    m = TicketMessage(ticket_id=tid, sender_id=msg.from_user.id, is_admin=True, text=msg.text)
    session.add(m)
    ticket.status = TicketStatus.IN_PROGRESS
    await session.flush()
    try:
        await msg.bot.send_message(ticket.user_id, f"\U0001f3ab پاسخ ادمین به تیکت #{tid}:\n{msg.text}")
    except: pass
    await msg.answer("\u2705 پاسخ ارسال شد.", reply_markup=back_kb(lang, "admin:tickets").as_markup())
    await state.clear()


@router.callback_query(F.data.startswith("admin:tkt:close:"))
async def admin_ticket_close(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    if not is_admin(user): return
    tid = int(cb.data.split(":")[3])
    ticket = await session.get(Ticket, tid)
    if ticket:
        ticket.status = TicketStatus.CLOSED
        await session.flush()
    await cb.message.edit_text(f"\u2705 تیکت #{tid} بسته شد.")
    await cb.answer()
