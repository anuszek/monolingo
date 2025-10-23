import ImageIcon from "@mui/icons-material/Image";
import MicIcon from "@mui/icons-material/Mic";
import {
  AppBar,
  Avatar,
  Box,
  IconButton,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  TextField,
  Typography,
  Container,
} from "@mui/material";
import "./App.css";



function App() {
  const conversationItems = [
    "What was the weather yesterday?",
    "Translate this sentence.",
    "Write a short poem",
    "Explain a short poem",
    "Explain quantum physics",
    "Recipe for lasgana?",
    "Capital time in Tokyo?",
    "Current time in Tokyo?",
    "How does photosythsis work?",
    "Tell me joke",
  ];
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
                  className={`conversation-item ${index === 0 ? "active" : ""}`}
                >
                  <ListItemText primary={item} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
        <Box className="content">
          <Box className="chat-area"></Box>
          <Box className="input-container">
            <TextField
              className="prompt-input"
              placeholder="Message Monolingo..."
              variant="standard"
              InputProps={{
                disableUnderline: true,
              }}
              fullWidth
            />
            <Box className="input-actions">
              <IconButton className="icon-button" aria-label="voice input">
                <MicIcon />
              </IconButton>
              <IconButton className="icon-button" aria-label="attach file">
                <ImageIcon />
              </IconButton>
            </Box>
          </Box>
        </Box>
      </Container>
    </>
  );
}

export default App;
