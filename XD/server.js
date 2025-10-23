const express = require("express");
const fetch = require("node-fetch");
const cors = require("cors");
const multer = require("multer");
const { createWorker } = require("tesseract.js");
require("dotenv").config();

const app = express();
app.use(cors());
app.use(express.json());

const OPENAI_KEY = process.env.OPENAI_API_KEY;
if (!OPENAI_KEY) {
  console.warn("Brak OPENAI_API_KEY w .env");
}

app.post("/api/agent", async (req, res) => {
  const { message } = req.body || {};
  if (!message) return res.status(400).json({ error: "Brak pola message" });

  try {
    const payload = {
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "You are an English-language tutor for Polish speakers. Your primary responses should be in clear, simple English suitable for a learner. After replying in English, if the user's input contains mistakes, provide a short correction: show the corrected sentence and a brief explanation in Polish. Offer a short follow-up question to continue the conversation. If the user asks about pronunciation, give a phonetic hint (IPA or simple phonetics). Keep answers concise (2-4 sentences) unless the user requests more.",
        },
        { role: "user", content: message },
      ],
    };

    const r = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_KEY}`,
      },
      body: JSON.stringify(payload),
    });

    if (!r.ok) {
      const text = await r.text();
      return res.status(502).json({ error: "Błąd od OpenAI", detail: text });
    }

    const data = await r.json();
    const reply =
      data.choices &&
      data.choices[0] &&
      data.choices[0].message &&
      data.choices[0].message.content;
    res.json({ reply });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// endpoint który zwraca gotowe audio (TTS) po zapytaniu do chat modelu
app.post("/api/agent-tts", async (req, res) => {
  const { message, lang } = req.body || {};
  if (!message) return res.status(400).json({ error: "Brak pola message" });

  try {
    // 1) zapytaj chat API o odpowiedź tekstową
    // wybierz odpowiedni system prompt w zależności od requested lang
    let systemPrompt = "Jesteś pomocnym asystentem, odpowiadaj po polsku.";
    if (lang && lang.startsWith("en")) {
      systemPrompt = `You are an English-language tutor for Polish speakers. Your primary responses should be in clear, simple English suitable for a learner. After replying in English, if the user's input contains mistakes, provide a short correction: show the corrected sentence and a brief explanation in Polish. Offer a short follow-up question to continue the conversation. If the user asks about pronunciation, give a phonetic hint (IPA or simple phonetics). Keep answers concise (2-4 sentences) unless the user requests more.`;
    }

    const chatPayload = {
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: message },
      ],
    };

    const chatResp = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_KEY}`,
      },
      body: JSON.stringify(chatPayload),
    });

    if (!chatResp.ok) {
      const t = await chatResp.text();
      return res
        .status(502)
        .json({ error: "Błąd od OpenAI (chat)", detail: t });
    }

    const chatData = await chatResp.json();
    const reply =
      chatData.choices &&
      chatData.choices[0] &&
      chatData.choices[0].message &&
      chatData.choices[0].message.content;
    if (!reply)
      return res
        .status(500)
        .json({ error: "Brak odpowiedzi tekstowej od modelu" });

    // 2) wygeneruj audio z tekstu (TTS)
    // Użyjemy endpointu /v1/audio/speech (zakładając kompatybilne API OpenAI). Zwrócimy audio jako stream (audio/mpeg)
    const ttsPayload = {
      voice: "alloy",
      input: reply,
      format: "mp3",
    };

    const ttsResp = await fetch("https://api.openai.com/v1/audio/speech", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${OPENAI_KEY}`,
      },
      body: JSON.stringify(ttsPayload),
    });

    if (!ttsResp.ok) {
      const tt = await ttsResp.text();
      return res
        .status(502)
        .json({ error: "Błąd od OpenAI (tts)", detail: tt });
    }

    // przekaż mime type i stream do klienta
    res.setHeader("Content-Type", "audio/mpeg");
    // streamujemy odpowiedź bez parsowania
    ttsResp.body.pipe(res);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// OCR endpoint: przyjmuje obraz (multipart/form-data field 'image') i zwraca rozpoznany tekst
const upload = multer({ storage: multer.memoryStorage() });
app.post("/api/ocr", upload.single("image"), async (req, res) => {
  if (!req.file)
    return res.status(400).json({ error: "Brak pliku (pole image)" });
  try {
    const worker = createWorker();
    await worker.load();
    await worker.loadLanguage("eng+pol");
    await worker.initialize("eng+pol");
    // recognize from buffer
    const {
      data: { text },
    } = await worker.recognize(req.file.buffer);
    await worker.terminate();

    // jeśli klient dołączył flagę sendToAgent=true, od razu prześlij rozpoznany tekst do chat i zwróć także odpowiedź
    const { sendToAgent } = req.body || {};
    if (sendToAgent === "true" || sendToAgent === true) {
      // forward to chat completions (reuse logic from /api/agent)
      const message = text;
      const chatPayload = {
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content:
              "You are an English-language tutor for Polish speakers. Respond concisely.",
          },
          { role: "user", content: message },
        ],
      };
      const chatResp = await fetch(
        "https://api.openai.com/v1/chat/completions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${OPENAI_KEY}`,
          },
          body: JSON.stringify(chatPayload),
        }
      );
      if (!chatResp.ok) {
        const t = await chatResp.text();
        return res
          .status(502)
          .json({ error: "Błąd od OpenAI (chat)", detail: t });
      }
      const chatData = await chatResp.json();
      const reply =
        chatData.choices &&
        chatData.choices[0] &&
        chatData.choices[0].message &&
        chatData.choices[0].message.content;
      return res.json({ text, reply });
    }

    res.json({ text });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// statyczne pliki (opcjonalne) — udostępnij voice.html
app.use(express.static(__dirname));

const PORT = process.env.PORT || 5174;
app.listen(PORT, () =>
  console.log(`XD server listening on http://localhost:${PORT}`)
);
