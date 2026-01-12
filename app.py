import os
import zipfile
from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# معلومات الحساب
api_id = 21100923
api_hash = "32ad1f2eb62a60301e7bbcdf91c43641"
bot_token = "8588458864:AAECfjlakVPDlhjAWIy-Tn5ClsMAez_3HYU"

app = Client("unzip_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def get_file_size(size_in_bytes):
    """تحويل الحجم من بايت إلى ميجابايت بشكل مقروء"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "أهلاً بك! أرسل ملف Zip وسأقوم بتحليله وفكه لك بالتفصيل 📁⚡",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Dev", url="https://t.me/xx28z")]])
    )

@app.on_message(filters.document)
async def analyze_and_unzip(client, message):
    if message.document.file_name.lower().endswith(".zip"):
        initial_msg = await message.reply_text("🔎 جاري فحص الملف...")
        
        try:
            # تحميل الملف للذاكرة للبدء بالتحليل
            file_data = await client.download_media(message, in_memory=True)
            zip_buffer = BytesIO(file_data.getbuffer())

            with zipfile.ZipFile(zip_buffer) as zip_ref:
                all_files = zip_ref.infolist()
                total_files = len([f for f in all_files if not f.is_dir()])
                
                # تحليل أنواع الملفات
                extensions = {}
                for f in all_files:
                    if not f.is_dir():
                        ext = os.path.splitext(f.filename)[1].lower() or "بلا امتداد"
                        extensions[ext] = extensions.get(ext, 0) + 1
                
                ext_details = "\n".join([f"- نوع `{ext}`: عدد ({count})" for ext, count in extensions.items()])
                
                # تقرير البداية
                report = (
                    f"📦 **تفاصيل الملف المضغوط:**\n"
                    f"• الاسم: `{message.document.file_name}`\n"
                    f"• الحجم الكلي: `{get_file_size(message.document.file_size)}`\n"
                    f"• عدد الملفات داخله: `{total_files}`\n\n"
                    f"📂 **محتويات الملف:**\n{ext_details}\n\n"
                    f"⏳ جاري فك الضغط والإرسال..."
                )
                await initial_msg.edit_text(report)

                # البدء بفك الضغط وإرسال ملف ملف
                count = 0
                for file_info in all_files:
                    if file_info.is_dir():
                        continue
                    
                    count += 1
                    with zip_ref.open(file_info.filename) as extracted_file:
                        to_send = BytesIO(extracted_file.read())
                        to_send.name = os.path.basename(file_info.filename)
                        
                        caption = (
                            f"📄 **ملف رقم:** {count} من {total_files}\n"
                            f"• الاسم: `{to_send.name}`\n"
                            f"• الحجم: `{get_file_size(file_info.file_size)}`"
                        )
                        
                        await client.send_document(message.chat.id, document=to_send, caption=caption)
                
                await message.reply_text(f"✅ تم الانتهاء من فك جميع الملفات ({total_files})")
                await initial_msg.delete()

        except Exception as e:
            await initial_msg.edit_text(f"❌ حدث خطأ: {e}")
    else:
        await message.reply_text("يرجى إرسال ملف بصيغة .zip فقط.")

print("بوت فك الضغط المتطور يعمل الآن... ✅")
app.run()
