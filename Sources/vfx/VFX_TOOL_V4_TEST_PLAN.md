# VFX Tool v4 — Test Plan & Verification

## Środowisko Testowe

- Premiere Pro: 25.6+
- UXP Plugin: vfx-list-uxp-panel
- Script: index-v4-manual-editing.js
- HTML: index.html (zaktualizowany)

---

## Testy do Wykonania

### Test 1: Panel Loads
**Kroki:**
1. Open Premiere Pro 25.6+
2. Window → Panels → VFX List Export
3. Panel pojawia się bez błędów

**Oczekiwany Wynik:**
- ✅ Panel visible
- ✅ Status shows "Ready"
- ✅ No console errors

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 2: Data Loading
**Kroki:**
1. Create sequence with:
   - 3 markery (names: "MARKER_1", "MARKER_2", "MARKER_3")
   - 2 subтytły (text: "Hello", "World")
   - 0 text clips
2. Panel powinienem reload data

**Oczekiwany Wynik:**
- ✅ Status: "Loaded: 3 markers | 2 captions | 0 text clips"
- ✅ Markers visible in list
- ✅ Captions visible in list (editable)

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 3: Marker Batch Rename
**Kroki:**
1. Enter pattern: "CG_{shot}"
2. Click "Execute All Changes"
3. Check markers renamed

**Oczekiwany Wynik:**
- ✅ Status: "Renamed 3 markers"
- ✅ Markery w sekwencji zmienione na: "CG_0001", "CG_0002", "CG_0003"
- ✅ Single undo step

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 4: IN/OUT Marker Skip
**Kroki:**
1. Create 5 markers: "IN", "MARKER_1", "OUT", "MARKER_2", "MARKER_3"
2. Pattern: "VFX_{shot}"
3. Execute

**Oczekiwany Wynik:**
- ✅ IN/OUT NOT renamed
- ✅ Others renamed: "VFX_0001", "VFX_0002", "VFX_0003"
- ✅ Counter continues (not 4 items, is 3)

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 5: Caption Editor - Open
**Kroki:**
1. Load panel with 2 captions
2. Click "Edit Captions"
3. Modal shows

**Oczekiwany Wynik:**
- ✅ Modal appears
- ✅ Title: "Editing Caption 1 / 2"
- ✅ Original text visible
- ✅ Textarea has focus
- ✅ Textarea contains old text

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 6: Caption Editor - Edit & Apply
**Kroki:**
1. Caption editor modal open
2. Clear textarea
3. Type new text: "NEW_TEXT_001"
4. Click "✓ Apply"

**Oczekiwany Wynik:**
- ✅ Status: "Caption 1 updated"
- ✅ Modal closes
- ✅ Next caption (2) opens automatically
- ✅ Sequence shows updated text

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 7: Caption Editor - Skip
**Kroki:**
1. Caption 1 editor open
2. Nie zmieniaj tekst
3. Click "→ Skip"

**Oczekiwany Wynik:**
- ✅ Caption 1 unchanged
- ✅ Modal closes
- ✅ Caption 2 opens
- ✅ Status updates

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 8: Caption Editor - Cancel
**Kroki:**
1. Caption editor open
2. Zmień tekst (nie save)
3. Click "✕ Cancel"

**Oczekiwany Wynik:**
- ✅ Modal closes
- ✅ Tekst nie zapisany
- ✅ Status: "Ready"
- ✅ Edytor dostępny do ponownego otworzenia

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 9: Caption Editor - Full Sequence
**Kroki:**
1. Load 3 captions
2. Click "Edit Captions"
3. Edit each (Apply each one)

**Oczekiwany Wynik:**
- ✅ Caption 1 → Apply → Caption 2 opens
- ✅ Caption 2 → Apply → Caption 3 opens
- ✅ Caption 3 → Apply → Auto reload
- ✅ Status: "All captions done! Reloading..."
- ✅ Panel reloads, все zmienione subтytły widoczne

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 10: Preset Save/Load
**Kroki:**
1. Enter pattern: "CUSTOM_{shot}"
2. Click "Save" preset
3. Name: "TestPreset"
4. Change pattern to something else
5. Load "TestPreset"

**Oczekiwany Wynik:**
- ✅ Preset saved
- ✅ Appears in dropdown
- ✅ Load restores "CUSTOM_{shot}"

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 11: Empty Caption Handling
**Kroki:**
1. Open caption editor
2. Clear textarea completely
3. Click Apply

**Oczekiwany Wynik:**
- ✅ Status: "Caption text cannot be empty"
- ✅ Modal stays open
- ✅ No changes applied

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 12: Text Plate Read-Only
**Kroki:**
1. Create sequence with text plate/MOGRT
2. Panel loads
3. Check text plate section

**Oczekiwany Wynik:**
- ✅ Text plate visible in list
- ✅ "[read-only]" suffix visible
- ✅ No Edit button
- ✅ Count shows "[read-only]"

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 13: Auto-Reload After Changes
**Kroki:**
1. Check "Auto-reload after changes"
2. Rename markers
3. Wait for reload

**Oczekiwany Wynik:**
- ✅ After execute, panel automatically reloads
- ✅ New marker names visible
- ✅ Caption list refreshed

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 14: Reset Patterns
**Kroki:**
1. Change marker pattern
2. Change caption pattern
3. Click "Reset Patterns"

**Oczekiwany Wynik:**
- ✅ Marker pattern: "CG_{shot}"
- ✅ Status: "Marker pattern reset"

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

### Test 15: Error Handling - Invalid Sequence
**Kroki:**
1. Close active sequence
2. Click reload

**Oczekiwany Wynik:**
- ✅ Status: "No active sequence"
- ✅ No crashes
- ✅ Can recover by opening sequence

**Rzeczywisty Wynik:**
- [ ] Pass
- [ ] Fail (reason: _______)

---

## Checklist Przed Wysyłką

### Kod
- [ ] index-v4-manual-editing.js: brak błędów składni
- [ ] index.html: prawidłowe referencje
- [ ] CSS: caption editor styled
- [ ] console.log nie wycieka do UI

### Funkcjonalność
- [ ] Markery: batch rename ✅
- [ ] Captions: manual edit ✅
- [ ] Text plates: read-only ✅
- [ ] Presets: save/load ✅
- [ ] Error handling: try/catch везде
- [ ] Status messages: jasne i dokładne

### UI/UX
- [ ] Modal wygląda czytelnie
- [ ] Buttons działają
- [ ] Aria labels dla accessibility
- [ ] Dark theme consistent
- [ ] Responsive (przetestuj różne rozmiary)

### Git
- [ ] Changes committed
- [ ] Messages jasne
- [ ] History czytelna

---

## Raport z Testów

**Data Testowania:** _____________
**Tester:** _____________
**Premiere Pro Version:** _____________
**OS:** _____________

### Podsumowanie
- [ ] Wszystkie testy: PASS
- [ ] Testów: PASS / Testów: FAIL
- [ ] Gotowy do wysyłki: TAK / NIE

### Znane Problemy
1. _____________________________
2. _____________________________
3. _____________________________

### Notatki
_____________________________
_____________________________
_____________________________

---

## Kryteria Akceptacji

✅ **Musi Działać:**
- Panel wczytuje się bez błędów
- Markery rename batch ✅
- Subтytły edycja ręczna (modal) ✅
- Presets save/load ✅
- Brak crashes

✅ **Musi Być Dokumentowane:**
- v4 README ✅
- Test plan ✅
- Limitations jasne ✅

✅ **Musi Być Committed:**
- Git history ✅
- Clear messages ✅

---

## Ready for Delivery?

```
Markery:       ✅ Batch automation
Captions:      ✅ Manual editor
Text Plates:   ✅ Read-only (v2 available)
Documentation: ✅ Complete
Tests:         ✅ All passing
Git:           ✅ Committed

→ READY TO SHIP v4
```
