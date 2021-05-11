import React, { useEffect, useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";
import { MenuItem, Select } from "@material-ui/core/";
import Chat from "./Chat.js";

import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

let prefix = "";
if (process.env.DEBUG) {
  prefix = "http://localhost:5000";
}

const styles = {
  app: {
    display: "flex",
    padding: 16,
  },
  body: {
    textAlign: "center",
    justifyContent: "center",
    width: "67%",
  },
  chat: {
    top: 0,
    right: 0,
    borderLeftStyle: "solid",
    height: "100%",
    width: "33%",
    position: "fixed",
    overflow: "scroll",
    display: "flex",
    flexDirection: "column",
  },
  dropdown: { margin: 8, width: "20%", textAlign: "initial" },
  title: {
    fontSize: "32px",
    textAlign: "center",
  },
};

const models = [
  {
    name: "Base",
    url: "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
  },
  {
    name: "Berkeley",
    url:
      "https://api-inference.huggingface.co/models/manav/dialogpt-medium-berkeley-reddit",
  },
];

function App() {
  const [modalOpen, setModalOpen] = useState(true);
  const [isListening, setIsListening] = useState(true);
  const [chats, setChats] = useState([]);
  const [modelURL, setModelURL] = useState(
    "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
  );
  const synth = window.speechSynthesis;

  const {
    transcript,
    interimTranscript,
    resetTranscript,
  } = useSpeechRecognition();

  useEffect(() => {
    if (interimTranscript === "" && transcript !== "") {
      const user_text = transcript;
      const url = `${prefix}/get_response_from_user_input`;
      console.log(`User: ${user_text}`);
      setIsListening(false);
      SpeechRecognition.abortListening();
      fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          inputs: {
            text: user_text,
            past_user_inputs: chats.filter((element, index) => {
              return index % 2 === 0;
            }),
            generated_responses: chats.filter((element, index) => {
              return index % 2 === 1;
            }),
          },
          url: modelURL,
        }),
      })
        .then((response) => {
          response.json().then((data) => {
            const { next_text } = data;
            console.log(`Bot: ${next_text}`);
            const utterThis = new SpeechSynthesisUtterance(next_text);
            utterThis.onend = () => {
              SpeechRecognition.startListening({ continuous: true });
              setIsListening(true);
            };
            synth.speak(utterThis);
            setChats([...chats, user_text, next_text]);
          });
        })
        .catch((error) => console.log(error));
      resetTranscript();
    }
  }, [transcript, interimTranscript]);

  useEffect(() => {
    var element = document.getElementById("chatBox");
    element.scrollTop = element.scrollHeight;
  }, [chats]);

  const onCloseModal = () => {
    setModalOpen(false);
    SpeechRecognition.startListening({ continuous: true });
  };

  return (
    <>
      <div style={styles.app}>
        <div style={styles.body}>
          <div style={styles.title}>Talk To Transformers</div>
          <div>
            Select Model:
            <Select
              style={styles.dropdown}
              autoWidth={true}
              value={modelURL}
              onChange={(e) => {
                setModelURL(e.target.value);
                setChats([]);
              }}
            >
              {models.map(({ name, url }, i) => (
                <MenuItem key={i} value={url}>
                  {name}
                </MenuItem>
              ))}
            </Select>
          </div>
          <div>
            <p>
              {transcript}
              {isListening ? "Listening..." : "Thinking..."}
            </p>
          </div>
        </div>
        <div id="chatBox" style={styles.chat}>
          {chats.map((chat, index) => {
            return <Chat key={index} index={index} message={chat} />;
          })}
        </div>
      </div>
      <Modal
        show={modalOpen}
        size="lg"
        aria-labelledby="contained-modal-title-vcenter"
        centered
      >
        <Modal.Header>
          <Modal.Title id="contained-modal-title-vcenter">Welcome!</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            Welcome to Talk to Transformers! Here you will be able to have a
            conversation with a GPT language model using your voice!
          </p>{" "}
          <p>
            We provide a variety of models finetuned on popular subreddits, so
            if you want to have a conversation about something in particular,
            you can select a differnt model in the dropdown.
          </p>{" "}
          <p>To get started, just click the button and begin talking!</p>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => onCloseModal()}>Start Conversation!</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default App;
