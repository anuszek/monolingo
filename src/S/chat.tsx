import { useState, useEffect } from "react";
import {
  Box,
  List,
  ListItem,
  ListItemText,
  TextField,
  IconButton,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

function Chat() {
  const [messages, setMessages] = useState<string[]>(() => {
    const saved = localStorage.getItem("chatMessages");
    return saved ? JSON.parse(saved) : [];
  });

  const [input, setInput] = useState("");

  // Zapis do localStorage po każdej zmianie
  useEffect(() => {
    localStorage.setItem("chatMessages", JSON.stringify(messages));
  }, [messages]);

  // Obsługa wysyłania wiadomości
  const handleSend = () => {
    if (!input.trim()) return;
    const newMessages = [...messages, input].slice(-10); // tylko 10 ostatnich
    setMessages(newMessages);
    setInput("");
  };

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        padding: 2,
      }}
    >
      {/* Lista wiadomości */}
      <List sx={{ flexGrow: 1, overflowY: "auto" }}>
        {messages.map((msg, index) => (
          <ListItem key={index}>
            <ListItemText primary={msg} />
          </ListItem>
        ))}
      </List>

      {/* Pole tekstowe */}
      <Box sx={{ display: "flex", gap: 1 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Napisz wiadomość..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <IconButton onClick={handleSend} color="primary">
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
}

export default Chat;
