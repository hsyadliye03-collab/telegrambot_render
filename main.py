import os
import random
import asyncio
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from fastapi import FastAPI, Request, Response
import uvicorn
from contextlib import asynccontextmanager

# =====================
# 🔑 TOKEN & SÜPER GRUP / KONU BAŞLIĞI ID'LERİ
# =====================
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN ortam değişkeni eksik!")

SUPERGROUP_ID = -1003506180823

TOPICS = {
    "gunluk_rutin":  14,
    "yapilacaklar":  16,
    "aliskanlik":    17,
    "farkindalik":   18,
}

# =====================
# 🌅 SABAH KARŞILAMA MESAJLARI
# =====================
SABAH_MESAJLARI = [
    "🦅 Güneş doğdu, sen de doğ! Fatih Sultan Mehmet 21 yaşında İstanbul'u fethetti. Sen bugün ne fethedeceksin?",
    "🌟 \"Bugün namazını kıl, yarın ölürsün belki!\" - Gaflet değil, gayret zamanı!",
    "🏹 \"Sabah erken kalkan yol alır!\" - Malazgirt'te Türk süvarisi gibi bugüne hazır mısın?",
    "📿 \"Uyku tatlıdır ama ibadet daha tatlıdır!\" - Fecr-i sadıkla uyan!",
    "🕌 \"Cennete giden yol sabah namazından geçer.\" - Bugün Allah'ın himayesinde bir gün!",
    "⚔️ \"Ben yalnız bir kişiyim ama bin kişi kadar çalışıyorum!\" - Mehmet Akif Ersoy gibi çalış!",
    "🌅 \"Sabahın seherinde kalkanlar, akşamın şerefini alır.\" - Haydi kalk!",
    "💎 \"İnsan sabahleyin ne ekerse, akşamleyin onu biçer.\" - Bugün ne ekeceksin?",
    "🐺 \"Korkma! Sönmez bu şafaklarda yüzen alsancak!\" - M. Akif Ersoy - Hücum et güne!",
    "🌟 \"Gün doğmadan neler doğar!\" - Mevlana - Sabahın sırrını keşfet!",
    "📖 \"Bir kitap bir insandır, oku!\" - İlk vahiy \"İkra!\" idi. Sen de oku!",
    "🎯 \"Ya olduğun gibi görün, ya göründüğün gibi ol!\" - Mevlana - Bugün hangi sen olacaksın?",
    "⭐ \"Gönülde kin tutmak, zehir içip düşmanın ölmesini beklemektir.\" - Mevlana - Temiz başla!",
    "🔥 \"Bir milletin haritası, gönlünde olduğu kadardır.\" - Necip Fazıl - Gönlünü genişlet!",
    "💪 \"Çalış çalış, ölürsün boş durursun da ölürsün!\" - Türk Atasözü",
    "🌄 \"Sabah vaktinde rızık kapıları açılır.\" - Hadis-i Şerif - Bereketli ol!",
    "🏛️ \"Fatih 21'inde İstanbul'u fethetti, sen bugün neyi fethedeceksin?\" - Hedefini koy!",
    "📚 \"İlim Çin'de de olsa gidip alınız!\" - Hadis-i Şerif - Bugün ne öğreneceksin?",
    "⚡ \"Dünkü güneş bugünü ısıtmaz!\" - Türk Atasözü - Yeni bir gün, yeni bir sen!",
    "🌺 \"Gül bahçesine girenler gülün kokusunu alır.\" - Tasavvuf - Güzel işlerle başla!",
    "🕊️ \"Sabah kuşu olana, kurttan pay vardır!\" - Erken kalk, avını al!",
    "🎪 \"Yalnızlık yoktur, matemsizlik yoktur. Mevlâ ile beraberlik vardır!\" - Yunus Emre",
    "📿 \"Akşamdan sabaha umma, sabahtan akşama ölüm gelir!\" - Yunus Emre - Anı yaşa!",
    "🌙 \"Fecr-i kâzib değil, fecr-i sadık!\" - Sahte şafak değil, gerçek aydınlık seninle!",
    "💫 \"Sabahın ilk saatinde kalkan, gün boyu bereketlidir.\" - Osmanlı Atasözü",
    "🏹 \"Yay gergin olmalı ki ok hedefe ulaşsın!\" - Disiplinli ol!",
    "🌟 \"Baki kalan bu cihan değildir, baki kalan Hak'tır, Hak'tan yana ol!\" - Baki",
    "🦅 \"Yavuz gibi azimli, Kanuni gibi heybetli, Fatih gibi kararlı ol!\" - Bugün senin günün!",
    "📖 \"Sabahları yataktan çıkmak zor, ama başarı daha da zordur!\" - Necip Fazıl",
    "🕌 \"Namazın farzını kıl, nafilesine devam et, sevabını gör!\" - Tasavvuf",
    "🌄 \"Her sabah yeni bir imkandır, bugün neyi kaçıracaksın?\" - Kalk ve kazan!",
    "💎 \"Hakikat arayanlara sabah namazı ilk kapıdır!\" - Mevlana",
    "⚔️ \"Kanuni'nin devleti gibi gün kurmaya hazır mısın?\" - İman, akıl, disiplin!",
    "🐺 \"Kurt gibi azimli, kartal gibi yüksel!\" - Bozkurt ruhuyla güne başla!",
]

# =====================
# 💬 MOTİVASYON CEVAPLARI
# =====================
OLUMLU_CEVAPLAR = {
    "uyandi": [
        "✅ Aferin! Erken kalkan yolcu, hem yol alır hem de yola bakır!",
        "💪 Süper! Sabahın erken saatlerinde bereketler var.",
        "🦅 Kartal gibi uçuyorsun! 06:30'da kalkmak disiplindir.",
        "⭐ Muhteşem! Osmanlı padişahları da sabah erken kalkardı.",
    ],
    "namaz": [
        "🕌 Mükemmel! \"Namazı kılanların huzuru vardır.\" - Maşallah!",
        "☪️ Allah razı olsun! Gününe bereketli başladın.",
        "🌟 Harika! Farz kılan, fazilet kazanır.",
        "💎 Elhamdülillah! Sabah namazı kalbin güneşidir.",
    ],
    "kitap_sabah": [
        "📚 Bravo! İlim nurdur, okumaya devam!",
        "🎓 Süper! Her sayfa seni güçlendirir.",
        "📖 Mükemmel! \"Oku!\" - İlk vahiy bile okumaktı.",
        "💡 Aferin! Okuyan toplumlar yönetir, okumayanlar yönetilir.",
    ],
    "yasin": [
        "📿 Maşallah! Yasin-i Şerif kalbe huzur verir.",
        "🌟 Elhamdülillah! Bereketli bir gün olacak.",
        "💎 Allah kabul etsin! Yasin okuyan gönül rahatlar.",
        "🕌 Mükemmel! Manevi gücün arttı bugün.",
    ],
    "sinav": [
        "💪 Kartal gibi! \"Sağlam kafa sağlam vücutta bulunur!\"",
        "🏋️ Muhteşem! Yeniçeri gibi güçlü ol!",
        "⚔️ Harika! Alp Eren gibi fit kalıyorsun!",
        "🔥 Süper! Bedeni güçlü, ruhu güçlü!",
    ],
    "mekik": [
        "🏋️ Bravo! Vücudunu tapınak gibi koru!",
        "💪 Aferin! Disiplin güç getirir!",
        "⚡ Harika! Her gün biraz daha güçleniyorsun!",
        "🦅 Mükemmel! Kartal gibi güçlüsün!",
    ],
    "telefon": [
        "📵 Mükemmel! Telefon değil, sen hayatını kontrol et!",
        "🧠 Bravo! Dikkatini dağıtmadın, odaklandın!",
        "⚡ Aferin! Dijital köle değil, dijital efendi ol!",
        "🎯 Harika! Sabah ruhunu telefona kaptırmadın!",
    ],
    "hedef": [
        "🎯 Muhteşem! \"Hedefi olmayan ok havada kaybolur.\"",
        "🏹 Aferin! Osmanlı okçusu gibi hedefe kilitlendin!",
        "🗺️ Süper! Yolunu bilmeyen, yolda kaybolur.",
        "💎 Harika! Hedefe yürüyen asla kaybolmaz!",
    ],
    "kitap_ogle": [
        "📚 Bravo! İlim nurdur, okumaya devam!",
        "🎓 Süper! Bilgi güçtür!",
        "📖 Mükemmel! Her kitap bir hazinedir.",
        "💡 Aferin! Okumak ruhun gıdasıdır.",
    ],
    "aliskanlik_sadik": [
        "🔥 Muhteşem! İstikrar başarının anahtarıdır!",
        "💪 Bravo! Disiplin özgürlüktür!",
        "⚡ Süper! Her gün biraz daha iyiye gidiyorsun!",
        "🎯 Harika! Alışkanlıkların seni inşa ediyor!",
    ],
    "erteleme": [
        "✅ Aferin! Ertelemek zamanı çalmaktır, sen çalmadın!",
        "🎯 Bravo! Bugün bugünün işini yaptın!",
        "💪 Mükemmel! Yarına bırakmadın, bugün hallettin!",
        "🔥 Harika! Disiplinli yaşam huzurlu yaşamdır!",
    ],
    "ezber_yaptim": [
        "🧠 Maşallah! Hafızan güçlü, kelimeler seninle!",
        "📜 Harika! Ezberin bereketi artsın!",
        "⭐ Çok güzel! Zihnin keskinleşiyor!",
        "💎 Kelimeleri kalbine nakşettin, aferin!",
    ],
}
OLUMSUZ_CEVAPLAR = [
    "💪 Sorun değil! Düşen kalkar, yenilmeyen kazanır. Yarın daha güçlü ol!",
    "🔥 Olur öyle günler! Mühim olan pes etmemek. \"Yedi defa düşen, sekiz kere kalkar!\"",
    "⚔️ Her savaş kazanılmaz ama savaşmaya devam et! Fatih de Varna'da yenildi, sonra İstanbul'u fethetti.",
    "🌱 Bugün yapamadın, yarın yaparsın. Tohum bugün filiz, yarın çınar olur!",
    "🦅 Takılma! \"Başarısızlık değil, henüz başarmamaktır.\" - Edison 10.000 kere denedi!",
    "💎 Her gün mükemmel olmak zorunda değilsin. Önemli olan yolda olmak!",
    "🏹 Ok bazen hedefe isabet etmez, ama atmaya devam eden okçu mutlaka vurur!",
    "🌟 \"Hayatta en büyük zafer, her yenilgiden sonra yeniden ayağa kalkmaktır.\" - Sen de kalkacaksın!",
    "☀️ Güneş bazen bulutların arkasına saklanır, ama hep doğar! Sen de doğacaksın yarın!",
    "🛡️ Bir muharebe kaybedildi diye savaş kaybedilmez! İlerle!",
]
ERTELEME_OLUMSUZ = [
    "💪 Olsun! Yarın erteleme, bugün yap! \"Bugünün işini yarına bırakma.\"",
    "🔥 Ertelemek alışkanlık olmasın! Yarın daha disiplinli ol!",
    "⚡ Sorun değil, ama dikkat et! Erteleme başarının düşmanıdır.",
    "🎯 Tamam, ama yarın direkt harekete geç! Erteleme tuzağına düşme!",
]

# =====================
# 📝 10 GÜNLÜK KENDİNİ TANIMA PROGRAMI
# =====================
KENDIN_TANI_SORULAR = {
    1: {"tema": "Farkındalık Başlangıcı", "ek_soru": "Bende gerçekten iyi olan 1 özellik ne?"},
    2: {"tema": "Güçlü Yanlar", "ek_soru": "Bende gerçekten iyi olan 1 özellik ne?"},
    3: {"tema": "Zayıf Yanları Olumlu Kullanma", "ek_soru": "Bir zayıf yönümü avantajlı hale nasıl getirebilirim?"},
    4: {"tema": "Enerji Yönetimi", "ek_soru": "Bana enerji veren 1 şey neydi?"},
    5: {"tema": "Hedeflere Yakınlaşma", "ek_soru": "Hedeflerime bugün attığım en küçük adım neydi?"},
    6: {"tema": "Gereksizleri Bırakma", "ek_soru": "Bugün vazgeçebileceğim gereksiz 1 alışkanlık ne?"},
    7: {"tema": "İlişkilerde Farkındalık", "ek_soru": "Bugün kiminle daha iyi iletişim kurdum?"},
    8: {"tema": "Kendine Söz Verme", "ek_soru": "Yarın kesin yapacağım tek şey ne?"},
    9: {"tema": "Disiplin Günü", "ek_soru": "Bugün kendimi en çok nerede disiplinli davrandım?"},
    10: {"tema": "Değerlendirme ve Kapanış", "ek_soru": "Son 10 günde değiştiğim 1 şey ne?"}
}

# =====================
# 📊 TAKİP VERİLERİ
# =====================
def get_daily_status(context: ContextTypes.DEFAULT_TYPE):
    if "daily_status" not in context.bot_data:
        context.bot_data["daily_status"] = _empty_daily()
    return context.bot_data["daily_status"]

def _empty_daily():
    return {
        "uyandi": None, "namaz": None, "kitap_sabah": None, "yasin": None,
        "sinav": None, "mekik": None, "telefon": None, "hedef": None,
        "kitap_ogle": None, "ogrendigi": "",
        "aliskanlik_sadik": None, "zor_yapilan": "", "erteleme": None,
        "en_iyi_sey": "", "daha_iyi_sey": "", "ogrendigi_gece": "", "ek_cevap": "",
        "ezber_yaptim": None,
    }

def reset_daily_status(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["daily_status"] = _empty_daily()

def get_10gun_sayaci(context: ContextTypes.DEFAULT_TYPE):
    if "gun_10_sayac" not in context.bot_data:
        context.bot_data["gun_10_sayac"] = 1
    return context.bot_data["gun_10_sayac"]

def increment_10gun_sayaci(context: ContextTypes.DEFAULT_TYPE):
    sayac = get_10gun_sayaci(context)
    sayac = (sayac % 10) + 1
    context.bot_data["gun_10_sayac"] = sayac

def get_weekly_counters(context: ContextTypes.DEFAULT_TYPE):
    if "weekly_done" not in context.bot_data:
        context.bot_data["weekly_done"] = 0
        context.bot_data["weekly_total"] = 0
        context.bot_data["day_counter"] = 0
    return (
        context.bot_data["weekly_done"],
        context.bot_data["weekly_total"],
        context.bot_data["day_counter"],
    )

def update_weekly_counters(context: ContextTypes.DEFAULT_TYPE, done_today: int, total_today: int):
    get_weekly_counters(context)
    context.bot_data["weekly_done"] += done_today
    context.bot_data["weekly_total"] += total_today
    context.bot_data["day_counter"] += 1

def reset_weekly_counters(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["weekly_done"] = 0
    context.bot_data["weekly_total"] = 0
    context.bot_data["day_counter"] = 0

def get_waiting_for(context: ContextTypes.DEFAULT_TYPE, chat_id):
    wf = context.bot_data.get("waiting_for", {})
    return wf.get(str(chat_id))

def set_waiting_for(context: ContextTypes.DEFAULT_TYPE, chat_id, key: str):
    if "waiting_for" not in context.bot_data:
        context.bot_data["waiting_for"] = {}
    context.bot_data["waiting_for"][str(chat_id)] = key

def clear_waiting_for(context: ContextTypes.DEFAULT_TYPE, chat_id):
    if "waiting_for" in context.bot_data:
        context.bot_data["waiting_for"].pop(str(chat_id), None)

# =====================
# 📋 YAPILACAKLAR LİSTESİ FONKSİYONLARI
# =====================
def get_gunluk_yapilacaklar(context):
    return context.bot_data.get("gunluk_yapilacaklar", [])

def set_gunluk_yapilacaklar(context, liste):
    context.bot_data["gunluk_yapilacaklar"] = liste

def get_gunluk_tamamlanan(context):
    # Her zaman AYNI dict referansını döndürür — asla sıfırdan oluşturmaz
    if "gunluk_tamamlanan" not in context.bot_data:
        context.bot_data["gunluk_tamamlanan"] = {}
    return context.bot_data["gunluk_tamamlanan"]

def reset_gunluk_tamamlanan(context):
    context.bot_data["gunluk_tamamlanan"] = {}

def get_haftalik_yapilacaklar(context):
    return context.bot_data.get("haftalik_yapilacaklar", [])

def set_haftalik_yapilacaklar(context, liste):
    context.bot_data["haftalik_yapilacaklar"] = liste

def get_haftalik_tamamlanan(context):
    # Her zaman AYNI dict referansını döndürür — asla sıfırdan oluşturmaz
    if "haftalik_tamamlanan" not in context.bot_data:
        context.bot_data["haftalik_tamamlanan"] = {}
    return context.bot_data["haftalik_tamamlanan"]

def reset_haftalik_tamamlanan(context):
    context.bot_data["haftalik_tamamlanan"] = {}

def get_haftalik_ezber_plan(context):
    return context.bot_data.get("haftalik_ezber_plan", "")

def set_haftalik_ezber_plan(context, text: str):
    context.bot_data["haftalik_ezber_plan"] = text.strip()

def get_haftalik_ezber_tamam(context):
    return context.bot_data.get("haftalik_ezber_tamam")

def set_haftalik_ezber_tamam(context, value):
    context.bot_data["haftalik_ezber_tamam"] = value

# =====================
# 🔘 BUTONLAR
# =====================
def yes_no_buttons(key: str):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Evet", callback_data=f"{key}_yes"),
            InlineKeyboardButton("❌ Hayır", callback_data=f"{key}_no"),
        ]
    ])

def farkindalik_buton(soru_key: str, soru_text: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✍️ {soru_text}", callback_data=f"fark_{soru_key}")]
    ])

def yapilacak_ekle_buttons(gorev_sayisi: int, is_haftalik=False):
    prefix = "hafta_" if is_haftalik else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ {gorev_sayisi + 1}. Görev Ekle", callback_data=f"{prefix}gorev_ekle_{gorev_sayisi}")],
        [InlineKeyboardButton("✅ Listemi Bitir", callback_data=f"{prefix}gorev_kaydet")]
    ])

def yapilacak_kontrol_buttons(is_haftalik=False):
    prefix = "hafta_" if is_haftalik else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Hepsini Yaptım", callback_data=f"{prefix}kontrol_hepsi")],
        [InlineKeyboardButton("⚠️ Kısmen Yaptım", callback_data=f"{prefix}kontrol_kismen")],
        [InlineKeyboardButton("❌ Yapamadım", callback_data=f"{prefix}kontrol_yok")]
    ])

def yapilacak_detay_buttons(liste: list, tamamlanan: dict, is_haftalik=False):
    """
    Her görev için ✅/❌ butonu gösterir.
    Daha önce işaretlenenler (seçili) olarak görünür.
    Altta "📊 Raporu Tamamla" butonu var — kullanıcı istediği zaman basar.
    """
    prefix = "hafta_" if is_haftalik else ""
    buttons = []
    for i, gorev in enumerate(liste):
        mevcut = tamamlanan.get(i)
        label_yes = f"✅ {i+1}.{' ◀' if mevcut == '✅' else ''}"
        label_no  = f"❌ {i+1}.{' ◀' if mevcut == '❌' else ''}"
        buttons.append([
            InlineKeyboardButton(label_yes, callback_data=f"{prefix}detay_{i}_yes"),
            InlineKeyboardButton(label_no,  callback_data=f"{prefix}detay_{i}_no"),
        ])
    buttons.append([
        InlineKeyboardButton("📊 Raporu Tamamla", callback_data=f"{prefix}detay_rapor")
    ])
    return InlineKeyboardMarkup(buttons)

# =====================
# 📨 YARDIMCI: Konuya mesaj gönder
# =====================
async def send_to_topic(context, topic_key: str, text: str, parse_mode=None, reply_markup=None):
    thread_id = TOPICS[topic_key]
    kwargs = dict(
        chat_id=SUPERGROUP_ID,
        message_thread_id=thread_id,
        text=text,
    )
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    if reply_markup:
        kwargs["reply_markup"] = reply_markup
    return await context.bot.send_message(**kwargs)

# =====================
# ⏰ GÖREV FONKSİYONLARI
# =====================
async def sabah_rutin(context: ContextTypes.DEFAULT_TYPE):
    karsilama = random.choice(SABAH_MESAJLARI)
    mesaj = (
        f"☀️ *SABAH RUTİN KONTROLÜ*\n\n"
        f"{karsilama}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"06:30'da uyandın mı?"
    )
    await send_to_topic(context, "gunluk_rutin", mesaj, parse_mode="Markdown",
                        reply_markup=yes_no_buttons("uyandi"))

async def ask_namaz(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="🕌 Sabah namazını kıldın mı?",
        reply_markup=yes_no_buttons("namaz")
    )

async def ask_kitap_sabah(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="📖 5 sayfa kitap okudun mu?",
        reply_markup=yes_no_buttons("kitap_sabah")
    )

async def ask_yasin(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="📿 Yasin okudun mu?",
        reply_markup=yes_no_buttons("yasin")
    )

async def ask_sinav(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="💪 20 şınav yaptın mı?",
        reply_markup=yes_no_buttons("sinav")
    )

async def ask_mekik(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="🏋️ 20 mekik yaptın mı?",
        reply_markup=yes_no_buttons("mekik")
    )

async def ask_telefon(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="📵 Telefonu ilk 30 dakika kullanmadın mı?",
        reply_markup=yes_no_buttons("telefon")
    )

async def ask_hedef(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="🎯 Bugün için 1 ana hedef belirledin mi?",
        reply_markup=yes_no_buttons("hedef")
    )

async def ask_ezber(context, chat_id, thread_id):
    await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id,
        text="🧠 Bugün bir ezber (cümle/atasözü/vecize/şiir satırı) yaptın mı?",
        reply_markup=yes_no_buttons("ezber_yaptim")
    )

async def ogle_kontrol(context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "📖 *GÜN ORTASI – KİTAP & ÖĞRENME*\n\n"
        "Bugün en az 5 sayfa kitap okudun mu?"
    )
    await send_to_topic(context, "gunluk_rutin", mesaj, parse_mode="Markdown",
                        reply_markup=yes_no_buttons("kitap_ogle"))

async def aksam_aliskanlik(context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "🔁 *AKŞAM – ALIŞKANLIK TAKİBİ*\n\n"
        "Bugün alışkanlıklarına sadık kaldın mı?"
    )
    await send_to_topic(context, "aliskanlik", mesaj, parse_mode="Markdown",
                        reply_markup=yes_no_buttons("aliskanlik_sadik"))

async def aksam_ezber_kontrol(context: ContextTypes.DEFAULT_TYPE):
    plan = get_haftalik_ezber_plan(context)
    if not plan.strip():
        return
    mesaj = (
        "🧠 *HAFTALIK EZBER KONTROLÜ*\n\n"
        f"Hedef:\n{plan}\n\n"
        "Bugün ezberine devam ettin / tamamladın mı?"
    )
    await send_to_topic(context, "gunluk_rutin", mesaj, parse_mode="Markdown",
                        reply_markup=yes_no_buttons("hafta_ezber"))

async def gece_farkindalik(context: ContextTypes.DEFAULT_TYPE):
    gun_sayisi = get_10gun_sayaci(context)
    gun_bilgi = KENDIN_TANI_SORULAR[gun_sayisi]
    mesaj = (
        f"🧠 *GECE – KENDİNİ TANIMA & FARKINDALIK*\n\n"
        f"📆 Gün {gun_sayisi} – {gun_bilgi['tema']}\n\n"
        f"Bugün 4 soruya cevap vereceksin.\n"
        f"Her soruya butona basarak başla!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"İlk soruya başlayalım:"
    )
    await send_to_topic(context, "farkindalik", mesaj, parse_mode="Markdown",
                        reply_markup=farkindalik_buton("en_iyi_sey", "Son 24 saatte en iyi yaptığım şey?"))

async def gunluk_yapilacaklar_planla(context: ContextTypes.DEFAULT_TYPE):
    set_gunluk_yapilacaklar(context, [])
    reset_gunluk_tamamlanan(context)
    mesaj = (
        "📋 *GÜNLÜK YAPILACAKLAR PLANLAMA*\n\n"
        "Yarın yapmayı planladığın görevleri ekle!\n\n"
        "📝 Mevcut Liste: (Boş)\n\n"
        "[➕ Görev Ekle] butonuna bas"
    )
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown",
                        reply_markup=yapilacak_ekle_buttons(0))

async def gunluk_yapilacaklar_kontrol(context: ContextTypes.DEFAULT_TYPE):
    liste = get_gunluk_yapilacaklar(context)
    if not liste:
        await send_to_topic(context, "yapilacaklar", "📋 Dün yapılacak listesi oluşturulmamış!")
        return
    reset_gunluk_tamamlanan(context)
    mesaj = "📋 *DÜN PLANLADIĞIN GÖREVLER*\n\n"
    for i, gorev in enumerate(liste, 1):
        mesaj += f"{i}. {gorev}\n"
    mesaj += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    mesaj += "Hangilerini tamamladın?"
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown",
                        reply_markup=yapilacak_kontrol_buttons())

async def haftalik_yapilacaklar_planla(context: ContextTypes.DEFAULT_TYPE):
    set_haftalik_yapilacaklar(context, [])
    reset_haftalik_tamamlanan(context)
    mesaj = (
        "📅 *HAFTALIK YAPILACAKLAR PLANLAMA*\n\n"
        "Bu hafta mutlaka yapılacak görevleri ekle!\n\n"
        "📝 Mevcut Liste: (Boş)\n\n"
        "[➕ Görev Ekle] butonuna bas"
    )
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown",
                        reply_markup=yapilacak_ekle_buttons(0, is_haftalik=True))

async def haftalik_ezber_planla(context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "📜 *BU HAFTA EZBER PLANI*\n\n"
        "Bu hafta ezberlemek istediğin metni (şiir, kıta, hadis, atasözü vs.) yazabilirsin.\n"
        "Birden fazla satır da olabilir.\n\n"
        "Şimdiki plan:\n"
        f"{get_haftalik_ezber_plan(context) or '(henüz yok)'}\n\n"
        "Cevabını yaz:"
    )
    set_waiting_for(context, SUPERGROUP_ID, "hafta_ezber_plan")
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown")

async def haftalik_yapilacaklar_rapor(context: ContextTypes.DEFAULT_TYPE):
    liste = get_haftalik_yapilacaklar(context)
    tamamlanan = get_haftalik_tamamlanan(context)
    if not liste:
        return
    tamamlanan_sayi = sum(1 for v in tamamlanan.values() if v == "✅")
    mesaj = "📅 *HAFTALIK RAPOR*\n\n"
    for i, gorev in enumerate(liste):
        durum = tamamlanan.get(i, "❌")
        mesaj += f"{durum} {gorev}\n"
    mesaj += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
    mesaj += f"🎯 Tamamlanan: {tamamlanan_sayi}/{len(liste)}\n\n"
    if tamamlanan_sayi == len(liste):
        mesaj += "🔥 Muhteşem! Hepsini tamamladın! Devam böyle! 💪"
    elif tamamlanan_sayi >= len(liste) * 0.7:
        mesaj += "👏 Harika performans! Küçük eksikler kalabilir, önemli olan devam! 🚀"
    else:
        mesaj += "💪 Bu hafta eksikler oldu ama pes etme! Gelecek hafta daha güçlü! 🦅"
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown")
    set_haftalik_yapilacaklar(context, [])
    reset_haftalik_tamamlanan(context)

async def daily_report(context: ContextTypes.DEFAULT_TYPE):
    daily = get_daily_status(context)
    butonlu_keys = [
        "uyandi", "namaz", "kitap_sabah", "yasin", "sinav", "mekik",
        "telefon", "hedef", "kitap_ogle", "aliskanlik_sadik", "erteleme",
        "ezber_yaptim"
    ]
    done_today = sum(1 for k in butonlu_keys if daily.get(k) == "✅")
    total_today = len(butonlu_keys)
    update_weekly_counters(context, done_today, total_today)
    weekly_done, weekly_total, day_counter = get_weekly_counters(context)
    percentage = int((done_today / total_today) * 100) if total_today else 0
    mesaj = (
        "📊 *GÜNLÜK RAPOR*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*☀️ SABAH RUTİN*\n"
        f"• 06:30 Uyanma: {daily.get('uyandi') or '—'}\n"
        f"• Sabah Namazı: {daily.get('namaz') or '—'}\n"
        f"• 5 Sayfa Kitap: {daily.get('kitap_sabah') or '—'}\n"
        f"• Yasin: {daily.get('yasin') or '—'}\n"
        f"• 20 Şınav: {daily.get('sinav') or '—'}\n"
        f"• 20 Mekik: {daily.get('mekik') or '—'}\n"
        f"• Telefonsuz 30dk: {daily.get('telefon') or '—'}\n"
        f"• Ana Hedef: {daily.get('hedef') or '—'}\n"
        f"• Ezber: {daily.get('ezber_yaptim') or '—'}\n\n"
        "*📖 ÖĞLEN*\n"
        f"• Kitap Okuma: {daily.get('kitap_ogle') or '—'}\n"
        f"• Öğrendikleri: {daily.get('ogrendigi') or '—'}\n\n"
        "*🔁 AKŞAM*\n"
        f"• Alışkanlık Sadakati: {daily.get('aliskanlik_sadik') or '—'}\n"
        f"• Zor Yapılan: {daily.get('zor_yapilan') or '—'}\n"
        f"• Erteleme: {daily.get('erteleme') or '—'}\n\n"
        "*🧠 GECE - FARKINDALIK*\n"
        f"• En İyi Yaptığım: {daily.get('en_iyi_sey') or '—'}\n"
        f"• Daha İyi Yapabilirdim: {daily.get('daha_iyi_sey') or '—'}\n"
        f"• Öğrendiğim: {daily.get('ogrendigi_gece') or '—'}\n"
        f"• Ek Cevap: {daily.get('ek_cevap') or '—'}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *GÜNLÜK SKOR*\n"
        f"✅ Tamamlanan: {done_today}/{total_today}\n"
        f"📈 Başarı Oranı: *%{percentage}*\n\n"
        f"🔥 Devam et! 💪"
    )
    await send_to_topic(context, "farkindalik", mesaj, parse_mode="Markdown")
    if day_counter >= 7:
        await weekly_report(context)
        reset_weekly_counters(context)
    increment_10gun_sayaci(context)
    reset_daily_status(context)

async def weekly_report(context: ContextTypes.DEFAULT_TYPE):
    weekly_done, weekly_total, _ = get_weekly_counters(context)
    percentage = int((weekly_done / weekly_total) * 100) if weekly_total else 0
    mesaj = (
        "📅 *HAFTALIK PERFORMANS RAPORU*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Toplam Görev: {weekly_total}\n"
        f"✅ Tamamlanan: {weekly_done}\n"
        f"❌ Yapılmayan: {weekly_total - weekly_done}\n\n"
        f"🎯 *Haftalık Başarı: %{percentage}*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💪 Devam et, istikrar kazanıyorsun!\n"
        "🔥 Her gün daha iyiye gidiyorsun!"
    )
    await send_to_topic(context, "farkindalik", mesaj, parse_mode="Markdown")

# =====================
# 🔔 BUTON HANDLER
# =====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    daily = get_daily_status(context)
    chat_id = query.message.chat_id
    thread_id = query.message.message_thread_id

    # ── Ezber butonları ──────────────────────────────────────
    if data == "ezber_yaptim_yes":
        daily["ezber_yaptim"] = "✅"
        await query.edit_message_text(random.choice(OLUMLU_CEVAPLAR["ezber_yaptim"]))
        return

    if data == "ezber_yaptim_no":
        daily["ezber_yaptim"] = "❌"
        await query.edit_message_text(random.choice(OLUMSUZ_CEVAPLAR))
        return

    if data == "hafta_ezber_yes":
        set_haftalik_ezber_tamam(context, "✅")
        await query.edit_message_text("🔥 Harika! Haftalık ezberine devam ediyorsun!")
        return

    if data == "hafta_ezber_no":
        set_haftalik_ezber_tamam(context, "❌")
        await query.edit_message_text(random.choice(OLUMSUZ_CEVAPLAR))
        return

    # ── Farkındalık soruları ─────────────────────────────────
    if data.startswith("fark_"):
        soru_key = data.replace("fark_", "")
        set_waiting_for(context, chat_id, soru_key)
        soru_metinleri = {
            "en_iyi_sey": "1️⃣ Son 24 saatte en iyi yaptığım şey?",
            "daha_iyi_sey": "2️⃣ Daha iyi yapabileceğim bir şey?",
            "ogrendigi_gece": "3️⃣ Bugün öğrendiğim 1 şey?",
            "ek_cevap": f"➕ {KENDIN_TANI_SORULAR[get_10gun_sayaci(context)]['ek_soru']}"
        }
        await query.edit_message_text(
            f"{soru_metinleri.get(soru_key, 'Cevabını yaz:')}\n\n💬 Cevabını yaz:"
        )
        return

    # ── Yapılacaklar: haftalık mı günlük mü? ────────────────
    is_haftalik = data.startswith("hafta_") and not data.startswith("hafta_ezber")
    prefix = "hafta_" if is_haftalik else ""

    # ── Görev ekleme ─────────────────────────────────────────
    if data.startswith(prefix + "gorev_ekle_"):
        gorev_index = int(data.split("_")[-1])
        waiting_key = f"yapilacak_{'hafta_' if is_haftalik else ''}{gorev_index}"
        set_waiting_for(context, chat_id, waiting_key)
        await query.edit_message_text(f"{gorev_index + 1}️⃣ Görevi yaz:")
        return

    if data == prefix + "gorev_kaydet":
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        if not liste:
            await query.edit_message_text("⚠️ Hiç görev eklenmedi!")
            return
        mesaj = f"✅ {len(liste)} görev kaydedildi!\n\n"
        for i, gorev in enumerate(liste, 1):
            mesaj += f"{i}. {gorev}\n"
        mesaj += "\n📋 " + ("Cuma akşamı" if is_haftalik else "Yarın akşam") + " kontrol edeceğiz!"
        await query.edit_message_text(mesaj)
        clear_waiting_for(context, chat_id)
        return

    # ── Kontrol butonları (hepsi / kısmen / hiç) ─────────────
    if data.startswith(prefix + "kontrol_"):
        kontrol_tip = data.replace(prefix + "kontrol_", "")
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)

        if kontrol_tip == "hepsi":
            for i in range(len(liste)):
                tamamlanan[i] = "✅"
            baslik = "📅 *HAFTALIK RAPOR*\n\n" if is_haftalik else "📋 *GÜNLÜK RAPOR*\n\n"
            mesaj = baslik + "\n".join(f"✅ {g}" for g in liste)
            mesaj += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
            mesaj += random.choice([
                "🔥 Muhteşem! Hepsini tamamladın! 💪",
                "🦅 Kartal gibi uçuyorsun! 🎯",
                "⚔️ Yeniçeri disiplini! Her şeyi bitirdin! 🔥",
            ])
            await query.edit_message_text(mesaj, parse_mode="Markdown")
            if is_haftalik:
                reset_haftalik_tamamlanan(context)
                set_haftalik_yapilacaklar(context, [])
            else:
                reset_gunluk_tamamlanan(context)
                set_gunluk_yapilacaklar(context, [])

        elif kontrol_tip == "yok":
            for i in range(len(liste)):
                tamamlanan[i] = "❌"
            baslik = "📅 *HAFTALIK RAPOR*\n\n" if is_haftalik else "📋 *GÜNLÜK RAPOR*\n\n"
            mesaj = baslik + "\n".join(f"❌ {g}" for g in liste)
            mesaj += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
            mesaj += random.choice(OLUMSUZ_CEVAPLAR)
            await query.edit_message_text(mesaj, parse_mode="Markdown")
            if is_haftalik:
                reset_haftalik_tamamlanan(context)
                set_haftalik_yapilacaklar(context, [])
            else:
                reset_gunluk_tamamlanan(context)
                set_gunluk_yapilacaklar(context, [])

        elif kontrol_tip == "kismen":
            # Tamamlananı temizle, detay butonlarını göster
            if is_haftalik:
                reset_haftalik_tamamlanan(context)
            else:
                reset_gunluk_tamamlanan(context)
            tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)
            mesaj = "Hangilerini yaptın? Tümünü işaretle, sonra 📊 Raporu Tamamla'ya bas:\n\n"
            for i, gorev in enumerate(liste, 1):
                mesaj += f"{i}. {gorev}\n"
            await query.edit_message_text(
                mesaj,
                reply_markup=yapilacak_detay_buttons(liste, tamamlanan, is_haftalik)
            )
        return

    # ── Detay: "Raporu Tamamla" butonu ───────────────────────
    if data == prefix + "detay_rapor":
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)
        tamamlanan_sayi = sum(1 for v in tamamlanan.values() if v == "✅")
        baslik = "📅 *HAFTALIK RAPOR*\n\n" if is_haftalik else "📋 *GÜNLÜK RAPOR*\n\n"
        mesaj = baslik
        for i, gorev in enumerate(liste):
            durum = tamamlanan.get(i, "❌")
            mesaj += f"{durum} {gorev}\n"
        mesaj += f"\n━━━━━━━━━━━━━━━━━━━━━━\n"
        mesaj += f"🎯 Tamamlanan: {tamamlanan_sayi}/{len(liste)}\n\n"
        if tamamlanan_sayi == len(liste):
            mesaj += "🔥 Muhteşem! Hepsini tamamladın! 💪"
        elif tamamlanan_sayi >= len(liste) * 0.7:
            mesaj += "👏 Harika! Çoğunu tamamladın! Yarın da devam! 💪"
        else:
            mesaj += random.choice(OLUMSUZ_CEVAPLAR)
        await query.edit_message_text(mesaj, parse_mode="Markdown")
        if is_haftalik:
            reset_haftalik_tamamlanan(context)
            set_haftalik_yapilacaklar(context, [])
        else:
            reset_gunluk_tamamlanan(context)
            set_gunluk_yapilacaklar(context, [])
        return

    # ── Detay: tek tek işaretleme ─────────────────────────────
    if data.startswith(prefix + "detay_"):
        parts = data.split("_")
        result = parts[-1]          # "yes" veya "no"
        gorev_index = int(parts[-2])
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)

        if result in ("yes", "no"):
            tamamlanan[gorev_index] = "✅" if result == "yes" else "❌"
            # Butonu güncel haliyle yenile (seçim göster)
            mesaj = "Hangilerini yaptın? Tümünü işaretle, sonra 📊 Raporu Tamamla'ya bas:\n\n"
            for i, gorev in enumerate(liste, 1):
                mesaj += f"{i}. {gorev}\n"
            await query.edit_message_text(
                mesaj,
                reply_markup=yapilacak_detay_buttons(liste, tamamlanan, is_haftalik)
            )
        return

    # ── Ana rutin yes/no butonları ───────────────────────────
    parts = data.rsplit("_", 1)
    if len(parts) != 2 or parts[1] not in ("yes", "no"):
        return

    key, result = parts[0], parts[1]
    daily[key] = "✅" if result == "yes" else "❌"

    if key == "erteleme":
        motivasyon = random.choice(OLUMLU_CEVAPLAR["erteleme"]) if result == "no" else random.choice(ERTELEME_OLUMSUZ)
    else:
        motivasyon = random.choice(OLUMLU_CEVAPLAR.get(key, ["👍 Kaydedildi!"])) if result == "yes" else random.choice(OLUMSUZ_CEVAPLAR)

    await query.edit_message_text(motivasyon)
    await asyncio.sleep(0.5)

    if key == "uyandi":
        await ask_namaz(context, chat_id, thread_id)
    elif key == "namaz":
        await ask_kitap_sabah(context, chat_id, thread_id)
    elif key == "kitap_sabah":
        await ask_yasin(context, chat_id, thread_id)
    elif key == "yasin":
        await ask_sinav(context, chat_id, thread_id)
    elif key == "sinav":
        await ask_mekik(context, chat_id, thread_id)
    elif key == "mekik":
        await ask_telefon(context, chat_id, thread_id)
    elif key == "telefon":
        await ask_hedef(context, chat_id, thread_id)
    elif key == "hedef":
        await ask_ezber(context, chat_id, thread_id)
    elif key == "kitap_ogle":
        set_waiting_for(context, chat_id, "ogrendigi")
        await context.bot.send_message(
            chat_id=chat_id, message_thread_id=thread_id,
            text="📝 Bugün öğrendiğin 1 şey neydi?\n\n💬 Cevabını yazabilirsin:"
        )
    elif key == "aliskanlik_sadik":
        set_waiting_for(context, chat_id, "zor_yapilan")
        await context.bot.send_message(
            chat_id=chat_id, message_thread_id=thread_id,
            text="📝 Zor geldiği halde yaptığın 1 şey neydi?\n\n💬 Cevabını yazabilirsin:"
        )

# =====================
# 💬 YAZI MESAJI HANDLER
# =====================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    chat_id = update.message.chat_id
    thread_id = update.message.message_thread_id
    waiting = get_waiting_for(context, chat_id)
    if not waiting:
        return

    user_text = update.message.text.strip()
    daily = get_daily_status(context)

    if waiting == "hafta_ezber_plan":
        set_haftalik_ezber_plan(context, user_text)
        set_haftalik_ezber_tamam(context, None)
        await update.message.reply_text(
            f"✅ Haftalık ezber kaydedildi!\n\n{user_text}\n\nCuma akşamı kontrol edeceğiz."
        )
        clear_waiting_for(context, chat_id)
        return

    if waiting.startswith("yapilacak_"):
        parts = waiting.split("_")
        is_haftalik = len(parts) > 2 and parts[1] == "hafta"
        gorev_index = int(parts[-1])
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        liste.append(user_text)
        if is_haftalik:
            set_haftalik_yapilacaklar(context, liste)
        else:
            set_gunluk_yapilacaklar(context, liste)
        mesaj = "📋 YAPILACAKLAR LİSTESİ\n\n"
        for i, gorev in enumerate(liste, 1):
            mesaj += f"{i}. {gorev}\n"
        await update.message.reply_text(
            mesaj,
            reply_markup=yapilacak_ekle_buttons(len(liste), is_haftalik)
        )
        clear_waiting_for(context, chat_id)
        return

    if waiting in ["en_iyi_sey", "daha_iyi_sey", "ogrendigi_gece", "ek_cevap"]:
        daily[waiting] = user_text
        clear_waiting_for(context, chat_id)
        gun_sayisi = get_10gun_sayaci(context)
        if waiting == "en_iyi_sey":
            await update.message.reply_text(
                "✅ Kaydedildi!\n\nİkinci soruya geç:",
                reply_markup=farkindalik_buton("daha_iyi_sey", "Daha iyi yapabileceğim bir şey?")
            )
        elif waiting == "daha_iyi_sey":
            await update.message.reply_text(
                "✅ Kaydedildi!\n\nÜçüncü soruya geç:",
                reply_markup=farkindalik_buton("ogrendigi_gece", "Bugün öğrendiğim 1 şey?")
            )
        elif waiting == "ogrendigi_gece":
            gun_bilgi = KENDIN_TANI_SORULAR[gun_sayisi]
            await update.message.reply_text(
                "✅ Kaydedildi!\n\nSon soruya geç:",
                reply_markup=farkindalik_buton("ek_cevap", gun_bilgi['ek_soru'])
            )
        elif waiting == "ek_cevap":
            await update.message.reply_text(
                "✅ Tüm sorular tamamlandı! Günü güzel kapatıyorsun 🌙\n\n"
                "📊 Günlük rapor birazdan gelecek!"
            )
        return

    daily[waiting] = user_text
    clear_waiting_for(context, chat_id)

    if waiting == "ogrendigi":
        await update.message.reply_text("✅ Kaydedildi! Teşekkürler 🙏")
    elif waiting == "zor_yapilan":
        await update.message.reply_text("✅ Kaydedildi!")
        await asyncio.sleep(0.5)
        await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="🔁 Bugün ertelediğin bir şey oldu mu?",
            reply_markup=yes_no_buttons("erteleme")
        )

# =====================
# 🚀 GLOBAL APPLICATION
# =====================
telegram_app = None

# =====================
# 🔧 LIFESPAN MANAGER
# =====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    print("🤖 Bot başlatılıyor...")
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    jq = telegram_app.job_queue

    # UTC saatleri — Türkiye UTC+3
    jq.run_daily(sabah_rutin,                  time(4, 0))              # 07:00 TRT
    jq.run_daily(ogle_kontrol,                 time(8, 0))              # 11:00 TRT
    jq.run_daily(aksam_aliskanlik,             time(15, 0))             # 18:00 TRT
    jq.run_daily(aksam_ezber_kontrol,          time(17, 0))             # 20:00 TRT
    jq.run_daily(gece_farkindalik,             time(19, 0))             # 22:00 TRT
    jq.run_daily(daily_report,                 time(19, 30))            # 22:30 TRT
    jq.run_daily(gunluk_yapilacaklar_planla,   time(19, 0))             # 22:00 TRT
    jq.run_daily(gunluk_yapilacaklar_kontrol,  time(17, 0))             # 20:00 TRT
    jq.run_daily(haftalik_yapilacaklar_planla, time(16, 0), days=(5,))  # 19:00 TRT Cumartesi
    jq.run_daily(haftalik_ezber_planla,        time(16, 30), days=(5,)) # 19:30 TRT Cumartesi
    jq.run_daily(haftalik_yapilacaklar_rapor,  time(17, 0), days=(4,))  # 20:00 TRT Cuma

    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    await telegram_app.initialize()
    await telegram_app.start()

    webhook_url = os.getenv("WEBHOOK_URL", "https://telegram-bot-xxxx.onrender.com/webhook")
    print(f"🔗 Webhook ayarlanıyor: {webhook_url}")
    try:
        await telegram_app.bot.set_webhook(url=webhook_url)
        print("✅ Webhook başarıyla ayarlandı!")
    except Exception as e:
        print(f"❌ Webhook hatası: {e}")

    yield

    print("🛑 Bot kapatılıyor...")
    await telegram_app.stop()
    await telegram_app.shutdown()

# =====================
# 🌐 FASTAPI UYGULAMASI
# =====================
app = FastAPI(title="Telegram Bot Webhook", lifespan=lifespan)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        json_data = await request.json()
        update = Update.de_json(json_data, telegram_app.bot)
        if update:
            await telegram_app.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        print(f"❌ Webhook hatası: {e}")
        return Response(status_code=500)

@app.get("/")
async def root():
    return {
        "status": "running",
        "bot": "active",
        "version": "3.1 - Detay buton fix",
        "message": "Telegram Bot çalışıyor! 🚀"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "3.1"}

# =====================
# 🚀 MAIN
# =====================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🌐 Server başlatılıyor (v3.1) - Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")