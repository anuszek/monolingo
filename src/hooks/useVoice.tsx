import { useRef, useState } from "react";
import { agentOcrTts } from "../services/api";

export function useVoice() {
  // status used only for UI feedback (idle/thinking/speaking/error)
  const [status, setStatus] = useState<
    "idle" | "thinking" | "speaking" | "error"
  >("idle");
  const audioQueue = useRef<Blob[]>([]);
  const isPlaying = useRef(false);

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
      console.error("audio play error", e);
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
      return res;
    } catch (err) {
      console.error("agentOcrTts error", err);
      setStatus("error");
      throw err;
    }
  }

  return {
    status,
    sendImageToAgent,
  };
}
