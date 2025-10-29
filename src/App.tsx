import ImageIcon from "@mui/icons-material/Image";
import MicIcon from "@mui/icons-material/Mic";
import SendIcon from "@mui/icons-material/Send";
import {
  AppBar,
  Avatar,
  Box,
  CircularProgress,
  Container,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useRef, useState } from "react";
import "./App.css";
import { useConversationHistory } from "./hooks/chat";
import { useChat } from "./hooks/useChat";
import { useVoice } from "./hooks/useVoice";

function App() {
  const [inputValue, setInputValue] = useState("");
  const { messages, isLoading, addMessage } = useChat();
  const {
    conversationItems,
    addConversationItem,
    activeIndex,
    selectConversation,
    getSelectedMessageIndex,
  } = useConversationHistory();
  const chatAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatAreaRef.current) {
      chatAreaRef.current.scrollTop = chatAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const messageText = inputValue.trim();
    setInputValue("");

    // Add to conversation history
    addConversationItem(messageText);

    // Send to AI
    await addMessage(messageText);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  useEffect(() => {
    const selectedIndex = getSelectedMessageIndex();
    if (selectedIndex !== null) {
      const messageElements =
        chatAreaRef.current?.getElementsByClassName("message-paper");
      if (messageElements && messageElements[selectedIndex]) {
        messageElements[selectedIndex].scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }
    }
  }, [activeIndex]);
  const { status, startListening, sendImageToAgent } = useVoice();

  return (
    <>
      <AppBar className="header">
        <Box className="logo-container">
          <Avatar
            className="logo"
            src="/src/resources/cyclop.webp"
            alt="Monolingo"
            sx={{ width: 56, height: 56 }}
          />
          <Typography variant="h5" className="app-name">
            Monolingo
          </Typography>
        </Box>
      </AppBar>
      <Container className="main-container">
        <Box className="sidebar">
          <List className="conversation-history" disablePadding>
            {conversationItems.map((item, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton
                  className={`conversation-item ${
                    index === activeIndex ? "active" : ""
                  }`}
                  onClick={() => {
                    const messageIndex = messages.findIndex(
                      (msg) => msg.role === "user" && msg.content === item
                    );
                    selectConversation(index, messageIndex);
                  }}
                >
                  <ListItemText primary={item} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
        <Box className="content">
          <Box className="chat-area" ref={chatAreaRef}>
            {messages.length === 0 ? (
              <Box
                sx={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  height: "100%",
                  color: "#888",
                }}
              >
                <Typography variant="h6" gutterBottom>
                  Welcome to Monolingo!
                </Typography>
                <Typography variant="body2">
                  Start a conversation with the AI assistant
                </Typography>
              </Box>
            ) : (
              messages.map((msg, index) => (
                <Paper
                  key={index}
                  className="message-paper"
                  elevation={1}
                  sx={{
                    padding: 2,
                    marginBottom: 2,
                    backgroundColor:
                      msg.role === "user" ? "#e3f2fd" : "#f5f5f5",
                    maxWidth: "80%",
                    marginLeft: msg.role === "user" ? "auto" : 0,
                    marginRight: msg.role === "user" ? 0 : "auto",
                  }}
                >
                  <Typography
                    variant="caption"
                    sx={{
                      fontWeight: "bold",
                      display: "block",
                      marginBottom: 0.5,
                    }}
                  >
                    {msg.role === "user" ? "You" : "Monolingo"}
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                    {msg.content}
                  </Typography>
                </Paper>
              ))
            )}
          </Box>
          <Box className="input-container">
            <TextField
              className="prompt-input"
              placeholder="Message Monolingo..."
              variant="standard"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
              InputProps={{
                disableUnderline: true,
              }}
              fullWidth
            />
            <Box className="input-actions">
              <IconButton className="icon-button" aria-label="voice input">
                <MicIcon onClick={() => startListening()} />
              </IconButton>
              <IconButton className="icon-button" aria-label="attach file">
                <ImageIcon
                  onClick={() => {
                    // trigger file input elsewhere or open file picker
                    const el = document.createElement("input");
                    el.type = "file";
                    el.accept = "image/*";
                    el.onchange = (ev: any) => {
                      const f = el.files && el.files[0];
                      if (f) sendImageToAgent(f);
                    };
                    el.click();
                  }}
                />
              </IconButton>
              <Box
                sx={{ display: "flex", alignItems: "center", marginLeft: 1 }}
              >
                <Typography variant="caption">
                  {status === "idle" ? "" : status}
                </Typography>
              </Box>
              <IconButton
                className="icon-button"
                aria-label="send message"
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
              >
                <SendIcon />
              </IconButton>
            </Box>
          </Box>
        </Box>
      </Container>
    </>
  );
}

export default App;
