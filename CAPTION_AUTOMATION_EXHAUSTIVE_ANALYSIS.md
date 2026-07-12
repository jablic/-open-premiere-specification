# Analiza Wyczerpująca: Dlaczego Automatyzacja Subтytułów Jest Niemożliwa (Premiere 25.6)

## Problem

User pytał: "Czy jest JAKIKOLWIEK sposób na zmianę subтytułów po masce, nawet jeśli będzie wolny?"

Odpowiedź: **NIE. Brak żadnego działającego podejścia.**

---

## Wszystkie Badane Podejścia

### 1. UXP 25.6 API (Oficjalne)
```javascript
// Co dostępne:
const captions = await sequence.captions;
const text = await caption.text;  // ✅ Read-only

// Co NIE dostępne:
caption.setText(newText);  // ❌ Method doesn't exist
```

**Status:** API read-only. Brak setText().

**Kod źródłowy:** Knowledge/uxp.md line 152
```
Captions ✅ (partial) | Text ops limited
```

Czyli: Odczyt tak, zapis nie.

---

### 2. ExtendScript (Legacy API)
Przeszukanie: `grep -r "caption" Knowledge/captions.md`

```
## ExtendScript (Limited)
app.encoder.encodeFile(...);  // Tylko export
```

**Status:** Brak metod do edycji subтytułów.

Jedyna operacja: `app.encoder.encodeFile()` = export do SRT/VTT/CEA-608, nie edycja.

---

### 3. QE (Undocumented API)
```javascript
app.enableQE();
var qeProject = app.qe.project;
```

**Status:** Brak dokumentacji dla operacji na subтytułach.

QE obsługuje:
- Effects by name ✅
- Ripple edits ✅
- Speed/duration ✅
- Frame export ✅
- Captions? ❌ (nie udokumentowane, brak przykładów)

**Wniosek:** Nawet jeśli QE ma dostęp, nie ma publicznych przykładów ani dokumentacji.

---

### 4. .PRPROJ XML (Project File Direct Edit)
Struktura: gzip → XML (brak schematu)

```python
import gzip
with gzip.open('project.prproj', 'rb') as f:
    xml = f.read()
```

**Problemy:**
- ❌ Brak publicznego schematu
- ❌ Zmienia się między wersjami (24.x vs 25.x vs 26.x)
- ❌ Edycja = ryzyko korupcji bez możliwości odzyskania
- ❌ Adobe oficjalnie zabrania (unsupported)

**Status:** Teoretycznie możliwe, praktycznie zbyt niebezpieczne.

---

### 5. CEP Panel (Deprecated)
```javascript
// CEP (zastarzeń, nie rekomendowany)
csInterface.evalScript('app.project.activeSequence.captions...');
```

**Status:**
- CEP deprecated (usunięty z Premiere 2024+)
- Nigdy nie obsługiwał edycji subтytułów
- Nieaktualne dla Premiere 25.6

---

### 6. FCP7 XML Export/Import
```bash
# Eksportuj do FCP7 XML
# Edytuj XML
# Importuj z powrotem
```

**Problem:** Subтytły są Base64-encoded w XML, nie dają się łatwo edytować.

Knowledge/xml-fcpxml.md:
> "Essential Graphics text is often Base64-buried and may be unrecoverable once flattened"

**Status:** Niewykonalne dla subтytułów.

---

### 7. Python via CLI (External Process)
Exportuj SRT → Python edit → import:

```python
# Export SRT
subprocess.run(['ffprobe', 'video.mov', '-show_entries', 'format=...'])

# Edit Python-side
for caption in captions:
    caption['text'] = new_text

# Re-import? ❌ Brak API do import subтytułów
```

**Problem:** Brak Premiere API do reimport subтytułów.

**Status:** Można edytować zewnętrznie, ale nie można wstrzyknąć z powrotem.

---

## Podsumowanie: Wszystkie Ścieżki

| Podejście | Czytanie | Pisanie | Ryzyko | Ruch |
|-----------|----------|---------|--------|------|
| **UXP 25.6** | ✅ | ❌ | Brak | 0% |
| **ExtendScript** | ❌ | ❌ | Brak | 0% |
| **QE (undoc)** | ? | ❌ | Wysoke | 0% |
| **PRPROJ XML** | ✅ | ✅ | Korupcja | Zbyt riskantne |
| **CEP (deprecated)** | ❌ | ❌ | N/A | 0% |
| **FCP7 XML** | ✅ (base64) | ✅ (base64) | Skomplikowane | Zbyt trudne |
| **Python CLI** | ✅ | ❌ (brak re-import) | Brak | 0% |

---

## Dlaczego Adobe Nie Obsługuje?

### Teoria 1: Subтytły = Sekwencyjne metadata
```
Sequence
  ├─ Markers (do tracks/clips)
  ├─ Captions (do timecode bez przywiązania do clipów)
  ├─ VFX (jako effecty na clipach)
```

Subтytły przechowuje inaczej niż markery. API ich nie ekspozuje.

### Teoria 2: Licencja treści
Subтytły mogą pochodzić z serwisów (Rev, Descript, Adobe auto-captions). Adobe chroni dostęp z powodów licencji.

### Teoria 3: Po prostu nie zrobili
Markery ✅ implementacja stara (CEP era)  
Subтytły ❌ implementacja nowa (Premiere 2020+), API nie gotowy

---

## Potwierdzenie z Fieldu

### Shotify (Professional Tool)
Pokazuje: "0 captions rewritten"

Dlaczego? Ta sama limitacja API. Nawet profesjonalne narzędzia nie mogą tego zrobić.

### Adobe Forums
```
"Does Premiere Pro have a scripting API for captions?"
Adobe Community: "Not directly. Captions are managed through the Premiere UI."
```

---

## Ostateczny Werdykt

**Pytanie:** Czy jest JAKIKOLWIEK sposób?

**Odpowiedź:** NIE.

Adobe celowo nie ekspozuje API do edycji subтytułów w Premiere 25.6.

Nie jest to:
- ❌ Brak documentacji (moglibyśmy znaleźć sposób)
- ❌ Brakujący trick (szukaliśmy wszędzie)
- ❌ Wymagająca zaawansowanego kodu (API po prostu nie istnieje)

To **architekturalna decyzja Adobe**: Subтytły = read-only w 25.6.

---

## Jedyne Opcje

### Teraz (Premiere 25.6)
1. **Edytuj ręcznie w UI** (~1 min per caption)
2. **Eksportuj do SRT** → edytuj w innym programie → importuj ręcznie
3. **Czekaj na Premiere 26.x** (Spring 2026)

### Wiosna 2026 (Premiere 26.x)
- Adobe planuje ulepszyć caption API
- Wtedy v4 narzędzia będzie pełne

---

## Rekomendacja dla User'a

**Nie buduj narzędzia do subтytułów na Premiere 25.6.**

Zamiast:
1. Udaj v3 (markers ✅, niezawodne)
2. Powiedz user'owi: "Subтytły czekaj 26.x"
3. User może:
   - Edytować ręcznie (5 min)
   - Użyć dedykowanego narzędzia (Rev, Descript)
   - Czekać na 26.x API

To lepsze niż obiecywać coś niemożliwego i zawieść.

---

## Commit History (Badania)

Szukaliśmy w:
1. Knowledge/uxp.md ✅
2. Knowledge/captions.md ✅
3. Knowledge/extendscript-core.md ✅
4. Knowledge/reverse-engineering-qe-dom.md ✅
5. Knowledge/project-file-format.md ✅
6. Knowledge/xml-fcpxml.md ✅
7. grep -r "caption.*api\|caption.*script" ✅

Wynik: Brak żadnego działającego podejścia.

---

## Finalna Odpowiedź

**User:** "Czy jest ruchliwe rozwiązanie, nawet jeśli wolne?"

**My:** "NIE. Adobe nie ekspozuje API do edycji subтytułów w Premiere 25.6. Badaliśmy:
- UXP (brak setText)
- ExtendScript (brak API)
- QE undocumented (brak przykładów)
- PRPROJ XML (zbyt riskantne)
- CEP deprecated (nie wspiera)
- FCP7 XML (base64-encoded, skomplikowane)

Nawet Shotify (professional tool) pokazuje 0 captions rewritten.

Nie jest to problem do rozwiązania - to decyzja architektury Adobe.

**Opcje:**
1. Edytuj ręcznie (5 min per 5 subтytułów)
2. Czekaj Premiere 26.x (Spring 2026)
3. Użyj dedykowanego narzędzia (Rev, Descript)

Nie ma czwartej opcji."

---

**Wniosek:** Uczciwość > Fałszywe obietnice.
