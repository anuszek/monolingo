import { useEffect, useRef, useState } from "react";
import { agentTts, agentOcrTts } from "../services/api";

export function useVoice() {
  const [status, setStatus] = useState<
    "idle" | "listening" | "thinking" | "speaking" | "error"
  >("idle");
  const audioQueue = useRef<Blob[]>([]);
  const isPlaying = useRef(false);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // setup SpeechRecognition if available
    const SpeechRecognition =
      (window as any).SpeechRecognition ||
      (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const r = new SpeechRecognition();
      r.lang = "pl-PL";
      r.interimResults = false;
      r.maxAlternatives = 1;
      r.onresult = async (e: any) => {
        const text = Array.from(e.results)
          .map((r: any) => r[0].transcript)
          .join("");
        // send to TTS
        setStatus("thinking");
        try {
          const blob = await agentTts(text, "en-US");
          enqueueAudio(blob);
        } catch (err) {
          setStatus("error");
        }
      };
      r.onend = () => {
        // keep idle; UI controls will restart if needed
      };
      recognitionRef.current = r;
    }
  }, []);

  function startListening() {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
        setStatus("listening");
      } catch (e) {}
    }
  }

  function stopListening() {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
        setStatus("idle");
      } catch (e) {}
    }
  }

  function enqueueAudio(blob: Blob) {
    audioQueue.current.push(blob);
    if (!isPlaying.current) playNext();
  }

  function playNext() {
    const next = audioQueue.current.shift();
    if (!next) {
      isPlaying.current = false;
      setStatus("idle");
      return;
    }
    isPlaying.current = true;
    setStatus("speaking");
    const url = URL.createObjectURL(next);
    const a = new Audio(url);
    a.onended = () => {
      URL.revokeObjectURL(url);
      isPlaying.current = false;
      playNext();
    };
    a.play().catch((e) => {
      setStatus("error");
      isPlaying.current = false;
    });
  }

  async function sendImageToAgent(file: File, lang = "en-US") {
    const form = new FormData();
    form.append("file", file);
    form.append("lang", lang);
    setStatus("thinking");
    try {
      const res = await agentOcrTts(form);
      if (res.audio_b64) {
        const bytes = Uint8Array.from(atob(res.audio_b64), (c) =>
          c.charCodeAt(0)
        );
        const blob = new Blob([bytes], { type: "audio/mpeg" });
        enqueueAudio(blob);
      }
    } catch (err) {
      setStatus("error");
    }
  }

  return { status, startListening, stopListening, sendImageToAgent };
}
