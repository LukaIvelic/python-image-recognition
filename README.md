# 🖐️ AI prepoznavanje ruku i upravljanje mišem

> **Upravljaj svojim računalom pokretima ruku kao u SF filmovima.**  
> Pokreću MediaPipe i OpenCV.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![MediaPipe](https://img.shields.io/badge/MediaPipe-Latest-orange) ![License](https://img.shields.io/badge/License-MIT-green)

Ovo je napredna, modularna Python aplikacija koja pretvara tvoju web kameru u precizan upravljač mišem. Osjeti glatko kretanje kursora, intuitivno klikanje i ugrađenu virtualnu ploču za crtanje izravno na ekranu.

---

## ✨ Mogućnosti

- **🖱️ Precizno upravljanje mišem**: 
  - **OneEuroFilter zaglađivanje**: Napredno smanjenje podrhtavanja za prirodan osjećaj "ljepljivog" kursora.
  - **Sigurnosna zaštita**: Stabilna implementacija koja sprječava rušenje aplikacije.
- **🔫 Napredni pokreti**:
  - **Pištolj (palac + kažiprst)**: Dvostruki klik (s provjerom geometrije kako bi se izbjeglo slučajno aktiviranje).
  - **Štipanje (palac + kažiprst)**: Lijevi klik / povlačenje (drag).
  - **Znak mira (Peace sign)**: Način za skrolanje (pomicanje gore/dolje).
- **🎨 Virtualni način crtanja**:
  - Crtaj po ekranu koristeći samo kažiprst.
  - **Jasne boje**: Crtanje u rozoj, zelenoj ili plavoj boji koje se jasno vide.
  - **Gumica**: Koristi otvorenu šaku za brisanje cijelog platna.
- **👁️ Snažan AI vid**:
  - **Pojačanje zasićenosti**: Automatski poboljšava boje za bolje praćenje ruku čak i uz složene pozadine.
  - **CLAHE poboljšanje**: Pametno prilagođavanje kontrasta za različite uvjete osvjetljenja.
  - **Model Complexity 1**: Koristi najprecizniji MediaPipe model.
- **🪞 Pametno iskustvo**:
  - **Zrcalni način (Mirror Mode)**: Prirodna interakcija kao da se gledaš u ogledalu.
  - **Vizualne povratne informacije**: HUD u stvarnom vremenu prikazuje prepoznate pokrete i razinu pouzdanosti AI modela.

---

## 🛠️ Instalacija

### Preduvjeti
- Python 3.8 ili noviji
- Web kamera

### Postavljanje
1. **Kloniraj repozitorij**:
   ```bash
   git clone https://github.com/LukaIvelic/python-image-recognition.git
   cd python-image-recognition
   ```

2. **Instaliraj potrebne pakete**:
   ```bash
   pip install -r requirements.txt
   ```
   *Napomena: Na macOS-u ćeš možda trebati dati dozvolu Terminalu ili VSCode-u za pristup kameri i "Accessibility" opcijama (za upravljanje mišem) u postavkama sustava.*

---

## 🚀 Korištenje

Pokreni glavnu aplikaciju:
```bash
python main.py
```

### 🎮 Kontrole i pokreti

| Pokret | Prsti | Akcija |
|:---:|:---|:---|
| **POINT** | ☝️ Samo kažiprst | **Pomicanje kursora** |
| **PINCH** | 👌 Dodir palca i kažiprsta | **Lijevi klik (drži za povlačenje)** |
| **GUN** | 🔫 Ispruženi palac i kažiprst | **Dvostruki klik** |
| **PEACE** | ✌️ Kažiprst i srednji prst | **Skrolanje** (pomiči ruku gore/dolje) |
| **SCROLL** | 🤟 Tri prsta | **Skrolanje** (alternativa) |
| **DRAW** | Pritisni `d` na tipkovnici | **Uključi/isključi crtanje** |
| **STOP** | 🖐️ Otvorena šaka | **Zaustavi / Gumica (u načinu crtanja)** |

### ⌨️ Kratice na tipkovnici
- **`q`**: Izlaz iz aplikacije
- **`d`**: Prebaci između miša i crtanja
- **`c`**: Očisti sve nacrtano

---

## ⚙️ Podešavanje

Sve možeš fino podesiti u datoteci `config/config.py`.

**Glavne postavke:**
```python
# Osjetljivost
MOUSE_SMOOTHING = 0.5   # Veći broj = glađe ali s više kašnjenja
SCROLL_AMOUNT = 50      # Koliko piksela se pomiče pri skrolanju

# Detekcija
MIN_DETECTION_CONFIDENCE = 0.8  # Stroža detekcija
MODEL_COMPLEXITY = 1            # 0=Brzo, 1=Precizno

# Vizualno
DRAWING_OPACITY = 1.0   # 1.0 = Neprozirne linije
```

---

---

## 🧠 Implementacija vs. Biblioteke

Za potrebe kolegija, ovdje je pregled onoga što smo sami programirali u usporedbi s korištenim gotovim rješenjima:

### 🛠️ Što smo sami implementirali (Ručni rad):
- **Logika prepoznavanja pokreta (`gesture_recognizer.py`)**: Umjesto gotovih rješenja za geste, sami smo napisali matematičke provjere (udaljenosti između zglobova, kutovi prstiju) kako bismo definirali što je "pištolj", "štipanje" ili "znak mira".
- **One Euro Filter (`one_euro_filter.py`)**: Implementirali smo ovaj napredni algoritam za filtriranje signala od nule kako bismo eliminirali podrhtavanje kursora kod kretanja ruku.
- **Upravljanje crtanjem (`drawing_manager.py`)**: Razvili smo vlastiti sustav za upravljanje platnom, bojama i prozirnošću linija koje se iscrtavaju preko videa.
- **Mapiranje koordinata (`geometry.py`)**: Napisali smo vlastitu logiku za pretvaranje koordinata iz prostora kamere u piksele ekrana, uključujući "padding" sustav koji omogućuje lakše dosezanje rubova ekrana.
- **HUD i Vizualizacija (`hud.py` & `visualizer.py`)**: Dizajnirali smo i programirali sučelje koje u stvarnom vremenu prikazuje status sustava i povratne informacije korisniku.

### 📚 Korištene biblioteke (Vanjski alati):
- **MediaPipe**: Koristimo ga isključivo za detekciju osnovnih 21 točaka (landmarkova) na ruci u 3D prostoru.
- **OpenCV**: Služi nam za rad s video streamom (čitanje kamere, crtanje grafike na frejmove, obrada slike poput CLAHE i HSV poboljšanja).
- **PyAutoGUI**: Koristimo za slanje naredbi operacijskom sustavu (pomicanje kursora, klikovi, skrolanje).
- **NumPy**: Pomaže nam kod brzih matematičkih operacija nad nizovima podataka.

---

## 🏗️ Struktura projekta
```
.
├── config/             # Postavke i definicije pokreta
│   ├── config.py       # Glavna konfiguracija sustava
│   └── gestures.py     # Definicije geometrije pokreta
├── src/                # Glavna logika
│   ├── app.py          # Glavna petlja aplikacije
│   ├── ai_worker.py    # Pozadinska obrada za AI zadatke
│   ├── camera_stream.py# Optimizirano upravljanje kamerom
│   ├── drawing_manager.py # Logika za crtanje i brisanje
│   ├── hand_detector.py# MediaPipe i poboljšanje slike (CLAHE/HSV)
│   ├── gesture_recognizer.py # Geometrijska logika za pokrete
│   ├── mouse_controller.py   # Upravljanje mišem i zaglađivanje
│   ├── one_euro_filter.py    # OneEuroFilter za stabilan kursor
│   ├── visualizer.py   # Prikazivanje slike na ekranu
│   ├── ui/             # UI komponente
│   │   └── hud.py      # HUD prikaz (Heads-Up Display)
│   └── utils/          # Pomoćni alati
│       └── geometry.py # Matematika za koordinatni sustav
├── main.py             # Početna točka aplikacije
└── requirements.txt    # Popis paketa
```

---

## ⚠️ Sigurnost i privatnost
- **Sve se obrađuje lokalno**: Video se nikada ne šalje u oblak.
- **Sigurnosni prekid**: Ako se miš "zgrabi" ili pobjegne kontroli, samo brzo gurni svoj pravi miš u kut ekrana da zaustaviš aplikaciju (ili pritisni `q`).

---

## 📜 Licenca
MIT Licenca. Slobodno koristi i mijenjaj.

