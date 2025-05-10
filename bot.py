from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random
import datetime

TOKEN = "7698778415:AAE8lSqSdQhX95I5aLtGCAai-pnRH24AU0s"

# Tymczasowa pamięć użytkowników
user_dna = {}
user_upgrades = {}
user_pets = {}
user_eggs = {}
user_amber = {}
user_last_claim = {}  # Daily reward tracking

# Definicje ulepszeń
upgrades = [
    {"name": "Małe Pazurki", "cost": 10, "bonus": 1},
    {"name": "Szybki Ogon", "cost": 50, "bonus": 2},
    {"name": "Twarda Łuska", "cost": 150, "bonus": 3},
    {"name": "Silne Skrzydła", "cost": 500, "bonus": 5},
    {"name": "Zęby Tyranozaura", "cost": 1200, "bonus": 8}
]

# Jajka premium
premium_eggs = [
    {"name": "Kryształowe Jajo", "cost": 3, "pet": "🐉 Kryształowy Dino", "rarity": "[Legendarny]"},
    {"name": "Złote Jajo", "cost": 2, "pet": "🦕 Złoty Raptor", "rarity": "[Epicki]"}
]

# Jajka zwykłe
basic_eggs = [
    {"name": "Zwykłe Jajo", "cost": 50, "pet": "🐢 Mały Dino", "rarity": "[Powszechny]", "desc": "Twój pierwszy przyjaciel!"},
    {"name": "Zielone Jajo", "cost": 150, "pet": "🦅 Raptorek", "rarity": "[Rzadki]", "desc": "Szybki i zwinny!"},
    {"name": "Nocne Jajo", "cost": 400, "pet": "🐲 Czarny Raptor", "rarity": "[Epicki]", "desc": "Cichy łowca nocy."}
]

# Komenda start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_dna:
        user_dna[user_id] = 1
        user_upgrades[user_id] = 0
        user_pets[user_id] = []
        user_eggs[user_id] = 0
        user_amber[user_id] = 0
        user_last_claim[user_id] = None

    await update.message.reply_text(
        f"🦕 — Witaj {update.effective_user.first_name} w DinoTapper! — 🦕\nZbieraj DNA, ulepszaj się i zbieraj rzadkie jajka!",
        reply_markup=main_menu()
    )

# Przyciski główne
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🦖 Kliknij!", callback_data="click")],
        [InlineKeyboardButton("🧬 Ulepszenia", callback_data="upgrade_menu"),
         InlineKeyboardButton("🎁 Codzienna Nagroda", callback_data="daily_reward")],
        [InlineKeyboardButton("🥚 Jajka", callback_data="eggs_category")],
        [InlineKeyboardButton("📊 Panel Użytkownika", callback_data="user_panel")]
    ])

# Obsługa przycisków
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    # Inicjalizacja użytkownika jeśli trzeba
    if user_id not in user_dna:
        user_dna[user_id] = 1
        user_upgrades[user_id] = 0
        user_pets[user_id] = []
        user_eggs[user_id] = 0
        user_amber[user_id] = 0
        user_last_claim[user_id] = None

    if data == "click":
        bonus = upgrades[user_upgrades[user_id]]['bonus'] if user_upgrades[user_id] < len(upgrades) else 0
        user_dna[user_id] += 1 + bonus

        click_effects = ["*CHOMP!*", "*Trzask pazurów!*", "*Ryk dinozaura!*"]
        effect = random.choice(click_effects)
        amber_msg = ""
        if random.random() < 0.01:
            user_amber[user_id] += 1
            amber_msg = "\n🎉 Znalazłeś bursztyn!"

        await query.answer()
        await query.edit_message_text(
            text=(f"{effect} 🦖 +{1 + bonus} DNA\n\n"
                  f"🧬 DNA: {user_dna[user_id]}\n💎 Bursztyny: {user_amber[user_id]}{amber_msg}"),
            reply_markup=main_menu(),
            parse_mode='Markdown'
        )

    elif data == "upgrade_menu":
        current_upgrade = user_upgrades[user_id]
        if current_upgrade >= len(upgrades):
            await query.answer("Wszystkie ulepszenia kupione!", show_alert=True)
            return

        u = upgrades[current_upgrade]
        text = (f"╔══════ 🔧 Ulepszenia ══════╗\n"
                f"🔹 Nazwa: {u['name']}\n"
                f"💰 Koszt: {u['cost']} DNA\n"
                f"📈 Bonus: +{u['bonus']} DNA\n"
                f"╚══════════════════════════╝")
        keyboard = [
            [InlineKeyboardButton("Kup Ulepszenie", callback_data="buy_upgrade")],
            [InlineKeyboardButton("⬅️ Powrót", callback_data="click")]
        ]
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "buy_upgrade":
        current_upgrade = user_upgrades[user_id]
        if current_upgrade >= len(upgrades):
            await query.answer("Nie ma więcej ulepszeń!", show_alert=True)
            return

        u = upgrades[current_upgrade]
        if user_dna[user_id] >= u['cost']:
            user_dna[user_id] -= u['cost']
            user_upgrades[user_id] += 1
            await query.answer("Kupiono ulepszenie!")
        else:
            await query.answer("Za mało DNA!", show_alert=True)
            return

        await query.edit_message_text(
            text=f"✅ Ulepszenie kupione!\n🧬 DNA: {user_dna[user_id]}\n💎 Bursztyny: {user_amber[user_id]}",
            reply_markup=main_menu()
        )

    elif data == "eggs_category":
        keyboard = [
            [InlineKeyboardButton("🔸 Zwykłe", callback_data="eggs_menu"),
             InlineKeyboardButton("🔹 Premium", callback_data="premium_shop")],
            [InlineKeyboardButton("⬅️ Powrót", callback_data="click")]
        ]
        await query.edit_message_text(
            text=("🥚╔═══════ KATEGORIE JAJEK ═══════╗🥚\n\n"
                  "🔸 Zwykłe Jajka — klasyczne dinozaury\n"
                  "🔹 Premium Jajka — rzadkie, silne stworzenia\n\n"
                  "╚════════════════════════════════╝"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "premium_shop":
        text = "💎 Sklep Premium:\n"
        keyboard = []
        for idx, egg in enumerate(premium_eggs):
            text += f"\n🥚 {egg['name']} — {egg['pet']} {egg['rarity']} ({egg['cost']} bursztynów)"
            keyboard.append([InlineKeyboardButton(f"Kup: {egg['name']}", callback_data=f"buy_premium_egg_{idx}")])
        keyboard.append([InlineKeyboardButton("⬅️ Powrót", callback_data="eggs_category")])
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("buy_premium_egg_"):
        idx = int(data.split("_")[-1])
        egg = premium_eggs[idx]
        if user_amber[user_id] >= egg['cost']:
            user_amber[user_id] -= egg['cost']
            user_pets[user_id].append(f"{egg['pet']} {egg['rarity']}")
            await query.answer("Zdobyto rzadkiego peta!")
        else:
            await query.answer("Za mało bursztynów!", show_alert=True)
        await query.edit_message_text(
            text=f"🧬 DNA: {user_dna[user_id]}\n💎 Bursztyny: {user_amber[user_id]}",
            reply_markup=main_menu()
        )

    elif data == "eggs_menu":
        keyboard = []
        for idx, egg in enumerate(basic_eggs):
            keyboard.append([InlineKeyboardButton(f"{egg['name']} ({egg['cost']} DNA)", callback_data=f"buy_basic_egg_{idx}")])
        keyboard.append([InlineKeyboardButton("⬅️ Powrót", callback_data="eggs_category")])
        await query.edit_message_text("🥚 Kup jajko za DNA:\n\nWybierz jedno z dostępnych:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("buy_basic_egg_"):
        idx = int(data.split("_")[-1])
        egg = basic_eggs[idx]
        if user_dna[user_id] >= egg['cost']:
            user_dna[user_id] -= egg['cost']
            user_pets[user_id].append(f"{egg['pet']} {egg['rarity']} — {egg['desc']}")
            await query.answer("Zdobyto nowego peta!")
            reveal_text = f"*Jajo się trzęsie...*\n💥 *Pękło!*\n🎉 Otrzymano: {egg['pet']} {egg['rarity']}"
        else:
            await query.answer("Za mało DNA!", show_alert=True)
            reveal_text = f"Nie udało się kupić jajka."

        await query.edit_message_text(
            text=f"{reveal_text}\n\n🧬 DNA: {user_dna[user_id]}\n💎 Bursztyny: {user_amber[user_id]}",
            reply_markup=main_menu(),
            parse_mode='Markdown'
        )

    elif data == "daily_reward":
        now = datetime.datetime.now()
        last_claim = user_last_claim[user_id]
        if last_claim is None or (now - last_claim).days >= 1:
            user_dna[user_id] += 100
            user_amber[user_id] += 1
            user_last_claim[user_id] = now
            await query.answer("🎁 Otrzymano codzienną nagrodę!")
        else:
            await query.answer("Nagroda już odebrana dzisiaj!", show_alert=True)
        await query.edit_message_text(
            text=f"🎉 DNA: {user_dna[user_id]}\n💎 Bursztyny: {user_amber[user_id]}",
            reply_markup=main_menu()
        )

    elif data == "user_panel":
        pet_list = "\n".join(user_pets[user_id]) if user_pets[user_id] else "Brak zwierzaków."
        text = (
            f"╔════ 📊 Panel Użytkownika ════╗\n"
            f"🧬 DNA: {user_dna[user_id]}\n"
            f"💎 Bursztyny: {user_amber[user_id]}\n"
            f"🔧 Ulepszenie: {user_upgrades[user_id]} / {len(upgrades)}\n"
            f"🐾 Pety:\n{pet_list}\n"
            f"╚══════════════════════════════╝"
        )
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Powrót", callback_data="click")]
        ]))

# Główna funkcja

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.run_polling()

if __name__ == "__main__":
    main()
