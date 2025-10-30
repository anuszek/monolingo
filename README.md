# Monolingo — uruchomienie lokalne (Windows / PowerShell)

To README opisuje krok po kroku jak uruchomić projekt Monolingo lokalnie na Windows (PowerShell). Zawiera instrukcje dla back-endu Flask (w katalogu `mati`) i front-endu (Vite + React). Zawiera też wskazówki dotyczące Tesseract OCR i zmiennych środowiskowych.

UWAGA: polecenia PowerShell są podane w blokach kodu z tagiem `powershell` — skopiuj i wklej w PowerShell (uruchom jako normalny użytkownik). Jeśli Twój system blokuje skrypty npm (`npm.ps1 cannot be loaded`), użyj `npm.cmd` zamiast `npm`.

## Wymagania

- Python 3.10+ (uruchamialne jako `py -3` lub `python`)
- Node.js + npm
- Systemowy Tesseract OCR (opcjonalnie, wymagany do OCR). Na Windows domyślnie instalator umieszcza go w `C:\Program Files\Tesseract-OCR`.

### Tesseract (szczegóły instalacji i weryfikacja)

Tesseract to natywny program (nie pakiet Pythona) potrzebny do funkcji OCR. Kilka praktycznych wskazówek dla Windows:

- Pobierz instalator dla Windows (zazwyczaj instalator EXE) ze strony projektu lub z zaufanego mirroru: https://github.com/tesseract-ocr/tesseract/releases
- Domyślna ścieżka instalacji to: `C:\Program Files\Tesseract-OCR\tesseract.exe`.

Weryfikacja z PowerShell (po instalacji):

```powershell
# sprawdzenie wersji (użyj pełnej ścieżki jeśli nie ma w PATH)
& 'C:\Program Files\Tesseract-OCR\tesseract.exe' --version

# lub, jeśli dodałeś Tesseract do PATH w tej sesji:
tesseract --version
```

Jeśli backend (Flask) nie znajduje Tesseract, masz trzy proste opcje:

1. Dodać Tesseract do PATH systemowego i zrestartować PowerShell/serwis:

```powershell
# tymczasowo w tej sesji PowerShell
$env:Path += ";C:\Program Files\Tesseract-OCR"

# trwale (ustawienie dla użytkownika) — wymaga ponownego uruchomienia sesji
setx PATH ("$env:Path;C:\Program Files\Tesseract-OCR")
```

2. Wskazać pełną ścieżkę w pliku `mati/.env` jako `TESSERACT_CMD` (najpewniejsze rozwiązanie):

```
TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

3. Upewnić się, że po zmianie ścieżki lub instalacji restartujesz backend (Flask), ponieważ serwer czyta `mati/.env` i sprawdza dostępność Tesseract przy starcie i podczas wywołań OCR.

Typowe błędy i wskazówki:

- Błąd typu `pytesseract.TesseractNotFoundError`: znaczy, że albo Tesseract nie jest zainstalowany, albo nie wskazano prawidłowej ścieżki w `TESSERACT_CMD`, albo proces uruchamiający Flask nie widzi zaktualizowanego PATH.
- Jeśli `tesseract --version` w PowerShell działa, ale Flask nadal nie widzi Tesseract — sprawdź, czy uruchamiasz Flask w tej samej sesji/shellu (restartuj proces backendu).
- Upewnij się, że masz odpowiednią wersję (64-bitowy instalator na 64-bitowym Windows).

Jeśli po tych krokach nadal masz problemy, uruchom diagnostykę:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/diag | ConvertTo-Json -Depth 5
```

W odpowiedzi zobaczysz, czy serwer widzi Tesseract oraz jaką ścieżkę używa — wklej tę odpowiedź jeśli chcesz, że pomogę dalej z debugowaniem.

## Szybkie kroki

1. Utwórz i aktywuj virtualenv dla backendu
2. Zainstaluj zależności Pythona
3. Ustaw zmienne środowiskowe (klucze, ścieżki)
4. Uruchom backend Flask
5. Zainstaluj zależności frontendu i uruchom Vite

Poniżej szczegóły krok po kroku.

---

## 1) Backend (Flask) — konfiguracja i uruchomienie

Otwórz PowerShell w katalogu repozytorium (gdzie znajduje się `mati/` i `package.json`).

Utwórz wirtualne środowisko i aktywuj je:

```powershell
# utworzenie venv (jeśli masz py launcher)
py -3 -m venv .venv
# aktywacja w PowerShell
.\.venv\Scripts\Activate.ps1
```

Zainstaluj zależności Pythona (plik z listą zależności dla backendu znajduje się w `mati/requirements_clean.txt`):

```powershell
pip install -r .\mati\requirements_clean.txt
```

Skonfiguruj zmienne środowiskowe potrzebne przez backend. Utwórz plik `mati/.env` (już jest przykładowy w repo) i ustaw co najmniej:

```
GROQ_API_KEY=your_groq_api_key_here
# jeśli Tesseract nie jest w PATH, wskaż jego pełną ścieżkę (Windows)
TESSERACT_CMD="C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# (opcjonalnie) inne zmienne jeśli używasz OpenAI itp
```

WAŻNE: Po zainstalowaniu Tesseract upewnij się, że restartujesz sesję PowerShell i restartujesz backend — proces Flask czyta `.env` przy starcie.

Uruchom backend:

```powershell
py -3 .\mati\app.py
# lub
python .\mati\app.py
```

Powinieneś zobaczyć log Flask i endpointy nasłuchujące na porcie 5000.

### Szybkie testy backendu

- Diagnoza Tesseract:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/diag | ConvertTo-Json -Depth 5
```

- Prosty test czatu (POST JSON):

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/chat -Body (@{prompt='Hello'} | ConvertTo-Json) -ContentType 'application/json'
```

---

## 2) Frontend (Vite + React)

W osobnym oknie PowerShell (nie musi mieć aktywnego venv) uruchom:

```powershell
# jeżeli pierwszy raz
npm.cmd install
# a następnie
npm.cmd run dev
```

Jeśli `npm` działa bez problemów, zamiast `npm.cmd` możesz użyć `npm` bez sufiksu.

Domyślnie frontend oczekuje backendu pod adresem `http://localhost:5000`. Jeśli chcesz to zmienić, ustaw w pliku `.env` w katalogu głównym repo (dla Vite) zmienną:

```
VITE_API_URL=http://127.0.0.1:5000
```

---

## 3) Testowanie OCR + TTS (z PowerShell / curl)

Przykładowe wysłanie pliku do endpointu OCR+TTS (curl):

```powershell
curl -X POST "http://127.0.0.1:5000/api/agent-ocr-tts" -F "file=@C:\path\to\your\image.jpg" -F "lang=en-US"
```

Przykład przy użyciu PowerShell `Invoke-WebRequest` (multipart):

```powershell
$form = @{ file = Get-Item 'C:\path\to\your\image.jpg' }
Invoke-WebRequest -Uri http://127.0.0.1:5000/api/agent-ocr-tts -Method Post -Form $form
```

Odpowiedź JSON zawiera póki co: `reply` (tekst odpowiedzi asystenta), `audio_b64` (base64 audio MP3), `ocr_text` (rozpoznany tekst) oraz opcjonalnie `ocr_debug`.

Jeśli chcesz zapisać audio z odpowiedzi do pliku (bash/curl):

```bash
# otrzymujesz audio_b64 w polu JSON.response.audio_b64
python - <<'PY'
import base64, json, sys
data = json.load(open('response.json'))
open('reply.mp3','wb').write(base64.b64decode(data['audio_b64']))
PY
```

---

## 4) Typowe problemy i wskazówki

- `python` / `py` nie działa: Upewnij się, że masz zainstalowanego Pythona i użyj `py -3` albo podaj pełną ścieżkę do interpretera. W PyCharm ustaw interpreter na `.venv`.
- `npm.ps1 cannot be loaded` w PowerShell: uruchom `npm.cmd` zamiast `npm`, lub zmień ExecutionPolicy (niezalecane globalnie).
- Tesseract zainstalowany, ale backend mówi że go nie widzi: upewnij się, że `TESSERACT_CMD` w `mati/.env` wskazuje na `C:\Program Files\Tesseract-OCR\tesseract.exe` i zrestartuj backend.
- Mikrofon: domyślnie został wyłączony w tej wersji (ikonka jest, ale klika pokazuje alert). Jeśli chcesz przywrócić funkcję rozpoznawania mowy, daj znać — dodam to opcjonalnie za flagą konfiguracyjną.

---

## 5) Pliki i ważne lokalizacje

- Backend Flask: `mati/app.py`
- Backend requirements: `mati/requirements_clean.txt`
- Frontend entry: `index.html`, `src/App.tsx`, `src/hooks/useVoice.tsx`
- Frontend API helper: `src/services/api.ts`

---

Jeżeli coś nie działa — wklej tu wycinki z terminala (błędy Flask lub `npm run dev`) oraz wynik `Invoke-RestMethod http://127.0.0.1:5000/api/diag`. Na podstawie logów pomogę dalej.

Powodzenia — jeśli chcesz, mogę automatycznie dodać przykładowy plik `mati/.env.example` z polami do uzupełnienia lub dodać skrótowy skrypt PowerShell `start.ps1`, który automatycznie przygotuje venv + zainstaluje zależności.

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
]);
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from "eslint-plugin-react-x";
import reactDom from "eslint-plugin-react-dom";

export default defineConfig([
  globalIgnores(["dist"]),
  {
    files: ["**/*.{ts,tsx}"],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs["recommended-typescript"],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.node.json", "./tsconfig.app.json"],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
]);
```
