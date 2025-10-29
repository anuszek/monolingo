import { useState, useRef } from "react";

// Maksymalna liczba rozmów do przechowania
const MAX_HISTORY_LENGTH = 10;

/**
 * Custom hook do zarządzania historią konwersacji.
 * Przechowuje listę ostatnich wiadomości (do 10) oraz
 * śledzi, która z nich jest aktualnie wybrana.
 */
export const useConversationHistory = () => {
  // Stan przechowujący listę wiadomości (początkowo pustą)
  const [conversationItems, setConversationItems] = useState<string[]>([]);

  // Stan przechowujący indeks aktywnego czatu
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const messageIndexRef = useRef<number | null>(null);

  /**
   * Dodaje nową wiadomość do historii.
   * Nowa wiadomość jest dodawana na początek listy.
   * Lista jest przycinana do MAX_HISTORY_LENGTH.
   * @param newItem - Tekst nowej wiadomości
   */
  const addConversationItem = (newItem: string) => {
    // Nie dodawaj pustych wiadomości
    if (!newItem.trim()) return;

    setConversationItems((prevItems) => {
      // Dodaj nowy element na początek tablicy
      const updatedItems = [newItem, ...prevItems];

      // Zwróć tylko 10 ostatnich elementów
      return updatedItems.slice(0, MAX_HISTORY_LENGTH);
    });

    // Ustaw nowo dodany element (na indeksie 0) jako aktywny
    setActiveIndex(0);
  };

  /**
   * Ustawia aktywną konwersację na podstawie klikniętego indeksu.
   * @param index - Indeks klikniętego elementu listy
   */
  const selectConversation = (index: number, messageIndex?: number) => {
    setActiveIndex(index);
    if (messageIndex !== undefined) {
      messageIndexRef.current = messageIndex;
    }
  };
  const getSelectedMessageIndex = () => messageIndexRef.current;
  // Zwróć stan oraz funkcje do zarządzania nim
  return {
    conversationItems,
    addConversationItem,
    activeIndex,
    selectConversation,
    getSelectedMessageIndex,
  };
};
