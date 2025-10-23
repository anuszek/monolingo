# Voice agent (XD)

Prosty klient i serwer proxy do rozmowy z agentem OpenAI.

Kroki uruchomienia:

1. Przejdź do folderu `XD`:

   ```powershell
   cd XD
   ```

2. Zainstaluj zależności:

   ```powershell
   npm install
   ```

3. Skopiuj `.env.example` do `.env` i ustaw `OPENAI_API_KEY`.

4. Uruchom serwer:

   ```powershell
   npm start
   ```

5. Otwórz w przeglądarce:

   http://localhost:5174/voice.html

Uwaga: Web Speech API (rozpoznawanie mowy) działa najlepiej w Chrome/Edge. Serwer działa jako proxy — nie ujawniaj klucza w kliencie.

## Dodatek — TTS po stronie serwera

Ten przykład zawiera endpoint POST `/api/agent-tts` który:

- przyjmuje JSON { message }
- pyta model chat o odpowiedź tekstową
- generuje audio (mp3) za pomocą OpenAI Text-to-Speech i zwraca je jako stream

Jak testować:

1. Uruchom serwer (`npm install` i `npm start`).
2. Otwórz `http://localhost:5174/voice.html` w Chrome/Edge.
3. Naciśnij mikrofon i mów — odpowiedź zostanie wygenerowana na serwerze i odtworzona w przeglądarce.

Uwaga: Endpoint używa OpenAI API. Upewnij się, że `OPENAI_API_KEY` jest poprawnie ustawiony w `.env`. API TTS i nazwy parametrów mogą się zmieniać w zależności od wersji OpenAI — w razie błędów sprawdź odpowiedź serwera zwróconą w konsoli.
