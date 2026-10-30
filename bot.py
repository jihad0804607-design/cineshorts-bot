import os
import telebot
from telebot import types
import yt_dlp
from moviepy.editor import VideoFileClip

TOKEN = "9285770739:AAGFgVqtPbF9I2fN2_UlqMCoOEFY0zCBx8g"
ADMIN_USER_ID = 1355104093

ALLOWED_USER_IDS = [
    ADMIN_USER_ID,  
]

bot = telebot.TeleBot(TOKEN)

user_notes = {}
user_todos = {}

def is_allowed(user_id):
    return user_id in ALLOWED_USER_IDS

def is_admin(user_id):
    return user_id == ADMIN_USER_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if not is_allowed(user_id):
        bot.reply_to(
            message, 
            "⚠️ **দুঃখিত! এই বটটি ব্যবহারের অনুমতি আপনার নেই।**\n\nএটি একটি প্রাইভেট বট। বটের মালিকের কাছ থেকে অ্যাক্সেস বা পারমিশন নিয়ে নিন। আপনার ইউজার আইডিটি হলো: `" + str(user_id) + "`", 
            parse_mode="Markdown"
        )
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🎬 মুভি/নাটক থেকে রিলস (Shorts)"),
        types.KeyboardButton("📥 মিডিয়া ডাউনলোডার"),
        types.KeyboardButton("🎵 ভিডিও থেকে MP3"),
        types.KeyboardButton("🖼️ থাম্বনেইল ডাউনলোড"),
        types.KeyboardButton("📝 আমার নোটস"),
        types.KeyboardButton("📌 টু-ডু লিস্ট")
    )
    
    if is_admin(user_id):
        markup.add(types.KeyboardButton("⚙️ অ্যাডমিন প্যানেল"))

    bot.reply_to(
        message, 
        "স্বাগতম বস! 🚀 আপনার রিলস মেকার বট পুরোপুরি প্রস্তুত। নিচে থেকে অপশন সিলেক্ট করুন:", 
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    if not is_allowed(user_id):
        return  

    text = message.text

    if text.startswith("/adduser "):
        if not is_admin(user_id):
            bot.reply_to(message, "এই কমান্ডটি শুধুমাত্র বটের মালিকের জন্য!")
            return
        try:
            new_user_id = int(text.replace("/adduser ", "").strip())
            if new_user_id not in ALLOWED_USER_IDS:
                ALLOWED_USER_IDS.append(new_user_id)
                bot.reply_to(message, f"✅ সফলভাবে ইউজার আইডি `{new_user_id}` কে বটের অ্যাক্সেস দেওয়া হয়েছে!", parse_mode="Markdown")
            else:
                bot.reply_to(message, "⚠️ এই ইউজার আইডিটি ইতিমধ্যে অনুমোদিত লিস্টে রয়েছে!")
        except ValueError:
            bot.reply_to(message, "❌ ভুল ফরম্যাট! সঠিকভাবে এভাবে লিখুন: `/adduser 123456789`", parse_mode="Markdown")
        return

    elif text.startswith("/removeuser "):
        if not is_admin(user_id):
            bot.reply_to(message, "এই কমান্ডটি শুধুমাত্র বটের মালিকের জন্য!")
            return
        try:
            rem_user_id = int(text.replace("/removeuser ", "").strip())
            if rem_user_id == ADMIN_USER_ID:
                bot.reply_to(message, "⚠️ মালিকের আইডি লিস্ট থেকে রিমুভ করা যাবে না!")
                return
            if rem_user_id in ALLOWED_USER_IDS:
                ALLOWED_USER_IDS.remove(rem_user_id)
                bot.reply_to(message, f"🗑️ ইউজার আইডি `{rem_user_id}` এর অ্যাক্সেস বাতিল করা হয়েছে!", parse_mode="Markdown")
            else:
                bot.reply_to(message, "⚠️ এই আইডিটি অনুমোদিত লিস্টে পাওয়া যায়নি।")
        except ValueError:
            bot.reply_to(message, "❌ ভুল ফরম্যাট! এভাবে লিখুন: `/removeuser 123456789`", parse_mode="Markdown")
        return

    if "youtube.com" in text or "youtu.be" in text:
        msg = bot.reply_to(message, "⏳ আপনার লিংকটি প্রসেস করা হচ্ছে...\n\n🔄 ভিডিও ডাউনলোড ও রিলস ফরম্যাটে রূপান্তর করা হচ্ছে, একটু অপেক্ষা করুন...")
        
        try:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': 'downloaded_video.mp4',
                'noplaylist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([text])

            clip = VideoFileClip("downloaded_video.mp4")
            duration = min(30, clip.duration) 
            short_clip = clip.subclip(0, duration)
            
            w, h = short_clip.size
            target_width = int(h * (9 / 16))
            if w > target_width:
                x_center = w / 2
                short_clip = short_clip.crop(x1=x_center - target_width/2, y1=0, x2=x_center + target_width/2, y2=h)

            output_filename = "final_reel.mp4"
            short_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")

            clip.close()
            short_clip.close()

            caption_text = (
                "✨ **আপনার রিলস সফলভাবে তৈরি হয়েছে!**\n\n"
                "🎵 **স্ট্যাটাস:** পারফেক্ট 9:16 রিলস ফরম্যাটে তৈরি।\n"
                "🏷️ #BanglaNatok #CineShorts #TrendingReels #ShortsBD"
            )

            with open(output_filename, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption=caption_text, parse_mode="Markdown")

            if os.path.exists("downloaded_video.mp4"):
                os.remove("downloaded_video.mp4")
            if os.path.exists(output_filename):
                os.remove(output_filename)

            bot.delete_message(message.chat.id, msg.message_id)

        except Exception as e:
            bot.edit_message_text(f"❌ ভিডিও প্রসেস করতে সমস্যা হয়েছে: {str(e)}", message.chat.id, msg.message_id)

    elif text == "⚙️ অ্যাডমিন প্যানেল" or text == "👥 ইউজার ম্যানেজমেন্ট":
        if not is_admin(user_id):
            bot.reply_to(message, "এই অপশনটি শুধুমাত্র বটের মালিকের জন্য!")
            return
        
        user_list_str = "\n".join([f"🔹 আইডি: `{uid}`" for uid in ALLOWED_USER_IDS])
        admin_text = (
            "🛠️ **বট অ্যাডমিন কন্ট্রোল প্যানেল**\n\n"
            f"👤 **মালিকের আইডি:** `{ADMIN_USER_ID}`\n"
            f"👥 **মোট অনুমোদিত ইউজার:** {len(ALLOWED_USER_IDS)} জন\n\n"
            f"📋 **অনুমোদিত ইউজারদের তালিকা:**\n{user_list_str}\n\n"
            "➕ **নতুন ইউজার যোগ করতে লিখুন:**\n`/adduser ইউজারের_আইডি`\n\n"
            "➖ **ইউজার বাদ দিতে লিখুন:**\n`/removeuser ইউজারের_আইডি`"
        )
        bot.reply_to(message, admin_text, parse_mode="Markdown")

    elif text.startswith("/note "):
        note = text.replace("/note ", "")
        if user_id not in user_notes:
            user_notes[user_id] = []
        user_notes[user_id].append(note)
        bot.reply_to(message, f"📝 আপনার নোটে সেভ করা হয়েছে:\n\n🔹 {note}")

    elif text == "📝 আমার নোটস":
        notes = user_notes.get(user_id, [])
        if not notes:
            bot.reply_to(message, "আপনার কোনো নোট সেভ করা নেই। নোট সেভ করতে `/note আপনার লেখা` লিখে পাঠান।")
        else:
            notes_text = "📋 **আপনার সেভ করা নোটসমূহ:**\n\n" + "\n".join([f"{i+1}. {n}" for i, n in enumerate(notes)])
            bot.reply_to(message, notes_text, parse_mode="Markdown")

    elif text.startswith("/todo "):
        task = text.replace("/todo ", "")
        if user_id not in user_todos:
            user_todos[user_id] = []
        user_todos[user_id].append(task)
        bot.reply_to(message, f"📌 টু-ডু লিস্টে যোগ হয়েছে: {task}")

    elif text == "📌 টু-ডু লিস্ট":
        todos = user_todos.get(user_id, [])
        if not todos:
            bot.reply_to(message, "আপনার কোনো টু-ডু লিস্ট নেই। যোগ করতে `/todo আপনার কাজ` লিখে পাঠান।")
        else:
            todos_text = "📌 **আপনার কাজের তালিকা:**\n\n" + "\n".join([f"☑️ {t}" for t in todos])
            bot.reply_to(message, todos_text, parse_mode="Markdown")

    elif text == "🎬 মুভি/নাটক থেকে রিলস (Shorts)":
        bot.reply_to(message, "দয়া করে যে মুভি বা নাটকের রিলস বানাতে চান, সেটির **ইউটিউব লিংকটি** চ্যাটে পাঠিয়ে দিন।")
    elif text == "📥 মিডিয়া ডাউনলোডার":
        bot.reply_to(message, "ফেসবুক বা ইনস্টাগ্রামের ভিডিও লিংক দিন, আমি ডাউনলোড করে দিচ্ছি।")
    elif text == "🎵 ভিডিও থেকে MP3":
        bot.reply_to(message, "যেকোনো ইউটিউব লিংক পাঠান, আমি সেটি থেকে শুধু অডিও (MP3) আলাদা করে দেব।")
    elif text == "🖼️ থাম্বনেইল ডাউনলোড":
        bot.reply_to(message, "ইউটিউব ভিডিওর লিংক দিন, আমি হাই-কোয়ালিটি থাম্বনেইল ছবি পাঠিয়ে দেব।")
    else:
        bot.reply_to(message, "বুঝে উঠতে পারিনি! মেনু থেকে বাটন সিলেক্ট করুন অথবা সঠিক লিংক পাঠান।")

bot.infinity_polling()
