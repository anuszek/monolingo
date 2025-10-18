import "./App.css";
import Input from "@mui/material/Input";

function App() {
  return (
    <>
      <div className="sidebar"></div>
      <div className="content">
        <div className="title">
          <h1>Welcome to Monolingo</h1>
        </div>
        <div className="input-container">
          <Input
            className="prompt-input"
            placeholder="Enter a word or phrase"
            inputProps={{ "aria-label": "description" }}
            disableUnderline={true}
          />
          <button className="submit-button">Submit</button>
        </div>
      </div>
    </>
  );
}

export default App;
