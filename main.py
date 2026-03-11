import os
import random
import asyncio
import aiohttp
from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from fastapi import FastAPI, Request, Response
import uvicorn
from contextlib import asynccontextmanager

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN ortam değişkeni eksik!")

SUPERGROUP_ID = -1003506180823

TOPICS = {
    "gunluk_rutin":  8,
    "yapilacaklar":  5,
    "aliskanlik":    3,
    "farkindalik":   4,
    "diksiyon":      310,
}

# ─────────────────────────────────────────────
# DİKSİYON 12 HAFTALIK PROGRAM
# ─────────────────────────────────────────────

DIKSIYON_PROGRAM = {
    1: """🎙️ *DİKSİYON PROGRAMI — HAFTA 1*
_R'nin Doğru Çıkış Noktasını Bulma_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Hata 1*
❌ R'yi boğazdan (Fransız R'si gibi) çıkarmak
✔ Doğrusu: R sesi dil ucunun üst damağa değip titreşmesiyle çıkar. Boğaz değil, ağız!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
Dil ortasının titreşimini hissetmek. 'N' sesiyle başlayıp titreşime geçmek. R'yi genizden değil ağızdan çıkarmak.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• Ağzını kapat, 'N' sesini çıkar — dil ucunu hafifçe titret. Bu titreşimi 10 kez hisset.
• Dudakları büzüp şişirir gibi — 5 tekrar.
• Dili dışarı çıkarıp yukarı-aşağı hareket ettirme — 5 tekrar.
• 'T-t-t-t' sesini hızlıca tekrarla (dil ucunu damaklara vur).

━━━━━━━━━━━━━━━━━━━━━━
🖊️ *KALEM YÖNTEMİ — Her gün 2 dk*
1. Bir kalemi yatay şekilde ön dişlerinin arasına koy.
2. Ağzın hafif açık olsun.
3. Dil ucunu üst dişlerinin arkasındaki damağa değdir.
4. Bu pozisyonda söyle: "dıdıdıdıdı"
Amaç: Dil geriye kaçmaz, R için doğru pozisyon öğrenilir.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Tek heceli (R'yi uzat): ar - er - or - ur - ür - ir - ır
İki heceli: ara - para - kara - yara - zara - bura - tara - sera - mera - cura
Üç heceli: araba - yarasa - karakol - parantez - karanlık - sarımsak - sararmak
Kelime sonu R: var - ser - ter - bir - dört - zor - mor - nur - pur - sur
Çeşitli: baraj - tarak - taraf - karar - yarar - ısrar - itiraz - garip - arif - arzu

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Bir berber bir berbere bre berber gel beraber bir berber dükkanı açalım demiş.
2. Kar ile kara karışmış, kara karardı, kar karardı.
3. Parlak pırıltılı pırlantalar pahalıdan da pahalıdır.
4. Ararın aradığı arada ararardı, ararken de arar.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Yarın akşam araba ile Karadeniz'e doğru yola çıkacağız.
• Karar vermek için biraz daha araştırma yapmalısınız.
• Kardeşim, karanlık koridorda kararsız bir şekilde durdu.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• R sesi genizden mi geliyor, ağızdan mı?
• Dilimin ortasını hissedebiliyor muyum?
• Kelime sonundaki R'leri yutuyor muyum?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    2: """🎙️ *DİKSİYON PROGRAMI — HAFTA 2*
_Sert Ünsüzlerle R (TR, KR, PR, BR)_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Hata 2*
❌ Dil çok geride kalıyor: Dil ağız ortasında kalırsa titreşim oluşmaz.
✔ Doğrusu: Dil ucu üst dişlerin hemen arkasındaki damağa gelmeli. Bunu kontrol et!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
Sert ünsüzlerin itici gücü ile R'nin daha belirgin çıkması. Dil bir önceki sert sesten güç alarak R'ye geçmeli.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• 'Pr-pr-pr, tr-tr-tr, kr-kr-kr' seslerini hızlıca tekrarla (her biri 10 kez).
• Dudakları germe-gevşetme — 10 tekrar.
• 'T' ve 'D' seslerini patlat, ardından 'R' ekle: T...R, D...R.

━━━━━━━━━━━━━━━━━━━━━━
🖊️ *D–R GEÇİŞ EGZERSİZİ — Her gün 3 dk*
Önce yavaş söyle: dı – dı – dı – dı
Sonra hızlandır: dıdıdıdıdı
Daha sonra: drdrdrdr
Son aşama: drrrrrr
Amaç: D sesi dilin damağa vurmasını sağlar ve R titreşimini başlatır.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
TR grubu: Trabzon - traktör - trafik - tıraş - tırmık - tırtıl - tren - trampet
KR grubu: krampon - kravat - kredi - krem - kral - kriz - krom - krater
PR grubu: pratik - prens - prenses - pranga - prova - profesör - proje - prensip
BR grubu: bravo - bre - briket - bronz - bronkoloji
Karma: program - problem - profil - proje - protokol

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Trakya'da traktörle trakya turu atarken traktörün tekeri trak trak takırdadı.
2. Pratik yapan prenses, prensine prömiyerde prensip gereği prens yapmış.
3. Kral kızı kırmızı kaponla kravatını kırıştırmış.
4. Profesör, projeyi pratik ve programlı bir şekilde anlattı.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Profesör, projeyi pratik bir şekilde anlattı.
• Trabzon'da traktörle trafiğe çıkmak tehlikeli.
• Prenses, prensine programı pratikte gösterdi.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• TR, KR gibi gruplarda R net çıkıyor mu?
• Kelimeleri söylerken dilim damaklara tam vuruyor mu?
• Hızlandıkça R'ler bozuluyor mu?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    3: """🎙️ *DİKSİYON PROGRAMI — HAFTA 3*
_Yumuşak Ünlülerle R (RE, Rİ, RA, RO, RU)_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Hata 3*
❌ Yeterince hava vermemek: Titreşim için hava gerekir, sessizce nefes tutarsan R çıkmaz.
✔ Doğrusu: Ağızdan biraz güçlü hava üfle. Titreşimi hava başlatır.

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
R'yi ince ve kalın ünlülerle akıcı hale getirmek. Her ünlü ile R arasındaki farkı hissetmek.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• 'Ra-ra-ra, re-re-re, ri-ri-ri, ro-ro-ro, ru-ru-ru' (her biri 10 kez, önce yavaş sonra hızlı).
• Dudakları 'o' ve 'i' yapıp geçişler — 10 tekrar.
• Derin nefes al, verirken 'rrrr' sesini uzat.

━━━━━━━━━━━━━━━━━━━━━━
💨 *TİTREŞİM BAŞLATMA EGZERSİZİ — Her gün 2 dk*
• Dil ucunu damağa yaklaştır.
• Hafif güçlü hava ver: rrrrrrrr
• Eğer çıkmazsa şu şekilde başla: trrrrrrr
• Dil ucunu damağa bastır, 5 sn tut, bırak — 10 tekrar.
Amaç: Dil ucunun titreşmesini sağlamak.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
RE sesi: recep - reklam - resim - rengarenk - reyhan - rezerv - rehber - rehin
Rİ/RI sesi: rihtim - rıza - ırmak - risturn - rica - ritim - rıfat
RO sesi: romatizma - rota - rol - roman - rozet - roket - robot - rodeo
RU/RÜ sesi: rüzgar - rütbe - rüya - gür - sür - kör - bür - tür - ruh
Karışık: renk - rakip - rutin - rekor - roman - rodaj - rafine - refahlı

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Recep, rengârenk resimler yapmayı çok severdi. Reyhan bahçesinde resim yapar, renk renk boyarlardı.
2. Rüzgâr gibi esen rüzgâr, rüyalarıma girdi rüzgâr.
3. Kırık kürek, kırık kova, kırıldı kaldı kıyıda.
4. Roma'da rozetli rehber, rota üzerinde roman okudu.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Rengârenk rozetler takmış olan rehber, Roma'yı anlattı.
• Rüzgârın romantik sesi ruhumu okşadı.
• Recep, rüyasında rengârenk bir rota izledi.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• 'Re' ve 'Ri' arasındaki fark hissediliyor mu?
• Rüzgar, kör gibi kelimelerde R yumuşak mı?
• Sesim genizden değil ağızdan geliyor mu?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    4: """🎙️ *DİKSİYON PROGRAMI — HAFTA 4*
_Kelime Sonundaki R'leri Güçlendirme_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Genel Tekrar*
3 Büyük Hata özeti:
❌ R'yi boğazdan çıkarmak → Dil ucu damağa değmeli
❌ Dil geride kalmak → Dil ucu üst dişlerin arkasına gelmeli
❌ Az hava vermek → Güçlü hava ile titreşim başlar
Bu haftadan itibaren üçünü birden otomatik kontrol et!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
En çok yutlan kelime sonu R'leri (var, gelir, gider) belirginleştirmek. Bu R'ler Türkçede en çok kaybolan seslerdir.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• 'Er, ar, or, ur, ür' seslerini tekrarla (her biri 10 kez, son R'yi uzat).
• Dudakları kuvvetlice büzüp aç — 10 tekrar.
• Yüksek sesle say: bir-R, iki, üç-R, dört-R, beş, altı-R.

━━━━━━━━━━━━━━━━━━━━━━
🥁 *DİL TIKLATMA EGZERSİZİ — Her gün 2 dk*
At yürüyüşü sesi çıkar: tak tak tak tak tak
Dil damağa vurup ayrılır.
🔁 30 tekrar
Amaç: Dil ucunun hızlı hareket etmesini sağlamak.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Fiil sonu R: gelir - gider - alır - verir - görür - sorar - arar - bilir - sever - ister
İsim sonu R: var - bir - dört - sür - nur - tür - kar - nar - dar - far
Çoğul ek R: annemler - babamlar - akşamlar - günler - bahçeler - çiçekler
Sayı R: bir - dört - üçer - beşer - altışar - yedişer - sekizer
Zaman eki R: gidiyorlar - geliyorlar - uyuyorlar - çalışıyorlar

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Var git oğul var git, talihini kendin ara. Giderim diyorsan gider, dönerim diyorsan döner.
2. Her giden geri gelmez, her bakan seni görmez.
3. Akşamlar oldu, kuşlar yuvalarına döndüler.
4. Gelir gider, gider gelir; ama her giden bir daha gelmez.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Babamlar yarın akşam gelirlerse, hep beraber gideriz.
• Dört arkadaşımız üçer üçer sıraya girdiler.
• Annemler geliyor, babamlar biliyor, kardeşlerim istiyor.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• 'Gelir' derken sondaki R net mi?
• Çoğul eklerinde R'yi söylüyor muyum?
• Kaydımı dinlediğimde R'ler düşüyor mu?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    5: """🎙️ *DİKSİYON PROGRAMI — HAFTA 5*
_R-L Ayrımı (Karıştırmayı Önlemek)_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Pozisyon Kontrolü*
Aynaya bak:
• L söylediğinde: Dil ucu yukarıya, dişlerin arkasına değiyor mu?
• R söylediğinde: Dil biraz geride, titreşim hissediliyor mu?
Fark net değilse önce bu ikisini ayır, sonra kelimelere geç.

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
R ile L'yi birbirine karıştırmadan, akıcı söyleyebilmek. Kulak eğitimi de gerekiyor — kayıtları dikkatlice dinle.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• 'La-la-la, ra-ra-ra' dönüşümlü (10 kez).
• Ayna karşısında 'L' söyle — dil ucu yukarı değdi mi? Şimdi 'R' söyle — fark ne?
• 'Lale - Rale, lirik - rilik' gibi zıt kelimeler.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
L kelimeleri: lale - lira - lüks - lütfen - lakin - limon - lamba - leyla - lavanta
R kelimeleri: rale - rol - ritim - renkli - rekor - rafine - rakip - roman
Karışık (dikkat): larva - leyla - lirik - liberal - labirent - ritmik - lazer
Zor çiftler: lira/riya - ral/lal - rol/lol - ruh/luh

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Leyla larva gibi lavların arasında kalmış, yaralı yaralı yalvarmış.
2. Laleleri rengârenk, reyhanları mis kokulu bir bahçede rüya gördüm.
3. Rihtımda kalan lüks lüferler, lakin rızkını arıyor.
4. Lale, yaralı ruhuna lirik şiirler okurdu.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Leyla, yaralı ruhuna lirik şiirler okurdu.
• Lalelerin rengârenk açması, ruhumu okşadı.
• Lamba ıslak rihtımı aydınlattı, leylekler uçtu.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• 'Leyla' ile 'rayla' arasındaki fark net mi?
• L söylediğimde dilim yukarıya değdi mi?
• R söylediğimde titreşim hissettim mi?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    6: """🎙️ *DİKSİYON PROGRAMI — HAFTA 6*
_R-Y Ayrımı & Nefes Kontrolü_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Hava Akışı*
R sesinde hava akışını test et: Avucunu ağzının önüne tut.
• R söylerken avucunda hava hissedebiliyor musun?
• Hissedemiyorsan daha güçlü hava ver.
• Çok kuvvetli değil — kontrollü, sürekli bir hava akışı olmalı.

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
R ile Y'yi ayırt etmek (Y çok ince, R daha sert ve titreşimli). Aynı zamanda uzun cümlelerde nefesi doğru yerlerde almak.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• 'Ya-ya-ya, ra-ra-ra' dönüşümlü (10 kez).
• Derin diyafram nefesi: Karnın şişsin, göğsün değil. 5 saniye al, 5 saniye ver.
• 'Y' ve 'R' sesini art arda söyle: y-r-y-r-y-r.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Y kelimeleri: yar - yara - yarım - yarış - yorgan - yıldız - yüksel - yumak
R kelimeleri: rar - ritar - risturn - rıza - rihtim
Her ikisi içeren: yarar - yırtık - yırtıcı - rüzgar - yürek - yarın - yiğit - reyhan
Nefes gerektiren: Kırklareli'nden Kırıkkale'ye giderken (bir nefeste söyle)

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Yaralı yaralı yalvarma, yarın yarış var.
2. Yorganım yırtıldı, yamalıyorum, yaramaz rüzgar yırttı.
3. Yarınki yarışta rekor kıracak yarışçı, yorgunluktan yığıldı.
4. Yaralı kuş, yuvasına dönmek için rüzgara yalvardı.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Kırklareli'nden kalkıp Kırıkkale'ye giderken / kırık dökük yollarda / karşılaşmalar beni yordu.
• Yarının rüzgarı bugünden belli olmaz.
• Yiğit oğul, yüreğini rüzgâra kaptırma.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• Y söylediğimde R çıkıyor mu?
• Uzun cümlelerde nefesim yetiyor mu?
• R'yi yutmadan cümlemi bitirebildim mi?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    7: """🎙️ *DİKSİYON PROGRAMI — HAFTA 7*
_Karma Tekerlemeler — Seviye 1_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Dil Kas Gücü*
Dil ucunu damağa bastır, 5 saniye tut, bırak — 10 tekrar.
At yürüyüşü: tak-tak-tak-tak (30 tekrar).
Bu iki egzersizi haftanın her günü ısınma olarak yap.
Güçlü dil = Net R!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
Birden fazla zor sesi aynı cümlede yönetmek. Tempo kontrolü: önce yavaş, sonra hızlan.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• Tüm ısınma hareketlerini birleştir: N titreşimi + TR + la-ra + ya-ra.
• 'Gübre-gübre-gübre' kelimesini 10 kez patlat.
• Kark-kark-kark sesini çıkart (K ve R birliği).

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
G+R grubu: gübre - gramer - grafik - granit - greyder
K+R grubu: kırk - kırmızı - kırık - kırıkkale - kırpma - kırtasiye
Karma: kırklareli - kırıkkale - kırpıntı - kırılgan - kırkpınar
Zor birleşikler: parçalanmak - karşılaşmak - borçlandırmak - yükümlülük

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Şu köşe yaz köşesi, bu köşe kış köşesi. Ortada bir su şişesi.
2. Gübreliğe gübre düşmüş, gübreliğin gübresi dökülmüş.
3. Kırk kürek kırık kürek, kırkı da kırık kürek.
4. Karınca kardan korkmaz, kardan adam korkar.
5. Kırklareli'nden kalkıp Kırıkkale'ye giderken, kırık dökük yollarda korkunç kazalar gördüm.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Kırkpınar'da kırk pehlivan güreşirken kırk bin kişi alkışlıyordu.
• Karşılaşmak, borçlanmak, yükümlü kalmak istemiyorum.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• Birden fazla zor sesi aynı cümlede yönetebildim mi?
• Hızlandıkça R'ler bozuldu mu?
• Nefesim nerede bitti?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    8: """🎙️ *DİKSİYON PROGRAMI — HAFTA 8*
_Karma Tekerlemeler — Seviye 2 & Hızlanma_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Hız Tuzağı*
Hızlandıkça R'leri yutmak çok yaygın bir hata!
Test: Bu cümleyi önce yavaş, sonra hızlı söyle:
"Kardeşim dört gün sonra Trabzon'dan gelecek."
Hızlı söyleyince R'ler kayıyor mu? Kayıyorsa tempo düşür, önce doğru söyle!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
Hızlanırken R'leri bozmamak. Tempo artışı: her tekrarda biraz daha hızlan, ama doğruluğu koru.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• Önceki haftanın tekerlemelerinden 2'sini seç ve hızlı söylemeyi dene.
• Metronom ya da telefonun metronom uygulaması ile ritmik tekrar.
• Nefes egzersizi: 4 al, 4 tut, 8 ver.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Hız gerektiren: trakya - traktör - trafik - tramvay - transfer
Karma hız: pratik-pratik-pratik (hızlanarak), profil-profil-profil
Zor birleşikler: kırıkpınar - kırkpınar - kırkkıloluk - kıvraklık

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — İstediğini seç, her birini 5 kez tekrarla*
1. Bir pır pırıldı pirinç pırıltısı, bir pırıl pırıldı pratik prensesin prensine prömiyerde prensipli prensip vaadi.
2. Trakya'da traktörle trakya turu atarken traktörün tekeri takır takır takırdadı.
3. Kırk kırık kürek, kırk kırık kovayla kırk gün kazı yaptı.
4. Tren tramvayı geçti, tramvay treni geçemedi.

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Kırkpınar'da kıvrak pehlivan, kırk kiloluk rakibini devirdi.
• Trabzon'dan transfer olan pratik profesör, projesini teslim etti.

━━━━━━━━━━━━━━━━━━━━━━
🐿️ *BU HAFTAYA ÖZEL — Porsuk Hazırlığı*
Aşağıdaki kelimeleri tek tek, çok yavaş söyle (her birini 10 kez):
sinik - kekere - mekere - dadanmış - bozala - porsuk
R ve K seslerine dikkat et!

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• Hızlanırken R'ler bozulmadı mı?
• Porsuk tekerlemesi kelimelerini doğru söyledim mi?
• Bu haftaki en zor tekerlemeyi rahatça söyledim mi?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    9: """🎙️ *DİKSİYON PROGRAMI — HAFTA 9*
_Porsuk Tekerlemesi — Aşamalı Çalışma (Bölüm 1)_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Kayıt & Dinleme*
Bu hafta mutlaka ses kaydı al!
• Porsuk tekerlemesinin ilk 2 cümlesini kaydet.
• Dinle: R sesleri net mi? Boğazdan mı geliyor?
• Hata bulduysan o kelimeyi 20 kez tekrar et.
Kulak eğitimi olmadan düzelme olmaz!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
'Bozala boz başlı pis porsuk' tekerlemesinin ilk iki cümlesini rahatça, doğru tempoda söyleyebilmek.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• B ve P seslerini güçlü patlat: B-B-B, P-P-P (her biri 15 kez).
• R sesini taze: 'N' ile başlayıp titreşime geç — 10 kez.
• K sesi: 'Kak-kak-kak' 10 kez.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Temel kelimeler (tek tek, abartarak): sinik - kekere - mekere - dadanmış - porsuk
İkişer kelime: boz ala - boz başlı - pis porsuk - kekere mekere
Üç kelime: bozala boz başlı - pis porsuk dadanmış
Hazırlık: tarlaya - ekilen - dadanan - zamandan - cevaben

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — Her birini 5 kez tekrarla*
1. Bu tarlaya bir sinik kekere mekere ekmişler. (5 kez yavaş)
2. Bu tarlaya da bir sinik kekere mekere ekmişler. (5 kez yavaş)
3. Bu tarlaya ekilen bir sinik kekere mekereye boz ala boz başlı pis porsuk dadanmış. (5 kez)
4. Bu tarlaya da ekilen bir sinik kekere mekereye de bozala boz başlı pis porsuk dadanmış. (5 kez)

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE ÇALIŞMASI*
• Sinik sinik bakma bana.
• Tarladaki porsuk dadanmıştı.
• Boz rengi bozala derler.

━━━━━━━━━━━━━━━━━━━━━━
🐿️ *AŞAMALI ÇALIŞMA YÖNTEMİ*
• Aşama 1: Her kelimeyi tek tek, abartarak oku.
• Aşama 2: İkişer kelime birleştir: 'boz ala - boz başlı', 'pis porsuk - dadanmış'.
• Aşama 3: Tam cümleyi çok yavaş oku (sanki yabancıya anlatır gibi).
• Aşama 4: Normal hızda dene. Her aşama için günlük 5 kez.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• İlk iki cümleyi yavaş söyledebildim mi?
• Sinik, kekere, mekere kelimelerini doğru söyledim mi?
• Porsuk kelimesinde R net çıktı mı?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    10: """🎙️ *DİKSİYON PROGRAMI — HAFTA 10*
_Porsuk Tekerlemesi — Aşamalı Çalışma (Bölüm 2)_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Tam Kontrol Listesi*
Her çalışma öncesi 30 saniye kontrol:
✔ Boğazım değil, dilim çalışıyor mu?
✔ Dil ucum damağa yakın mı?
✔ Nefesim güçlü ve kontrollü mü?
Bu üçü tamam → Egzersize başla!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
Tekeremenin tamamını ezberleyip, diyalog kısmını da dahil ederek söyleyebilmek.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• 9. Haftanın tekerleme cümlelerini taze tut — önce onları söyle.
• Diyalog pratiği: 'Sen ne zamandan beri...' cümlesini 10 kez tekrarla.
• Nefes kontrolü: Uzun cümle için derin diyafram nefesi.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Diyalog kelimeleri: zamandan - dadanan - cevaben - porsuğum - porsuksun
Zor geçişler: dadanan-boz-ala, mekereye-dadanan, beri-bu-tarlaya
Tüm tekerleme özeti: sinik - kekere - mekere - bozala - boz başlı - pis - porsuk - dadanmış - zamandan - cevaben

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TAM TEKERLEME*
_Aşama 1 — Çok yavaş, her kelime ayrı:_
Bu tarlaya bir sinik kekere mekere ekmişler. Bu tarlaya da bir sinik kekere mekere ekmişler. Bu tarlaya ekilen bir sinik kekere mekereye boz ala boz başlı pis porsuk dadanmış. Bu tarlaya da ekilen bir sinik kekere mekereye de bozala boz başlı pis porsuk dadanmış. O tarlaya ekilen bir sinik kekere mekereye dadanan boz ala boz başlı pis porsuk, diğer tarlaya ekilen bir sinik kekere mekereye dadanan boz ala boz başlı pis porsuğa demiş ki: 'Sen ne zamandan beri bu tarlaya ekilen bir sinik kekere mekereye dadanan boz ala boz başlı pis porsuksun?' O da ona cevaben: 'Sen ne zamandan beri o tarlaya ekilen bir sinik kekere mekereye dadanan boz ala boz başlı pis porsuksan, ben de o zamandan beri bu tarlaya ekilen bir sinik kekere mekereye dadanan boz ala boz başlı pis porsuğum.' demiş.

━━━━━━━━━━━━━━━━━━━━━━
🐿️ *BU HAFTAYA ÖZEL*
• Tekerlemeyi EZBERE söylemeye çalış. Yazılı bakmadan söyle.
• Günde 10 kez tam tekerlemeyi söyle — önce yavaş, sonra normal hız.
• Kaydını al ve dinle: Diyalog kısmındaki R'ler kayıyor mu?

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• Tam tekerlemeyi ezbere söyledim mi?
• Diyalog kısmında R'ler net çıktı mı?
• Hızlandıkça hangi kelimede takılıyorum?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    11: """🎙️ *DİKSİYON PROGRAMI — HAFTA 11*
_Günlük Konuşma & Haber Spikeri Metinleri_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *BU HAFTA HATIRLATMA — Günlük Hayat Testi*
Bu hafta günlük konuşmanda R'leri bilinçli takip et.
Arkadaşınla konuşurken, telefonda konuşurken...
• R sesini yuttuğun anları fark et.
• Fark ettiğinde dur, tekrar et, doğru söyle.
Otomatikleşme bu farkındalıkla başlar!

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
Öğrenilenleri günlük hayata taşımak. R sesi otomatik hale gelmeli — düşünmeden, doğal konuşurken de çıkabilmeli.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• Porsuk tekerlemesini 2 kez söyle — giriş ritüelimiz bu artık.
• Berber tekerlemesi: 3 kez hızlı.
• Kırk kürek tekerlemesi: 3 kez.

━━━━━━━━━━━━━━━━━━━━━━
📝 *KELİME LİSTESİ — Günde 3 kez, yavaş ve abartarak*
Günlük konuşma: arkadaş - buluşmak - rıhtım - kahve - rüzgar - sera - rota - karşı
Haber dili: uluslararası - renkli - performans - festival - katılım - program
Diksiyon kelimeleri: net - anlaşılır - vurgu - tonlama - hız - akıcılık

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — Her birini 5 kez tekrarla*
1. Porsuk tekerlemesi (Tam metin — 2 kez)
2. Bir berber bir berbere bre berber gel beraber (3 kez hızlı)
3. Kırk kırık kürek (3 kez hızlı)

━━━━━━━━━━━━━━━━━━━━━━
💬 *CÜMLE & METİN ÇALIŞMASI*
*Kişisel metin:* Dün akşam ne yaptığını anlat. Metni yaz ve R'lerin altını çiz, ardından oku.

*Haber metni örneği:*
Trabzon'da düzenlenen uluslararası kültür festivali, renkli görüntülere sahne oldu. Programa katılan yerli ve yabancı sanatçılar, performanslarıyla büyük beğeni topladı. Festival kapsamında açılan resim sergisi, sanatseverlerden tam not aldı.

*Örnek kişisel metin:*
Dün akşam arkadaşlarımla buluştuk. Rıhtımda bir kafede oturduk. Rüzgar biraz serindi ama manzara güzeldi. Arkadaşım Ramazan, yarınki gezi için plan yaptı. Trabzon'a gitmek istiyoruz. Arabayla gideceğiz, yaklaşık 4 saat sürüyormuş.

━━━━━━━━━━━━━━━━━━━━━━
✅ *KENDİNİ DEĞERLENDİR*
• Kişisel metinde R'leri yutuyor muyum?
• Haber metnini spiker gibi okuyabildi mi?
• Doğal konuşurken R'ler otomatik geliyor mu?

━━━━━━━━━━━━━━━━━━━━━━
💡 *HATIRLATMA*
Her gün 10-15 dakika ayır. Ses kaydı al ve dinle. Aynaya bakarak çalış.""",

    12: """🎙️ *DİKSİYON PROGRAMI — HAFTA 12*
_FİNAL — Genel Tekrar & Performans Testi_

━━━━━━━━━━━━━━━━━━━━━━
⚠️ *FİNAL HATIRLATMASI — 3 Büyük Hata Son Kez*
❌ Hata 1: R boğazdan → Dil ucu damağa
❌ Hata 2: Dil geride → Üst dişlerin arkasına
❌ Hata 3: Az hava → Güçlü, kontrollü hava
Bu üçü artık sende alışkanlık haline geldi mi?
1. Haftanın kaydını dinle, sonra bugünkü kaydı dinle. Fark var mı?

━━━━━━━━━━━━━━━━━━━━━━
🎯 *BU HAFTANIN HEDEFİ*
3 aylık sürecin tamamını ölçmek. En zor tekerlemeleri rahatça söyleyebilmek. R sesinin otomatik hale geldiğini onaylamak.

━━━━━━━━━━━━━━━━━━━━━━
🔥 *ISINMA — Her gün 2 dk*
• Tüm ısınma hareketlerini birleştir — N titreşimi, TR grubu, la-ra, ya-ra.
• Porsuk tekerlemesini giriş ritüeli olarak söyle.

━━━━━━━━━━━━━━━━━━━━━━
📝 *FİNAL KELİME TESTİ — Günde 3 kez*
kırklareli - kırıkkale - kırkpınar - borçlandırmak - yükümlülük
En zor gruplar: trakya-traktör, pratik-prensip, kırk-kırık, bozala-porsuk
Otomatiklik testi: Spontan 3 cümle kur — içinde R olan kelimeler kullan.

━━━━━━━━━━━━━━━━━━━━━━
🗣️ *TEKERLEMELER — Her birini 5 kez tekrarla*
1. PORSUK TEKERLEMESİ (3 kez, giderek hızlanarak — tam metin)
2. Trakya'da traktörle trakya turu atarken traktörün tekeri takır takır takırdadı.
3. Bir berber bir berbere bre berber gel beraber bir berber dükkanı açalım demiş.
4. Pratik yapan prenses, prensine prömiyerde prensipli prensip vaadi vermiş.
5. Kırk kırık kürek, kırk kırık kovayla kırk gün kazı yaptı.

━━━━━━━━━━━━━━━━━━━━━━
💬 *FİNAL CÜMLE ÇALIŞMASI*
• Final okuma: Kendi seçtiğin bir şiir ya da şarkı sözü — ezbere oku.
• Spontan konuşma: 2 dakika sürekli konuş — haber anlat, gün anlat, sefer anlat.
• Kayıt: Bu haftayı kaydet ve 1. hafta kaydınla karşılaştır.

━━━━━━━━━━━━━━━━━━━━━━
🏆 *FİNAL DEĞERLENDİRME*
• R'ler genizden değil ağızdan geliyor mu?
• Hızlı konuşurken R'ler bozulmuyor mu?
• Porsuk tekerlemesini rahatça söyledim mi?
• Günlük konuşmamda R otomatik hale geldi mi?
• 1. Hafta ile bugünün kaydını karşılaştırdım — fark var mı?

━━━━━━━━━━━━━━━━━━━━━━
🌟 *TEBRİKLER!*
12 haftalık programı tamamladın! Eğer hâlâ zorlanıyorsan bir dil ve konuşma terapistine git. Bu program temeli attı — uzman bunu pekiştirir. 💪"""
}

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
    "cevsen": [
        "📿 Maşallah! Cevşen'in nuru kalbine dolsun!",
        "🌟 Elhamdülillah! 15 bab Cevşen büyük bir bereket!",
        "💎 Allah kabul etsin! Cevşen okuyan gönül güçlenir.",
        "🕌 Mükemmel! Manevi zırhını kuşandın bugün!",
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
    "diksiyon_gun": [
        "🎙️ Bravo! Diksiyon çalışması dili güçlendirir, devam et!",
        "🗣️ Harika! Sesini her gün biraz daha ustalaştırıyorsun!",
        "🔥 Mükemmel! R sesi giderek daha net çıkacak!",
        "💪 Aferin! Düzenlilik başarının anahtarı!",
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

# ─────────────────────────────────────────────
# STATE HELPERS
# ─────────────────────────────────────────────

def get_daily_status(context):
    if "daily_status" not in context.bot_data:
        context.bot_data["daily_status"] = _empty_daily()
    return context.bot_data["daily_status"]

def _empty_daily():
    return {
        "uyandi": None, "namaz": None, "kitap_sabah": None, "yasin": None,
        "cevsen": None, "sinav": None, "mekik": None, "telefon": None,
        "hedef": None, "hedef_metni": "", "kitap_ogle": None, "ogrendigi": "",
        "aliskanlik_sadik": None, "zor_yapilan": "", "erteleme": None,
        "en_iyi_sey": "", "daha_iyi_sey": "", "ogrendigi_gece": "", "ek_cevap": "",
        "ezber_yaptim": None, "diksiyon_gun": None,
    }

def reset_daily_status(context):
    context.bot_data["daily_status"] = _empty_daily()

def get_10gun_sayaci(context):
    if "gun_10_sayac" not in context.bot_data:
        context.bot_data["gun_10_sayac"] = 1
    return context.bot_data["gun_10_sayac"]

def increment_10gun_sayaci(context):
    sayac = get_10gun_sayaci(context)
    sayac = (sayac % 10) + 1
    context.bot_data["gun_10_sayac"] = sayac

def get_weekly_counters(context):
    if "weekly_done" not in context.bot_data:
        context.bot_data["weekly_done"] = 0
        context.bot_data["weekly_total"] = 0
        context.bot_data["day_counter"] = 0
    return (context.bot_data["weekly_done"], context.bot_data["weekly_total"], context.bot_data["day_counter"])

def update_weekly_counters(context, done_today, total_today):
    get_weekly_counters(context)
    context.bot_data["weekly_done"] += done_today
    context.bot_data["weekly_total"] += total_today
    context.bot_data["day_counter"] += 1

def reset_weekly_counters(context):
    context.bot_data["weekly_done"] = 0
    context.bot_data["weekly_total"] = 0
    context.bot_data["day_counter"] = 0

def get_diksiyon_hafta(context):
    if "diksiyon_hafta" not in context.bot_data:
        context.bot_data["diksiyon_hafta"] = 1
    return context.bot_data["diksiyon_hafta"]

def set_diksiyon_hafta(context, hafta):
    context.bot_data["diksiyon_hafta"] = hafta

def get_waiting_for(context, chat_id):
    return context.bot_data.get("waiting_for", {}).get(str(chat_id))

def set_waiting_for(context, chat_id, key):
    if "waiting_for" not in context.bot_data:
        context.bot_data["waiting_for"] = {}
    context.bot_data["waiting_for"][str(chat_id)] = key

def clear_waiting_for(context, chat_id):
    if "waiting_for" in context.bot_data:
        context.bot_data["waiting_for"].pop(str(chat_id), None)

def get_gunluk_yapilacaklar(context):
    return context.bot_data.get("gunluk_yapilacaklar", [])

def set_gunluk_yapilacaklar(context, liste):
    context.bot_data["gunluk_yapilacaklar"] = liste

def get_gunluk_tamamlanan(context):
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
    if "haftalik_tamamlanan" not in context.bot_data:
        context.bot_data["haftalik_tamamlanan"] = {}
    return context.bot_data["haftalik_tamamlanan"]

def reset_haftalik_tamamlanan(context):
    context.bot_data["haftalik_tamamlanan"] = {}

def get_haftalik_ezber_plan(context):
    return context.bot_data.get("haftalik_ezber_plan", "")

def set_haftalik_ezber_plan(context, text):
    context.bot_data["haftalik_ezber_plan"] = text.strip()

def get_haftalik_ezber_tamam(context):
    return context.bot_data.get("haftalik_ezber_tamam")

def set_haftalik_ezber_tamam(context, value):
    context.bot_data["haftalik_ezber_tamam"] = value

# ─────────────────────────────────────────────
# BUTTON HELPERS
# ─────────────────────────────────────────────

def yes_no_buttons(key):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Evet", callback_data=f"{key}_yes"),
        InlineKeyboardButton("❌ Hayır", callback_data=f"{key}_no"),
    ]])

def farkindalik_buton(soru_key, soru_text):
    return InlineKeyboardMarkup([[InlineKeyboardButton(f"✍️ {soru_text}", callback_data=f"fark_{soru_key}")]])

def yapilacak_ekle_buttons(gorev_sayisi, is_haftalik=False):
    prefix = "hafta_" if is_haftalik else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"➕ {gorev_sayisi + 1}. Görevi Ekle", callback_data=f"{prefix}gorev_ekle_{gorev_sayisi}")],
        [InlineKeyboardButton("✅ Listemi Bitir", callback_data=f"{prefix}gorev_kaydet")]
    ])

def yapilacak_kontrol_buttons(is_haftalik=False):
    prefix = "hafta_" if is_haftalik else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Hepsini Yaptım", callback_data=f"{prefix}kontrol_hepsi")],
        [InlineKeyboardButton("⚠️ Kısmen Yaptım", callback_data=f"{prefix}kontrol_kismen")],
        [InlineKeyboardButton("❌ Yapamadım", callback_data=f"{prefix}kontrol_yok")]
    ])

def yapilacak_detay_buttons(liste, tamamlanan, is_haftalik=False):
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
    buttons.append([InlineKeyboardButton("📊 Raporu Tamamla", callback_data=f"{prefix}detay_rapor")])
    return InlineKeyboardMarkup(buttons)

def gunluk_bos_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yenisini Oluştur", callback_data="gunluk_olustur")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def gunluk_mevcut_buttons():
    """Günlük liste mevcut olduğunda gösterilecek butonlar."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Düzenle", callback_data="gunluk_duzenle_menu")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def gunluk_duzenle_menu_buttons():
    """Günlük düzenle alt menüsü: görev ekle veya sıfırdan oluştur."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Mevcut Listeye Görev Ekle", callback_data="gunluk_gorev_ekle_mevcut")],
        [InlineKeyboardButton("🗑️ Sil & Sıfırdan Oluştur",    callback_data="gunluk_olustur")],
        [InlineKeyboardButton("❌ Kapat",                       callback_data="slash_kapat")]
    ])

def haftalik_bos_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yenisini Oluştur", callback_data="haftalik_olustur")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def haftalik_mevcut_buttons():
    """Haftalık liste mevcut olduğunda gösterilecek butonlar."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Düzenle", callback_data="haftalik_duzenle_menu")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def haftalik_duzenle_menu_buttons():
    """Haftalık düzenle alt menüsü: görev ekle veya sıfırdan oluştur."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Mevcut Listeye Görev Ekle", callback_data="haftalik_gorev_ekle_mevcut")],
        [InlineKeyboardButton("🗑️ Sil & Sıfırdan Oluştur",    callback_data="haftalik_olustur")],
        [InlineKeyboardButton("❌ Kapat",                       callback_data="slash_kapat")]
    ])

def ezber_bos_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Yenisini Oluştur", callback_data="ezber_olustur")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def ezber_mevcut_buttons():
    """Ezber metni mevcut olduğunda gösterilecek butonlar."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Düzenle", callback_data="ezber_duzenle")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def rutin_baslat_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Rutini Başlat", callback_data="rutin_baslat")],
        [InlineKeyboardButton("❌ Kapat", callback_data="slash_kapat")]
    ])

def yapilacak_ekle_mevcut_buttons(gorev_sayisi, is_haftalik=False):
    """Mevcut listeye ek görev eklerken gösterilecek butonlar."""
    prefix = "hafta_" if is_haftalik else ""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Bir Tane Daha Ekle", callback_data=f"{prefix}gorev_ekle_{gorev_sayisi}")],
        [InlineKeyboardButton("✅ Tamam, Bitir",        callback_data=f"{prefix}gorev_kaydet")]
    ])

# ─────────────────────────────────────────────
# SEND HELPER
# ─────────────────────────────────────────────

async def send_to_topic(context, topic_key, text, parse_mode=None, reply_markup=None):
    thread_id = TOPICS[topic_key]
    kwargs = dict(chat_id=SUPERGROUP_ID, message_thread_id=thread_id, text=text)
    if parse_mode:
        kwargs["parse_mode"] = parse_mode
    if reply_markup:
        kwargs["reply_markup"] = reply_markup
    return await context.bot.send_message(**kwargs)

async def send_to_topic_long(context, topic_key, text, parse_mode=None):
    """4096 karakter limitini aşan mesajları ikiye bölerek gönderir."""
    limit = 4000
    if len(text) <= limit:
        await send_to_topic(context, topic_key, text, parse_mode=parse_mode)
        return
    bolme = text.rfind("\n", 0, limit)
    if bolme == -1:
        bolme = limit
    parca1 = text[:bolme]
    parca2 = text[bolme:]
    await send_to_topic(context, topic_key, parca1, parse_mode=parse_mode)
    await asyncio.sleep(0.5)
    await send_to_topic(context, topic_key, parca2, parse_mode=parse_mode)

# ─────────────────────────────────────────────
# SABAH RUTIN SORU ZİNCİRİ
# ─────────────────────────────────────────────

async def sabah_rutin(context: ContextTypes.DEFAULT_TYPE):
    karsilama = random.choice(SABAH_MESAJLARI)
    mesaj = f"☀️ *SABAH RUTİN KONTROLÜ*\n\n{karsilama}\n\n━━━━━━━━━━━━━━━━━━━━━━\n06:30'da uyandın mı?"
    await send_to_topic(context, "gunluk_rutin", mesaj, parse_mode="Markdown", reply_markup=yes_no_buttons("uyandi"))

async def ask_namaz(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="🕌 Sabah namazını kıldın mı?", reply_markup=yes_no_buttons("namaz"))

async def ask_kitap_sabah(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="📖 5 sayfa kitap okudun mu?", reply_markup=yes_no_buttons("kitap_sabah"))

async def ask_yasin(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="📿 Yasin okudun mu?", reply_markup=yes_no_buttons("yasin"))

async def ask_cevsen(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="📖 Bugün 15 bab Cevşen okudun mu?", reply_markup=yes_no_buttons("cevsen"))

async def ask_sinav(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="💪 20 şınav yaptın mı?", reply_markup=yes_no_buttons("sinav"))

async def ask_mekik(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="🏋️ 20 mekik yaptın mı?", reply_markup=yes_no_buttons("mekik"))

async def ask_telefon(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="📵 Telefonu ilk 30 dakika kullanmadın mı?", reply_markup=yes_no_buttons("telefon"))

async def ask_hedef(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="🎯 Bugün için 1 ana hedef belirledin mi?", reply_markup=yes_no_buttons("hedef"))

async def ask_ezber(context, chat_id, thread_id):
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="🧠 Bugün bir ezber (cümle/atasözü/vecize/şiir satırı) yaptın mı?", reply_markup=yes_no_buttons("ezber_yaptim"))

# ─────────────────────────────────────────────
# DİKSİYON ZAMANLAMA
# ─────────────────────────────────────────────

async def diksiyon_sabah_hatirlatma(context: ContextTypes.DEFAULT_TYPE):
    hafta = get_diksiyon_hafta(context)
    if hafta < 1 or hafta > 12:
        hafta = 1
        set_diksiyon_hafta(context, hafta)
    mesaj = (
        f"🎙️ *DİKSİYON ÇALIŞMASI — Hafta {hafta}*\n\n"
        f"Günlük 10-15 dakika diksiyon çalışma zamanı!\n\n"
        f"Bugün Hafta {hafta} programını uyguladın mı?\n"
        f"_(Programı görmek için /dicerik {hafta} yaz)_"
    )
    await send_to_topic(context, "diksiyon", mesaj, parse_mode="Markdown", reply_markup=yes_no_buttons("diksiyon_gun"))

# ─────────────────────────────────────────────
# ZAMANLI GÖREVLER
# ─────────────────────────────────────────────

async def ogle_kontrol(context: ContextTypes.DEFAULT_TYPE):
    await send_to_topic(context, "gunluk_rutin", "📖 *GÜN ORTASI – KİTAP & ÖĞRENME*\n\nBugün en az 5 sayfa kitap okudun mu?", parse_mode="Markdown", reply_markup=yes_no_buttons("kitap_ogle"))

async def aksam_aliskanlik(context: ContextTypes.DEFAULT_TYPE):
    await send_to_topic(context, "aliskanlik", "🔁 *AKŞAM – ALIŞKANLIK TAKİBİ*\n\nBugün alışkanlıklarına sadık kaldın mı?", parse_mode="Markdown", reply_markup=yes_no_buttons("aliskanlik_sadik"))

async def aksam_ezber_kontrol(context: ContextTypes.DEFAULT_TYPE):
    plan = get_haftalik_ezber_plan(context)
    if not plan.strip():
        return
    mesaj = f"🧠 *HAFTALIK EZBER KONTROLÜ*\n\nHedef:\n{plan}\n\nBugün ezberine devam ettin / tamamladın mı?"
    await send_to_topic(context, "gunluk_rutin", mesaj, parse_mode="Markdown", reply_markup=yes_no_buttons("hafta_ezber"))

async def gece_farkindalik(context: ContextTypes.DEFAULT_TYPE):
    gun_sayisi = get_10gun_sayaci(context)
    gun_bilgi = KENDIN_TANI_SORULAR[gun_sayisi]
    mesaj = f"🧠 *GECE – KENDİNİ TANIMA & FARKINDALIK*\n\n📆 Gün {gun_sayisi} – {gun_bilgi['tema']}\n\nBugün 4 soruya cevap vereceksin.\nHer soruya butona basarak başla!\n\n━━━━━━━━━━━━━━━━━━━━━━\nİlk soruya başlayalım:"
    await send_to_topic(context, "farkindalik", mesaj, parse_mode="Markdown", reply_markup=farkindalik_buton("en_iyi_sey", "Son 24 saatte en iyi yaptığım şey?"))

async def gunluk_yapilacaklar_planla(context: ContextTypes.DEFAULT_TYPE):
    set_gunluk_yapilacaklar(context, [])
    reset_gunluk_tamamlanan(context)
    mesaj = "📋 *GÜNLÜK YAPILACAKLAR PLANLAMA*\n\nYarın yapmayı planladığın görevleri ekle!\n\n📝 Mevcut Liste: (Boş)\n\n[➕ Görev Ekle] butonuna bas"
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown", reply_markup=yapilacak_ekle_buttons(0))

async def gunluk_yapilacaklar_kontrol(context: ContextTypes.DEFAULT_TYPE):
    liste = get_gunluk_yapilacaklar(context)
    if not liste:
        await send_to_topic(context, "yapilacaklar", "📋 Dün yapılacak listesi oluşturulmamış!")
        return
    reset_gunluk_tamamlanan(context)
    mesaj = "📋 *DÜN PLANLADIĞIN GÖREVLER*\n\n"
    for i, gorev in enumerate(liste, 1):
        mesaj += f"{i}. {gorev}\n"
    mesaj += "\n━━━━━━━━━━━━━━━━━━━━━━\nHangilerini tamamladın?"
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown", reply_markup=yapilacak_kontrol_buttons())

async def haftalik_yapilacaklar_planla(context: ContextTypes.DEFAULT_TYPE):
    set_haftalik_yapilacaklar(context, [])
    reset_haftalik_tamamlanan(context)
    mesaj = "📅 *HAFTALIK YAPILACAKLAR PLANLAMA*\n\nBu hafta mutlaka yapılacak görevleri ekle!\n\n📝 Mevcut Liste: (Boş)\n\n[➕ Görev Ekle] butonuna bas"
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown", reply_markup=yapilacak_ekle_buttons(0, is_haftalik=True))

async def haftalik_ezber_planla(context: ContextTypes.DEFAULT_TYPE):
    mesaj = f"📜 *BU HAFTA EZBER PLANI*\n\nBu hafta ezberlemek istediğin metni yazabilirsin.\n\nŞimdiki plan:\n{get_haftalik_ezber_plan(context) or '(henüz yok)'}\n\nCevabını yaz:"
    set_waiting_for(context, SUPERGROUP_ID, "hafta_ezber_plan")
    await send_to_topic(context, "yapilacaklar", mesaj, parse_mode="Markdown")

async def haftalik_diksiyon_hafta_guncelle(context: ContextTypes.DEFAULT_TYPE):
    """Her Pazartesi diksiyon hafta sayacını bir artırır (max 12)."""
    hafta = get_diksiyon_hafta(context)
    if hafta < 12:
        set_diksiyon_hafta(context, hafta + 1)
        yeni_hafta = hafta + 1
        mesaj = (
            f"🎙️ *YENİ DİKSİYON HAFTASI BAŞLADI!*\n\n"
            f"Bu hafta: *Hafta {yeni_hafta}*\n\n"
            f"Bu haftanın programını görmek için:\n/dicerik {yeni_hafta}"
        )
        await send_to_topic(context, "diksiyon", mesaj, parse_mode="Markdown")

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
    mesaj += f"\n━━━━━━━━━━━━━━━━━━━━━━\n🎯 Tamamlanan: {tamamlanan_sayi}/{len(liste)}\n\n"
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
    butonlu_keys = ["uyandi", "namaz", "kitap_sabah", "yasin", "cevsen", "sinav", "mekik", "telefon", "hedef", "kitap_ogle", "aliskanlik_sadik", "erteleme", "ezber_yaptim", "diksiyon_gun"]
    done_today = sum(1 for k in butonlu_keys if daily.get(k) == "✅")
    total_today = len(butonlu_keys)
    update_weekly_counters(context, done_today, total_today)
    weekly_done, weekly_total, day_counter = get_weekly_counters(context)
    percentage = int((done_today / total_today) * 100) if total_today else 0
    hedef_metni = daily.get("hedef_metni", "")
    hedef_goster = f"{daily.get('hedef') or '—'}" + (f" — {hedef_metni}" if hedef_metni else "")
    mesaj = (
        "📊 *GÜNLÜK RAPOR*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*☀️ SABAH RUTİN*\n"
        f"• 06:30 Uyanma: {daily.get('uyandi') or '—'}\n"
        f"• Sabah Namazı: {daily.get('namaz') or '—'}\n"
        f"• 5 Sayfa Kitap: {daily.get('kitap_sabah') or '—'}\n"
        f"• Yasin: {daily.get('yasin') or '—'}\n"
        f"• 15 Bab Cevşen: {daily.get('cevsen') or '—'}\n"
        f"• 20 Şınav: {daily.get('sinav') or '—'}\n"
        f"• 20 Mekik: {daily.get('mekik') or '—'}\n"
        f"• Telefonsuz 30dk: {daily.get('telefon') or '—'}\n"
        f"• Ana Hedef: {hedef_goster}\n"
        f"• Ezber: {daily.get('ezber_yaptim') or '—'}\n\n"
        "*📖 ÖĞLEN*\n"
        f"• Kitap Okuma: {daily.get('kitap_ogle') or '—'}\n"
        f"• Öğrendikleri: {daily.get('ogrendigi') or '—'}\n\n"
        "*🔁 AKŞAM*\n"
        f"• Alışkanlık Sadakati: {daily.get('aliskanlik_sadik') or '—'}\n"
        f"• Zor Yapılan: {daily.get('zor_yapilan') or '—'}\n"
        f"• Erteleme: {daily.get('erteleme') or '—'}\n\n"
        "*🎙️ DİKSİYON*\n"
        f"• Diksiyon Çalışması: {daily.get('diksiyon_gun') or '—'}\n\n"
        "*🧠 GECE - FARKINDALIK*\n"
        f"• En İyi Yaptığım: {daily.get('en_iyi_sey') or '—'}\n"
        f"• Daha İyi Yapabilirdim: {daily.get('daha_iyi_sey') or '—'}\n"
        f"• Öğrendiğim: {daily.get('ogrendigi_gece') or '—'}\n"
        f"• Ek Cevap: {daily.get('ek_cevap') or '—'}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 *GÜNLÜK SKOR*\n✅ Tamamlanan: {done_today}/{total_today}\n📈 Başarı Oranı: *%{percentage}*\n\n🔥 Devam et! 💪"
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
        "📅 *HAFTALIK PERFORMANS RAPORU*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 Toplam Görev: {weekly_total}\n✅ Tamamlanan: {weekly_done}\n❌ Yapılmayan: {weekly_total - weekly_done}\n\n"
        f"🎯 *Haftalık Başarı: %{percentage}*\n\n━━━━━━━━━━━━━━━━━━━━━━\n💪 Devam et, istikrar kazanıyorsun!\n🔥 Her gün daha iyiye gidiyorsun!"
    )
    await send_to_topic(context, "farkindalik", mesaj, parse_mode="Markdown")

# ─────────────────────────────────────────────
# KOMUTLAR
# ─────────────────────────────────────────────

async def test_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "✅ *Bot aktif ve çalışıyor!*\n\n🤖 Sistem durumu: Normal\n📡 Webhook: Bağlı\n⏰ Zamanlı görevler: Aktif\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n📌 *Günlük program (TR saati):*\n"
        "• 07:00 — Sabah rutini\n• 09:00 — Diksiyon hatırlatması\n• 11:00 — Öğlen kitap kontrolü\n"
        "• 18:00 — Akşam alışkanlık takibi\n• 18:10 — Günlük yapılacaklar kontrolü\n"
        "• 20:00 — Ezber kontrolü\n• 20:30 — Gece farkındalık\n"
        "• 22:30 — Günlük yapılacaklar planı\n• 22:40 — Günlük rapor\n\nSaati geldiğinde mesajlar otomatik gelecek! 💪"
    )
    await update.message.reply_text(mesaj, parse_mode="Markdown")

async def bilgi_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        "📌 *Kullanılabilir Komutlar:*\n\n"
        "/test — Botun çalışıp çalışmadığını kontrol eder\n"
        "/rutin — Günlük rutini manuel başlatır\n"
        "/gunluk — Günlük yapılacaklar listesini gösterir\n"
        "/haftalik — Haftalık yapılacaklar listesini gösterir\n"
        "/ezber — Haftalık ezber metnini gösterir\n"
        "/bilgi — Bu yardım mesajını gösterir\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎙️ *Diksiyon Komutları:*\n\n"
        "/diksiyon \\<1\\-12\\> — Diksiyon hafta sayacını ayarlar\n"
        "Örnek: /diksiyon 5 → 5\\. haftadan devam eder\n\n"
        "/dicerik \\<1\\-12\\> — O haftanın programını gösterir\n"
        "Örnek: /dicerik 3 → 3\\. haftanın egzersiz/kelime/tekerleme içeriği\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🧠 *Farkındalık Komutu:*\n\n"
        "/tanima \\<1\\-10\\> — Farkındalık gün sayacını ayarlar\n"
        "Örnek: /tanima 4 → 4\\. günden devam eder"
    )
    await update.message.reply_text(mesaj, parse_mode="MarkdownV2")

async def gunluk_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    liste = get_gunluk_yapilacaklar(context)
    if not liste:
        await update.message.reply_text(
            "📋 *GÜNLÜK YAPILACAKLAR*\n\n⚠️ Henüz günlük yapılacaklar listesi oluşturulmamış!\n\nYeni bir liste oluşturmak ister misin?",
            parse_mode="Markdown", reply_markup=gunluk_bos_buttons())
        return
    mesaj = "📋 *GÜNLÜK YAPILACAKLAR*\n\n"
    for i, gorev in enumerate(liste, 1):
        mesaj += f"{i}. {gorev}\n"
    mesaj += "\n━━━━━━━━━━━━━━━━━━━━━━\nListeyi düzenlemek ister misin?"
    await update.message.reply_text(mesaj, parse_mode="Markdown", reply_markup=gunluk_mevcut_buttons())

async def haftalik_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    liste = get_haftalik_yapilacaklar(context)
    if not liste:
        await update.message.reply_text(
            "📅 *HAFTALIK YAPILACAKLAR*\n\n⚠️ Henüz haftalık yapılacaklar listesi oluşturulmamış!\n\nYeni bir liste oluşturmak ister misin?",
            parse_mode="Markdown", reply_markup=haftalik_bos_buttons())
        return
    mesaj = "📅 *HAFTALIK YAPILACAKLAR*\n\n"
    for i, gorev in enumerate(liste, 1):
        mesaj += f"{i}. {gorev}\n"
    mesaj += "\n━━━━━━━━━━━━━━━━━━━━━━\nListeyi düzenlemek ister misin?"
    await update.message.reply_text(mesaj, parse_mode="Markdown", reply_markup=haftalik_mevcut_buttons())

async def ezber_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan = get_haftalik_ezber_plan(context)
    if not plan.strip():
        await update.message.reply_text(
            "📜 *HAFTALIK EZBER*\n\n⚠️ Henüz haftalık ezber metni eklenmemiş!\n\nYeni bir ezber metni oluşturmak ister misin?",
            parse_mode="Markdown", reply_markup=ezber_bos_buttons())
        return
    mesaj = f"📜 *HAFTALIK EZBER METNİ*\n\n{plan}\n\n━━━━━━━━━━━━━━━━━━━━━━\nEzber metnini düzenlemek ister misin?"
    await update.message.reply_text(mesaj, parse_mode="Markdown", reply_markup=ezber_mevcut_buttons())

async def rutin_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    daily = get_daily_status(context)
    if daily.get("uyandi") is not None:
        await update.message.reply_text(
            "☀️ *GÜNLÜK RUTİN*\n\n✅ Bugünkü rutin zaten başlatılmış!\n\nRutine kaldığın yerden devam edebilirsin.",
            parse_mode="Markdown")
        return
    await update.message.reply_text(
        "☀️ *GÜNLÜK RUTİN*\n\n⚠️ Bugün henüz sabah rutini başlatılmamış.\n\nŞimdi başlatmak ister misin?",
        parse_mode="Markdown",
        reply_markup=rutin_baslat_buttons())

async def diksiyon_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        hafta = get_diksiyon_hafta(context)
        await update.message.reply_text(
            f"🎙️ *DİKSİYON*\n\nŞu an *{hafta}. hafta* takibindesin.\n\nFarklı bir haftadan devam etmek için:\n`/diksiyon <1-12>`\n\nHaftanın programını görmek için:\n`/dicerik {hafta}`",
            parse_mode="Markdown")
        return
    try:
        hafta = int(args[0])
        if hafta < 1 or hafta > 12:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Geçerli bir hafta numarası gir (1-12).\nÖrnek: /diksiyon 5")
        return
    set_diksiyon_hafta(context, hafta)
    await update.message.reply_text(
        f"✅ Diksiyon takibi *{hafta}. haftadan* itibaren devam edecek!\n\nBu haftanın programını görmek için:\n`/dicerik {hafta}`",
        parse_mode="Markdown")

async def dicerik_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        hafta = get_diksiyon_hafta(context)
    else:
        try:
            hafta = int(args[0])
            if hafta < 1 or hafta > 12:
                raise ValueError
        except ValueError:
            await update.message.reply_text("⚠️ Geçerli bir hafta numarası gir (1-12).\nÖrnek: /dicerik 5")
            return
    program = DIKSIYON_PROGRAM.get(hafta, "")
    if not program:
        await update.message.reply_text("⚠️ Bu hafta için program bulunamadı.")
        return
    limit = 4000
    if len(program) <= limit:
        await update.message.reply_text(program, parse_mode="Markdown")
    else:
        bolme = program.rfind("\n", 0, limit)
        if bolme == -1:
            bolme = limit
        await update.message.reply_text(program[:bolme], parse_mode="Markdown")
        await asyncio.sleep(0.5)
        await update.message.reply_text(program[bolme:], parse_mode="Markdown")

async def tanima_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        gun = get_10gun_sayaci(context)
        gun_bilgi = KENDIN_TANI_SORULAR[gun]
        await update.message.reply_text(
            f"🧠 *KENDİNİ TANIMA*\n\nŞu an *{gun}. gün* takibindesin.\nTema: {gun_bilgi['tema']}\n\nFarklı bir günden devam etmek için:\n`/tanima <1-10>`",
            parse_mode="Markdown")
        return
    try:
        gun = int(args[0])
        if gun < 1 or gun > 10:
            raise ValueError
    except ValueError:
        await update.message.reply_text("⚠️ Geçerli bir gün numarası gir (1-10).\nÖrnek: /tanima 4")
        return
    context.bot_data["gun_10_sayac"] = gun
    gun_bilgi = KENDIN_TANI_SORULAR[gun]
    await update.message.reply_text(
        f"✅ Farkındalık takibi *{gun}. günden* itibaren devam edecek!\nTema: _{gun_bilgi['tema']}_",
        parse_mode="Markdown")

# ─────────────────────────────────────────────
# BUTTON HANDLER
# ─────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    daily = get_daily_status(context)
    chat_id = query.message.chat_id
    thread_id = query.message.message_thread_id

    if data == "slash_kapat":
        await query.edit_message_reply_markup(reply_markup=None)
        return

    if data == "rutin_baslat":
        reset_daily_status(context)
        karsilama = random.choice(SABAH_MESAJLARI)
        mesaj = f"☀️ *SABAH RUTİN KONTROLÜ*\n\n{karsilama}\n\n━━━━━━━━━━━━━━━━━━━━━━\n06:30'da uyandın mı?"
        await query.edit_message_text(mesaj, parse_mode="Markdown", reply_markup=yes_no_buttons("uyandi"))
        return

    # ─── GÜNLÜK DÜZENLE MENÜSÜ ───────────────────────────────────────────────
    if data == "gunluk_duzenle_menu":
        liste = get_gunluk_yapilacaklar(context)
        mesaj = "📋 *GÜNLÜK YAPILACAKLAR — DÜZENLE*\n\n"
        for i, gorev in enumerate(liste, 1):
            mesaj += f"{i}. {gorev}\n"
        mesaj += "\n━━━━━━━━━━━━━━━━━━━━━━\nNe yapmak istersin?"
        await query.edit_message_text(mesaj, parse_mode="Markdown", reply_markup=gunluk_duzenle_menu_buttons())
        return

    # ─── GÜNLÜK MEVCUT LİSTEYE GÖREV EKLE ──────────────────────────────────
    if data == "gunluk_gorev_ekle_mevcut":
        liste = get_gunluk_yapilacaklar(context)
        gorev_index = len(liste)
        waiting_key = f"yapilacak_{gorev_index}"
        set_waiting_for(context, chat_id, waiting_key)
        await query.edit_message_text(
            f"📋 Mevcut listene ek görev ekleyebilirsin.\n\n{gorev_index + 1}️⃣ Yeni görevi yaz:")
        return

    # ─── GÜNLÜK SIFIRDAN OLUŞTUR ─────────────────────────────────────────────
    if data == "gunluk_olustur":
        set_gunluk_yapilacaklar(context, [])
        reset_gunluk_tamamlanan(context)
        await query.edit_message_text(
            "📋 *GÜNLÜK YAPILACAKLAR PLANLAMA*\n\nYapmayı planladığın görevleri ekle!\n\n📝 Mevcut Liste: (Boş)\n\n[➕ Görev Ekle] butonuna bas",
            parse_mode="Markdown", reply_markup=yapilacak_ekle_buttons(0, is_haftalik=False))
        return

    # ─── HAFTALIK DÜZENLE MENÜSÜ ─────────────────────────────────────────────
    if data == "haftalik_duzenle_menu":
        liste = get_haftalik_yapilacaklar(context)
        mesaj = "📅 *HAFTALIK YAPILACAKLAR — DÜZENLE*\n\n"
        for i, gorev in enumerate(liste, 1):
            mesaj += f"{i}. {gorev}\n"
        mesaj += "\n━━━━━━━━━━━━━━━━━━━━━━\nNe yapmak istersin?"
        await query.edit_message_text(mesaj, parse_mode="Markdown", reply_markup=haftalik_duzenle_menu_buttons())
        return

    # ─── HAFTALIK MEVCUT LİSTEYE GÖREV EKLE ────────────────────────────────
    if data == "haftalik_gorev_ekle_mevcut":
        liste = get_haftalik_yapilacaklar(context)
        gorev_index = len(liste)
        waiting_key = f"yapilacak_hafta_{gorev_index}"
        set_waiting_for(context, chat_id, waiting_key)
        await query.edit_message_text(
            f"📅 Mevcut haftalık listene ek görev ekleyebilirsin.\n\n{gorev_index + 1}️⃣ Yeni görevi yaz:")
        return

    # ─── HAFTALIK SIFIRDAN OLUŞTUR ───────────────────────────────────────────
    if data == "haftalik_olustur":
        set_haftalik_yapilacaklar(context, [])
        reset_haftalik_tamamlanan(context)
        await query.edit_message_text(
            "📅 *HAFTALIK YAPILACAKLAR PLANLAMA*\n\nBu hafta mutlaka yapılacak görevleri ekle!\n\n📝 Mevcut Liste: (Boş)\n\n[➕ Görev Ekle] butonuna bas",
            parse_mode="Markdown", reply_markup=yapilacak_ekle_buttons(0, is_haftalik=True))
        return

    # ─── EZBER DÜZENLEME ─────────────────────────────────────────────────────
    if data == "ezber_olustur" or data == "ezber_duzenle":
        set_waiting_for(context, chat_id, "hafta_ezber_plan")
        await query.edit_message_text(
            "📜 *YENİ EZBER METNİ*\n\nEzberlemek istediğin metni yaz:\n(şiir, kıta, hadis, atasözü vs.)\n\n💬 Cevabını yaz:",
            parse_mode="Markdown")
        return

    if data == "hafta_ezber_yes":
        set_haftalik_ezber_tamam(context, "✅")
        await query.edit_message_text("🔥 Harika! Haftalık ezberine devam ediyorsun!")
        return
    if data == "hafta_ezber_no":
        set_haftalik_ezber_tamam(context, "❌")
        await query.edit_message_text(random.choice(OLUMSUZ_CEVAPLAR))
        return

    if data.startswith("fark_"):
        soru_key = data.replace("fark_", "")
        set_waiting_for(context, chat_id, soru_key)
        soru_metinleri = {
            "en_iyi_sey": "1️⃣ Son 24 saatte en iyi yaptığım şey?",
            "daha_iyi_sey": "2️⃣ Daha iyi yapabileceğim bir şey?",
            "ogrendigi_gece": "3️⃣ Bugün öğrendiğim 1 şey?",
            "ek_cevap": f"➕ {KENDIN_TANI_SORULAR[get_10gun_sayaci(context)]['ek_soru']}"
        }
        await query.edit_message_text(f"{soru_metinleri.get(soru_key, 'Cevabını yaz:')}\n\n💬 Cevabını yaz:")
        return

    # ─── YAPILACAKLAR GÖREV EKLEME / KONTROL / DETAY ────────────────────────
    is_haftalik = data.startswith("hafta_") and not data.startswith("hafta_ezber")
    prefix = "hafta_" if is_haftalik else ""

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
        mesaj += "\n📋 " + ("Pazar akşamı" if is_haftalik else "Yarın akşam") + " kontrol edeceğiz!"
        await query.edit_message_text(mesaj)
        clear_waiting_for(context, chat_id)
        return

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
            mesaj += random.choice(["🔥 Muhteşem! Hepsini tamamladın! 💪", "🦅 Kartal gibi uçuyorsun! 🎯", "⚔️ Yeniçeri disiplini! Her şeyi bitirdin! 🔥"])
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
            mesaj += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n" + random.choice(OLUMSUZ_CEVAPLAR)
            await query.edit_message_text(mesaj, parse_mode="Markdown")
            if is_haftalik:
                reset_haftalik_tamamlanan(context)
                set_haftalik_yapilacaklar(context, [])
            else:
                reset_gunluk_tamamlanan(context)
                set_gunluk_yapilacaklar(context, [])
        elif kontrol_tip == "kismen":
            if is_haftalik:
                reset_haftalik_tamamlanan(context)
            else:
                reset_gunluk_tamamlanan(context)
            tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)
            mesaj = "Hangilerini yaptın? Tümünü işaretle, sonra 📊 Raporu Tamamla'ya bas:\n\n"
            for i, gorev in enumerate(liste, 1):
                mesaj += f"{i}. {gorev}\n"
            await query.edit_message_text(mesaj, reply_markup=yapilacak_detay_buttons(liste, tamamlanan, is_haftalik))
        return

    if data == prefix + "detay_rapor":
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)
        tamamlanan_sayi = sum(1 for v in tamamlanan.values() if v == "✅")
        baslik = "📅 *HAFTALIK RAPOR*\n\n" if is_haftalik else "📋 *GÜNLÜK RAPOR*\n\n"
        mesaj = baslik
        for i, gorev in enumerate(liste):
            durum = tamamlanan.get(i, "❌")
            mesaj += f"{durum} {gorev}\n"
        mesaj += f"\n━━━━━━━━━━━━━━━━━━━━━━\n🎯 Tamamlanan: {tamamlanan_sayi}/{len(liste)}\n\n"
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

    if data.startswith(prefix + "detay_"):
        parts = data.split("_")
        result = parts[-1]
        gorev_index = int(parts[-2])
        liste = get_haftalik_yapilacaklar(context) if is_haftalik else get_gunluk_yapilacaklar(context)
        tamamlanan = get_haftalik_tamamlanan(context) if is_haftalik else get_gunluk_tamamlanan(context)
        if result in ("yes", "no"):
            tamamlanan[gorev_index] = "✅" if result == "yes" else "❌"
            mesaj = "Hangilerini yaptın? Tümünü işaretle, sonra 📊 Raporu Tamamla'ya bas:\n\n"
            for i, gorev in enumerate(liste, 1):
                mesaj += f"{i}. {gorev}\n"
            await query.edit_message_text(mesaj, reply_markup=yapilacak_detay_buttons(liste, tamamlanan, is_haftalik))
        return

    # ─── EVET / HAYIR BUTONLARI ───────────────────────────────────────────────
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
        await ask_cevsen(context, chat_id, thread_id)
    elif key == "cevsen":
        await ask_sinav(context, chat_id, thread_id)
    elif key == "sinav":
        await ask_mekik(context, chat_id, thread_id)
    elif key == "mekik":
        await ask_telefon(context, chat_id, thread_id)
    elif key == "telefon":
        await ask_hedef(context, chat_id, thread_id)
    elif key == "hedef":
        if result == "yes":
            set_waiting_for(context, chat_id, "hedef_metni")
            await context.bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text="🎯 Harika! Bugünkü ana hedefiniz nedir?\n\n✍️ Hedefini yaz:")
        else:
            await ask_ezber(context, chat_id, thread_id)
    elif key == "kitap_ogle":
        set_waiting_for(context, chat_id, "ogrendigi")
        await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="📝 Bugün öğrendiğin 1 şey neydi?\n\n💬 Cevabını yazabilirsin:")
    elif key == "aliskanlik_sadik":
        set_waiting_for(context, chat_id, "zor_yapilan")
        await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="📝 Zor geldiği halde yaptığın 1 şey neydi?\n\n💬 Cevabını yazabilirsin:")

# ─────────────────────────────────────────────
# TEXT HANDLER
# ─────────────────────────────────────────────

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
        await update.message.reply_text(f"✅ Haftalık ezber kaydedildi!\n\n{user_text}\n\nPazar akşamı kontrol edeceğiz.")
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

        # Güncel listeyi göster
        tip = "📅 HAFTALIK" if is_haftalik else "📋 GÜNLÜK"
        mesaj = f"{tip} YAPILACAKLAR LİSTESİ\n\n"
        for i, gorev in enumerate(liste, 1):
            mesaj += f"{i}. {gorev}\n"

        # Mevcut listeye ekleme modundaysak özel butonları göster
        # (gorev_index 0'dan başladığı için: len(liste)-1 == gorev_index ise ekleme modundayız)
        await update.message.reply_text(
            mesaj,
            reply_markup=yapilacak_ekle_mevcut_buttons(len(liste), is_haftalik)
        )
        clear_waiting_for(context, chat_id)
        return

    if waiting in ["en_iyi_sey", "daha_iyi_sey", "ogrendigi_gece", "ek_cevap"]:
        daily[waiting] = user_text
        clear_waiting_for(context, chat_id)
        gun_sayisi = get_10gun_sayaci(context)
        if waiting == "en_iyi_sey":
            await update.message.reply_text("✅ Kaydedildi!\n\nİkinci soruya geç:", reply_markup=farkindalik_buton("daha_iyi_sey", "Daha iyi yapabileceğim bir şey?"))
        elif waiting == "daha_iyi_sey":
            await update.message.reply_text("✅ Kaydedildi!\n\nÜçüncü soruya geç:", reply_markup=farkindalik_buton("ogrendigi_gece", "Bugün öğrendiğim 1 şey?"))
        elif waiting == "ogrendigi_gece":
            gun_bilgi = KENDIN_TANI_SORULAR[gun_sayisi]
            await update.message.reply_text("✅ Kaydedildi!\n\nSon soruya geç:", reply_markup=farkindalik_buton("ek_cevap", gun_bilgi['ek_soru']))
        elif waiting == "ek_cevap":
            await update.message.reply_text("✅ Tüm sorular tamamlandı! Günü güzel kapatıyorsun 🌙\n\n📊 Günlük rapor birazdan gelecek!")
        return

    if waiting == "hedef_metni":
        daily["hedef_metni"] = user_text
        clear_waiting_for(context, chat_id)
        await update.message.reply_text(
            f"🎯 Ana hedefin kaydedildi:\n\n*{user_text}*\n\nHaydi başar! 💪",
            parse_mode="Markdown")
        await asyncio.sleep(0.5)
        await ask_ezber(context, chat_id, thread_id)
        return

    daily[waiting] = user_text
    clear_waiting_for(context, chat_id)

    if waiting == "ogrendigi":
        await update.message.reply_text("✅ Kaydedildi! Teşekkürler 🙏")
    elif waiting == "zor_yapilan":
        await update.message.reply_text("✅ Kaydedildi!")
        await asyncio.sleep(0.5)
        await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text="🔁 Bugün ertelediğin bir şey oldu mu?", reply_markup=yes_no_buttons("erteleme"))

# ─────────────────────────────────────────────
# FASTAPI & WEBHOOK
# ─────────────────────────────────────────────

telegram_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global telegram_app
    print("🤖 Bot başlatılıyor...")
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    jq = telegram_app.job_queue

    jq.run_daily(sabah_rutin,                    time(4, 0))
    jq.run_daily(diksiyon_sabah_hatirlatma,       time(6, 0))
    jq.run_daily(ogle_kontrol,                   time(8, 0))
    jq.run_daily(gunluk_yapilacaklar_kontrol,    time(15, 10))
    jq.run_daily(aksam_aliskanlik,               time(15, 0))
    jq.run_daily(aksam_ezber_kontrol,            time(17, 0))
    jq.run_daily(gece_farkindalik,               time(17, 30))
    jq.run_daily(gunluk_yapilacaklar_planla,     time(19, 30))
    jq.run_daily(daily_report,                   time(19, 40))
    jq.run_daily(haftalik_yapilacaklar_planla,   time(16, 0),  days=(6,))
    jq.run_daily(haftalik_ezber_planla,          time(16, 30), days=(6,))
    jq.run_daily(haftalik_yapilacaklar_rapor,    time(17, 0),  days=(5,))
    jq.run_daily(haftalik_diksiyon_hafta_guncelle, time(7, 0), days=(0,))

    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.add_handler(CommandHandler("test", test_komutu))
    telegram_app.add_handler(CommandHandler("bilgi", bilgi_komutu))
    telegram_app.add_handler(CommandHandler("gunluk", gunluk_komutu))
    telegram_app.add_handler(CommandHandler("haftalik", haftalik_komutu))
    telegram_app.add_handler(CommandHandler("ezber", ezber_komutu))
    telegram_app.add_handler(CommandHandler("rutin", rutin_komutu))
    telegram_app.add_handler(CommandHandler("diksiyon", diksiyon_komutu))
    telegram_app.add_handler(CommandHandler("dicerik", dicerik_komutu))
    telegram_app.add_handler(CommandHandler("tanima", tanima_komutu))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    await telegram_app.initialize()
    await telegram_app.start()

    webhook_url = os.getenv("WEBHOOK_URL", "https://telegrambot-render-xodf.onrender.com/webhook")
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
    return {"status": "running", "bot": "active", "version": "4.2 - mevcut listeye gorev ekleme", "message": "Telegram Bot çalışıyor! 🚀"}

@app.get("/health")
@app.head("/health")
async def health():
    return {"status": "healthy", "version": "4.2"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    print(f"🌐 Server başlatılıyor (v4.2) - Port: {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
