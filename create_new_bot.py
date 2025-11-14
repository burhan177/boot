#!/usr/bin/env python3
# سكريبت لإنشاء بوت جديد تلقائياً

import requests
import random
import string

def generate_bot_username():
    """توليد اسم مستخدم عشوائي للبوت"""
    prefixes = [
        "security_check",
        "photo_verify", 
        "identity_bot",
        "verification",
        "secure_photo",
        "check_system",
        "safety_bot"
    ]
    
    suffix = ''.join(random.choices(string.digits, k=4))
    prefix = random.choice(prefixes)
    
    return f"{prefix}_{suffix}_bot"

def suggest_bot_names():
    """اقتراح أسماء للبوت"""
    suggestions = []
    
    for i in range(5):
        username = generate_bot_username()
        suggestions.append(username)
    
    return suggestions

if __name__ == "__main__":
    print("🤖 اقتراحات أسماء للبوت الجديد:")
    print("=" * 50)
    
    suggestions = suggest_bot_names()
    
    for i, name in enumerate(suggestions, 1):
        print(f"{i}. @{name}")
    
    print("=" * 50)
    print("📋 خطوات إنشاء البوت:")
    print("1️⃣ اذهب إلى @BotFather")
    print("2️⃣ أرسل: /newbot")
    print("3️⃣ اختر اسم للبوت: Security Check Bot")
    print("4️⃣ اختر أحد الأسماء المقترحة أعلاه")
    print("5️⃣ انسخ التوكن الجديد")
    print("6️⃣ حدّث ملف boot.py بالتوكن الجديد")
