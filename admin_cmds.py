# admin_cmds.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import db
import config
from lang import t
from utils import esc, staff_ids, main_kb


def _admin_only(f):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in config.ADMINS:
            return await update.message.reply_text("❌ Admin only.")
        return await f(update, context)
    wrapper.__name__ = f.__name__
    return wrapper


def _staff_only(f):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in staff_ids():
            return await update.message.reply_text("❌ Staff only.")
        return await f(update, context)
    wrapper.__name__ = f.__name__
    return wrapper


# ── Manager management ────────────────────────────────────────────────────

@_admin_only
async def cmd_addmanager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        mgrs = await db.get_managers()
        lines = [f"🔧 {m}" for m in mgrs] or ["(none)"]
        return await update.message.reply_text(
            "Managers:\n" + "\n".join(lines) + "\n\nAdd: /addmanager <user_id>"
        )
    try:
        uid = int(context.args[0])
        if uid in config.ADMINS:
            return await update.message.reply_text("❌ Cannot add admin as manager.")
        await db.add_manager(uid, update.effective_user.id)
        if uid not in config.MANAGERS:
            config.MANAGERS.append(uid)
        await update.message.reply_text(f"✅ Manager {uid} added.")
        try:
            await context.bot.send_message(uid, "✅ You have been added as Manager.")
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


@_admin_only
async def cmd_removemanager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /removemanager <user_id>")
    try:
        uid = int(context.args[0])
        if uid in config.ADMINS:
            return await update.message.reply_text("❌ Cannot remove admin.")
        removed = await db.remove_manager(uid)
        if uid in config.MANAGERS:
            config.MANAGERS.remove(uid)
        if removed:
            await update.message.reply_text(f"✅ Manager {uid} removed.")
            try:
                await context.bot.send_message(uid, "ℹ️ You have been removed as Manager.")
            except Exception:
                pass
        else:
            await update.message.reply_text(f"❌ {uid} is not a manager.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")


@_admin_only
async def cmd_listmanagers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mgrs  = await db.get_managers()
    lines = [f"👑 Admin: {a}" for a in config.ADMINS]
    lines += [f"🔧 Manager: {m}" for m in mgrs]
    await update.message.reply_text("Staff:\n" + "\n".join(lines) if lines else "No staff.")


# ── Financial settings ────────────────────────────────────────────────────

@_admin_only
async def cmd_setdeprate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        v = await db.get_setting('usdt_deposit_rate')
        return await update.message.reply_text(f"Current deposit rate: 1 USDT = {v} TK\nSet: /setdeprate <rate>")
    try:
        rate = float(context.args[0])
        await db.set_setting('usdt_deposit_rate', str(rate))
        await update.message.reply_text(f"✅ Deposit rate: 1 USDT = {rate} TK")
    except ValueError:
        await update.message.reply_text("❌ Invalid number.")


@_admin_only
async def cmd_setwitrate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        v = await db.get_setting('usdt_withdraw_rate')
        return await update.message.reply_text(f"Current withdraw rate: 1 USDT = {v} TK\nSet: /setwitrate <rate>")
    try:
        rate = float(context.args[0])
        await db.set_setting('usdt_withdraw_rate', str(rate))
        await update.message.reply_text(f"✅ Withdraw rate: 1 USDT = {rate} TK")
    except ValueError:
        await update.message.reply_text("❌ Invalid number.")


@_admin_only
async def cmd_setrules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        rules = await db.get_setting('rules_text')
        return await update.message.reply_text(f"Current rules:\n{rules or '(not set)'}\n\nSet: /setrules <text>")
    await db.set_setting('rules_text', ' '.join(context.args))
    await update.message.reply_text("✅ Rules updated.")


# ── Daily report ──────────────────────────────────────────────────────────

@_admin_only
async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = await db.get_daily_report()
    text = (
        f"📊 Daily Report — {r['date']}\n"
        f"{'='*30}\n\n"
        f"👥 Total users: {r['total_users']} (+{r['new_users']} today)\n\n"
        f"🎮 Matches: {r['matches']} | Completed: {r['completed']}\n"
        f"   Fees collected: {r['fees']:.2f} TK\n\n"
        f"💳 MFS Deposits: {r['mfs_dep_count']} × {r['mfs_dep_amount']:.2f} TK\n"
        f"💎 Exc Deposits: {r['exc_dep_count']} × {r['exc_dep_usdt']:.4f} USDT ({r['exc_dep_tk']:.2f} TK)\n\n"
        f"💸 MFS Withdrawals: {r['mfs_wit_amount']:.2f} TK\n"
        f"💸 Exc Withdrawals: {r['exc_wit_usdt']:.4f} USDT\n\n"
        f"⏳ Pending\n"
        f"   MFS dep: {r['pending_mfs_dep']} | Exc dep: {r['pending_exc_dep']}\n"
        f"   MFS wit: {r['pending_mfs_wit']} | Exc wit: {r['pending_exc_wit']}\n\n"
        f"{'='*30}\n"
        f"💱 Rates: Dep 1 USDT={r['dep_rate']} TK | Wit 1 USDT={r['wit_rate']} TK"
    )
    await update.message.reply_text(text)


# ── User management ───────────────────────────────────────────────────────

@_staff_only
async def cmd_userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /userinfo <user_id>")
    try:
        uid  = int(context.args[0])
        user = await db.get_user(uid)
        if not user:
            return await update.message.reply_text("❌ Not found.")
        text = (
            f"👤 User {uid}\n"
            f"IGN: {esc(user.get('ingame_name'))}\n"
            f"Phone: {esc(user.get('phone'))}\n"
            f"Available: {user['available_bal']:.2f} TK\n"
            f"Locked: {user['locked_bal']:.2f} TK\n"
            f"ELO: {user['elo']} | Won: {user['wins']} | Lost: {user['losses']}\n"
            f"Banned: {'Yes' if user['is_banned'] else 'No'}"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔒 Ban", callback_data=f"admin_ban_{uid}"),
        ]])
        await update.message.reply_text(text, reply_markup=kb)
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")


@_admin_only
async def cmd_banuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /banuser <user_id>")
    try:
        uid = int(context.args[0])
        await db.update_user(uid, is_banned=1)
        await update.message.reply_text(f"✅ Banned {uid}.")
        try:
            await context.bot.send_message(uid, "❌ Your account has been banned.")
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")


@_admin_only
async def cmd_unbanuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /unbanuser <user_id>")
    try:
        uid = int(context.args[0])
        await db.update_user(uid, is_banned=0)
        await update.message.reply_text(f"✅ Unbanned {uid}.")
        try:
            await context.bot.send_message(uid, "✅ Your account has been restored.")
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Invalid ID.")


@_admin_only
async def cmd_addbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("Usage: /addbalance <user_id> <amount> [note]")
    try:
        uid    = int(context.args[0])
        amount = float(context.args[1])
        note   = ' '.join(context.args[2:]) or 'admin bonus'
        user   = await db.get_user(uid)
        if not user:
            return await update.message.reply_text("❌ Not found.")
        await db.admin_adjust_balance(uid, amount, note)
        await update.message.reply_text(f"✅ Added {amount:.2f} TK to {esc(user.get('ingame_name'))}.")
        try:
            await context.bot.send_message(uid, f"✅ {amount:.2f} TK added. ({note})")
        except Exception:
            pass
    except ValueError:
        await update.message.reply_text("❌ Invalid input.")


@_admin_only
async def cmd_deductbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("Usage: /deductbalance <user_id> <amount> [note]")
    try:
        uid    = int(context.args[0])
        amount = float(context.args[1])
        note   = ' '.join(context.args[2:]) or 'admin deduct'
        user   = await db.get_user(uid)
        if not user:
            return await update.message.reply_text("❌ Not found.")
        if user['available_bal'] < amount:
            return await update.message.reply_text("❌ Insufficient balance.")
        await db.admin_adjust_balance(uid, -amount, note)
        await update.message.reply_text(f"✅ Deducted {amount:.2f} TK from {esc(user.get('ingame_name'))}.")
    except ValueError:
        await update.message.reply_text("❌ Invalid input.")


# ── Match management ──────────────────────────────────────────────────────

@_staff_only
async def cmd_pending_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending = await db.get_pending_matches()
    if not pending:
        return await update.message.reply_text("✅ No pending matches.")
    for m in pending:
        p1 = await db.get_user(m['p1_id'])
        p2 = await db.get_user(m['p2_id'])
        p1_ign = esc(p1.get('ingame_name') if p1 else '?')
        p2_ign = esc(p2.get('ingame_name') if p2 else '?')
        text = f"🎮 Match #{m['match_id']}\n{p1_ign} vs {p2_ign}\nFee: {m['fee']} TK"
        kb   = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ {p1_ign}", callback_data=f"verify_{m['match_id']}_{m['p1_id']}"),
            InlineKeyboardButton(f"✅ {p2_ign}", callback_data=f"verify_{m['match_id']}_{m['p2_id']}"),
        ]])
        await update.message.reply_text(text, reply_markup=kb)


@_staff_only
async def cmd_pending_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mfs = await db.get_pending_mfs_deposits()
    exc = await db.get_pending_exc_deposits()
    if not mfs and not exc:
        return await update.message.reply_text("✅ No pending deposits.")
    for d in mfs:
        user = await db.get_user(d['user_id'])
        info = config.MOBILE_BANKING.get(d['method'], {})
        cap  = (
            f"💳 MFS Deposit #{d['id']}\n"
            f"👤 {esc(user.get('ingame_name') if user else '?')} ({d['user_id']})\n"
            f"📱 {info.get('name', d['method'])} | TxID: {d['txid']}\n"
            f"💰 {d['amount']:.2f} TK"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ #{d['id']}", callback_data=f"mdep_approve_{d['id']}"),
            InlineKeyboardButton(f"❌ #{d['id']}", callback_data=f"mdep_reject_{d['id']}"),
        ]])
        try:
            await context.bot.send_photo(update.effective_user.id, d['screenshot'], caption=cap, reply_markup=kb)
        except Exception:
            await update.message.reply_text(cap, reply_markup=kb)
    for d in exc:
        user = await db.get_user(d['user_id'])
        info = config.EXCHANGERS.get(d['exchanger'], {})
        cap  = (
            f"💎 Exc Deposit #{d['id']}\n"
            f"👤 {esc(user.get('ingame_name') if user else '?')} ({d['user_id']})\n"
            f"🏦 {info.get('name', d['exchanger'])}\n"
            f"💵 {d['amount_usdt']:.4f} USDT = {d['amount_tk']:.2f} TK\n"
            f"📥 Our UID: {d.get('our_uid', '?')}\n"
            f"📤 Their UID: {d.get('user_uid', '?')}"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ #{d['id']}", callback_data=f"edep_approve_{d['id']}"),
            InlineKeyboardButton(f"❌ #{d['id']}", callback_data=f"edep_reject_{d['id']}"),
        ]])
        try:
            await context.bot.send_photo(update.effective_user.id, d['screenshot'], caption=cap, reply_markup=kb)
        except Exception:
            await update.message.reply_text(cap, reply_markup=kb)


@_staff_only
async def cmd_pending_withdrawals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mfs = await db.get_pending_mfs_withdrawals()
    exc = await db.get_pending_exc_withdrawals()
    if not mfs and not exc:
        return await update.message.reply_text("✅ No pending withdrawals.")
    for w in mfs:
        user = await db.get_user(w['user_id'])
        info = config.MOBILE_BANKING.get(w['method'], {})
        text = (
            f"💸 MFS Withdrawal #{w['id']}\n"
            f"👤 {esc(user.get('ingame_name') if user else '?')} ({w['user_id']})\n"
            f"📱 {info.get('name', w['method'])}: {w['account']}\n"
            f"💰 {w['amount']:.2f} TK"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ #{w['id']}", callback_data=f"mwit_approve_{w['id']}"),
            InlineKeyboardButton(f"❌ #{w['id']}", callback_data=f"mwit_reject_{w['id']}"),
        ]])
        await update.message.reply_text(text, reply_markup=kb)
    for w in exc:
        user = await db.get_user(w['user_id'])
        info = config.EXCHANGERS.get(w['exchanger'], {})
        our_uid = info.get('our_uid', '?')
        text = (
            f"💸 Exc Withdrawal #{w['id']}\n"
            f"👤 {esc(user.get('ingame_name') if user else '?')} ({w['user_id']})\n"
            f"🏦 {info.get('name', w['exchanger'])}\n"
            f"💵 {w['amount_usdt']:.4f} USDT = {w['amount_tk']:.2f} TK\n"
            f"📤 Their UID: {w['user_uid']}\n"
            f"📥 Our UID: {our_uid}"
        )
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(f"✅ #{w['id']}", callback_data=f"ewit_approve_{w['id']}"),
            InlineKeyboardButton(f"❌ #{w['id']}", callback_data=f"ewit_reject_{w['id']}"),
        ]])
        await update.message.reply_text(text, reply_markup=kb)


# ── Broadcast ─────────────────────────────────────────────────────────────

@_admin_only
async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /broadcast <message>")
    import aiosqlite
    msg  = ' '.join(context.args)
    ok   = 0
    fail = 0
    async with aiosqlite.connect(db.DB) as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.execute("SELECT user_id FROM users WHERE is_registered=1") as cur:
            users = await cur.fetchall()
    import asyncio
    for row in users:
        try:
            await context.bot.send_message(row['user_id'], f"📢 {msg}")
            ok += 1
        except Exception:
            fail += 1
        if (ok + fail) % 25 == 0:
            await asyncio.sleep(1)
    await update.message.reply_text(f"✅ Broadcast done. OK: {ok} | Failed: {fail}")


@_admin_only
async def cmd_message_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        return await update.message.reply_text("Usage: /message_user <user_id> <text>")
    try:
        uid  = int(context.args[0])
        text = ' '.join(context.args[1:])
        await context.bot.send_message(uid, f"📬 Message from admin:\n\n{text}")
        await update.message.reply_text("✅ Sent.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ── Tournament management ─────────────────────────────────────────────────

@_admin_only
async def cmd_create_tourney(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = ' '.join(context.args)
    if '|' not in text:
        return await update.message.reply_text(
            "Usage: /create_tourney <name> | <slots> | <fee> | <prize>\n"
            "e.g.: /create_tourney Friday Cup | 16 | 50 | 500"
        )
    parts = [p.strip() for p in text.split('|')]
    if len(parts) != 4:
        return await update.message.reply_text("❌ Need 4 parts separated by |")
    try:
        name, slots, fee, prize = parts[0], int(parts[1]), float(parts[2]), float(parts[3])
        tid = await db.create_tournament(name, slots, fee, prize)
        await update.message.reply_text(
            f"✅ Tournament #{tid} created!\n{name}\n{slots} slots | {fee} TK fee | {prize} TK prize"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


@_admin_only
async def cmd_generate_round(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /generate_round <tourney_id>")
    import random
    try:
        tid     = int(context.args[0])
        tourney = await db.get_tournament(tid)
        if not tourney:
            return await update.message.reply_text("❌ Tournament not found.")
        players = await db.get_tourney_players(tid, 'ACTIVE')
        if len(players) < 2:
            return await update.message.reply_text("❌ Not enough players.")
        if tourney['status'] == 'OPEN':
            await db.update_tournament_status(tid, 'RUNNING')
        random.shuffle(players)
        count = 0
        for i in range(0, len(players) - 1, 2):
            p1, p2 = players[i]['user_id'], players[i+1]['user_id']
            mid = await db.create_match(p1, p2, 0, tourney_id=tid)
            u1 = await db.get_user(p1)
            u2 = await db.get_user(p2)
            l1 = await db.get_user_lang(p1)
            l2 = await db.get_user_lang(p2)
            try:
                await context.bot.send_message(
                    p1,
                    f"⚔️ Tournament match!\nvs {esc(u2.get('ingame_name') if u2 else '?')}\n\nCreate a room and send the 8-digit code here.",
                    reply_markup=__import__('utils').cancel_kb(l1)
                )
                await db.set_state(p1, 'awaiting_room_code', mid)
                await context.bot.send_message(
                    p2,
                    f"⚔️ Tournament match!\nvs {esc(u1.get('ingame_name') if u1 else '?')}\n\nWaiting for room code...",
                )
            except Exception:
                pass
            count += 1
        if len(players) % 2 != 0:
            bye = players[-1]['user_id']
            blang = await db.get_user_lang(bye)
            try:
                await context.bot.send_message(bye, "🍀 BYE — you advance to the next round!")
            except Exception:
                pass
        await update.message.reply_text(f"✅ Round generated! {count} match(es) created.")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


# ── Background jobs ───────────────────────────────────────────────────────

async def job_daily_backup(context):
    """Daily SQLite backup using native backup API."""
    from datetime import datetime
    dest = f"backup_{datetime.now().strftime('%Y-%m-%d')}.db"
    try:
        await db.safe_backup(dest)
        # Remove backups older than 7 days
        import os, glob
        from datetime import timedelta
        for path in glob.glob("backup_*.db"):
            try:
                date_str = path[7:17]
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                if (datetime.now() - file_date).days > 7:
                    os.remove(path)
            except Exception:
                pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Backup failed: {e}")


@_admin_only
async def cmd_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ ডাটাবেজ ব্যাকআপ তৈরি হচ্ছে, দয়া করে অপেক্ষা করুন...")
    from datetime import datetime
    dest = f"manual_backup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    try:
        await db.safe_backup(dest)
        import os
        with open(dest, 'rb') as doc:
            await context.bot.send_document(
                chat_id=update.effective_user.id,
                document=doc,
                filename=dest,
                caption="✅ আপনার ডাটাবেজ ব্যাকআপ সফলভাবে সম্পন্ন হয়েছে!"
            )
        os.remove(dest)  # সেন্ড করার পর সার্ভার থেকে মুছে ফেলবে যাতে স্টোরেজ না ভরে
    except Exception as e:
        await update.message.reply_text(f"❌ ব্যাকআপ নিতে সমস্যা হয়েছে: {e}")


@_admin_only
async def cmd_settutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.video:
        return await update.message.reply_text("❌ আপনাকে প্রথমে বটকে একটি ভিডিও পাঠাতে হবে, তারপর সেই ভিডিওতে রিপ্লাই করে /settutorial লিখতে হবে।")
    
    file_id = update.message.reply_to_message.video.file_id
    await db.set_setting('tutorial_video_id', file_id)
    await update.message.reply_text("✅ চমৎকার! টিউটোরিয়াল ভিডিও সফলভাবে ডাটাবেজে সেভ হয়েছে। এখন ইউজাররা 'How to Play' তে ক্লিক করলেই এই ভিডিওটি দেখতে পাবে।")
