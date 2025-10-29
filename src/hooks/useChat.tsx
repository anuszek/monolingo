import { useCallback, useState } from "react";
import type { Message } from "../services/api";
import { sendMessage } from "../services/api";

export const useChat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addMessage = useCallback(async (userMessage: string) => {
    if (!userMessage.trim()) return;

    setError(null);
    setIsLoading(true);

    // Add user message to the chat
    const newUserMessage: Message = {
      role: "user",
      content: userMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);

    try {
      // Send message to backend and get response
      const response = await sendMessage(userMessage);

      // Add AI response to the chat
      const aiMessage: Message = {
        role: "assistant",
        content: response.reply,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);

      // Add error message to chat
      const errorMsg: Message = {
        role: "assistant",
        content: `Sorry, there was an error: ${errorMessage}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addRawMessage = useCallback((message: Message) => {
    setMessages((prev) => [...prev, message]);
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    addMessage,
    clearChat,
    addRawMessage,
  };
};
