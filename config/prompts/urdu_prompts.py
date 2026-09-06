"""Urdu/Roman Urdu translations for Kisan Dost."""

URDU_PROMPTS = {
    "greeting": "السلام علیکم! میں کسان دوست ہوں۔ آج میں آپ کی کسانوں کی مدد کیسے کر سکتا ہوں؟",
    "greeting_roman": "Assalam-o-Alaikum! Main Kisan Dost hoon. Aaj main aap ki kisanon ki madad kaise kar sakta hoon?",
    
    "ask_district": "آپ کا ضلع کون سا ہے؟ (مثال: ملتان، فيصل آباد، لاہور)",
    "ask_district_roman": "Aap ka zila kaun sa hai? (Misaal: Multan, Faisalabad, Lahore)",
    
    "ask_land_size": "آپ کے پاس کتنے ایکڑ زمین ہے؟",
    "ask_land_size_roman": "Aap ke paas kitne acres zameen hai?",
    
    "ask_soil_type": "مٹی کی نوعیت کیا ہے؟ (چکنی، دو मत، ریتیلی، Mitti ka type: clay, loam, sandy)",
    "ask_soil_type_roman": "Mitti ki noiayat kya hai? (Chikni, do-mat, retili)",
    
    "ask_season": "موسم کون سا ہے؟ (ربی / خریف / زاید)",
    "ask_season_roman": "Mausam kaun sa hai? (Rabi / Kharif / Zaid)",
    
    "ask_water": "پانی کی دستیابی؟ (بارانی / محدود آبپاشی / پوری آبپاشی / نہر / ٹیوب ویل)",
    "ask_water_roman": "Pani ki dostiyabi? (Barani / mehdood abpashi / poori abpashi / nehar / tubewell)",
    
    "ask_crop": "کौن سی فصل لگی ہوئی ہے؟",
    "ask_crop_roman": "Kaun si fasal lagi hui hai?",
    
    "ask_symptoms": "پودوں میں کیا علامات نظر آ رہی ہیں؟ تفصیل سے بتائیں۔",
    "ask_symptoms_roman": "Podon mein kya alamat nazar aa rahi hain? Tafseel se bataein.",
    
    "crop_recommendation": "آپ کیCONDITIONS کے لئے بہترین فصلیں:",
    "crop_recommendation_roman": "Aap ki conditions ke liye behtareen faslein:",
    
    "primary_crop": "بنیادی تجویز: {crop} - متوقع پیداوار {yield} کلوگرام فی ایکڑ، منافعہ تقریبا {profit} روپے فی ایکڑ",
    "primary_crop_roman": "Bunyadi tajweez: {crop} - Mutawaqqa pedawar {yield} kg per acre, munaafa taqreeban {profit} rupay per acre",
    
    "fertilizer_plan": "کھاد کا پلان: یوریا {urea} بوڑے، ڈی اے پی {dap} بوڑے، کل خرچہ {cost} روپے",
    "fertilizer_plan_roman": "Khad ka plan: Urea {urea} boray, DAP {dap} boray, kul kharcha {cost} rupay",
    
    "pest_diagnosis": "تشخیص: {pest} ({confidence}% یقین) - شدت: {severity}",
    "pest_diagnosis_roman": "Tashkhees: {pest} ({confidence}% yaqeen) - Shiddat: {severity}",
    
    "treatment_plan": "علاج: {pesticide} - ڈوز: {dosage} مل فی ایکڑ - طریقہ: {method} - وقت: {timing}",
    "treatment_plan_roman": "Ilaaj: {pesticide} - Dose: {dosage} ml per acre - Tareeqa: {method} - Waqt: {timing}",
    
    "safety_warning": "⚠️ احتیاط: کٹائی سے {phi} دن پہلے स्पری نہ کریں۔ داخلہ سے پہلے {rei} گھنٹے انتظار کریں۔ ماسک، دستانے، چشمیہ لازمی ہیں۔",
    "safety_warning_roman": "⚠️ Ehtiyat: Katai se {phi} din pehle spray na karein. Dakhla se pehle {rei} ghante intezar karein. Mask, dastaney, chashmiyah lazmi hain.",
    
    "mandi_prices": "قریب کی منڈیوں میں آج کے ریٹس:",
    "mandi_prices_roman": "Qareeb ki mandiyon mein aaj ke rates:",
    
    "profit_estimate": "موسم کا بالانس: خرچہ {cost} روپے، آمدنی {revenue} روپے، منافعہ {profit} روپے ({margin}%)، بریک ایون {breakeven} کلوگرام فی ایکڑ",
    "profit_estimate_roman": "Mausam ka balance: Kharcha {cost} rupay, aamdani {revenue} rupay, munaafa {profit} rupay ({margin}%), Break-even {breakeven} kg per acre",
    
    "govt_scheme": "سرکاری سکیم: {name} - قابلیت: {eligible} - اقدام: {next_step}",
    "govt_scheme_roman": "Sarkari scheme: {name} - Qabiliyat: {eligible} - Iqdam: {next_step}",
    
    "irrigation_advice": "آبیاری: {action} - وجوہ: {reason} - تاریخ: {date} - مقدار: {amount} مم",
    "irrigation_advice_roman": "Abpashi: {action} - Wajah: {reason} - Tareekh: {date} - Miqdar: {amount} mm",
    
    "weather_alert": "موسمی انتباہ: {alert}",
    "weather_alert_roman": "Mausami intibaah: {alert}",
    
    "error_generic": "معذرت، کچھ خرابی ہو گئی۔ براہ کرم دوبارہ کوشش کریں۔",
    "error_generic_roman": "Maazrat, kuch kharabi ho gayi. Barah karam dobara koshish karein.",
    
    "off_topic": "میں صرف زرعی مشورے دے سکتا ہوں۔ براہ کرم اپنی کھیتی سے متعلق سوال پوچیں۔",
    "off_topic_roman": "Main sirf zara'i mashware de sakta hoon. Barah karam apni kheti se mutaliq sawal poochein.",
    
    "unsafe_pesticide": "یہ دوائی محظور ہے یا غیر محفوظ ہے۔ میں اس کی تجویز نہیں دے سکتا۔",
    "unsafe_pesticide_roman": "Ye dawa mehzoor hai ya ghair mehfooz hai. Main is ki tajweez nahi de sakta.",
    
    "goodbye": "اللہ حافظ! خوشہال کھیتی کی دعا کرتا ہوں۔",
    "goodbye_roman": "Allah Hafiz! Khushhal kheti ki dua karta hoon.",
    
    "help": "دستیاب کمانڈز: /help /lang /reset /profile /history",
    "help_roman": "Dastiyab commands: /help /lang /reset /profile /history",
}

# Crop names in Urdu
CROP_URDU_NAMES = {
    "wheat": "گندم",
    "cotton": "کپاس",
    "rice": "چاول",
    "maize": "مکئی",
    "sugarcane": "گنا",
    "chickpea": "چنا",
    "lentil": "مصúr",
    "mungbean": "موگن",
    "mothbean": "موٹھ",
    "mustard": "سرسوں",
    "rapeseed": "تلہ",
    "groundnut": "مُونگ پھلی",
    "sesame": "تل",
    "sunflower": "سورج مکھی",
    "potato": "آلو",
    "onion": "پیاز",
    "tomato": "ٹماٹر",
    "okra": "بھنڈی",
    "chili": "مرچ",
    "garlic": "لیہسن",
    "ginger": "ادرک",
}

# Pest names in Urdu
PEST_URDU_NAMES = {
    "whitefly": "سفید مکھی",
    "aphid": "سیلا",
    "jassid": "چوسنی",
    "thrips": "ترپس",
    "bollworm": "کنڈی کا کیڑا",
    "pink_bollworm": "گلابی کنڈی کا کیڑا",
    "armyworm": "لشکری کیڑا",
    "stem_borer": "تنا کا کیڑا",
    "leaf_folder": "پتوں کو موڑنے والا کیڑا",
    "blast": "بلاسٹ (بیماری)",
    "blight": "بلائٹ (بیماری)",
    "rust": "زنگ (بیماری)",
    "smut": "کالا دانہ (بیماری)",
    "wilt": "مرجھا (بیماری)",
    "root_rot": "جڑ کا گلن (بیماری)",
}

# Soil types in Urdu
SOIL_URDU_NAMES = {
    "clay": "چکنی مٹی",
    "loam": "دو مٹی",
    "sandy": "ریتیلی مٹی",
    "silt": "گادہ مٹی",
    "clay_loam": "چکنی دو مٹی",
    "sandy_loam": "ریتیلی دو مٹی",
}

# Seasons in Urdu
SEASON_URDU_NAMES = {
    "rabi": "ربی",
    "kharif": "خریف",
    "zaid": "زائد",
}

# Water availability in Urdu
WATER_URDU_NAMES = {
    "rainfed": "بارانی",
    "limited_irrigation": "محدود آبپاشی",
    "full_irrigation": "پوری آبپاشی",
    "canal": "نہری آبپاشی",
    "tubewell": "ٹیوب ویل آبپاشی",
}