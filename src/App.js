import React, { useEffect, useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";

import Chat from "./Chat.js";

import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

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
  title: {
    fontSize: "32px",
    textAlign: "center",
  },
};

function App() {
  const [modalOpen, setModalOpen] = useState(true);
  const [chats, setChats] = useState([]);

  const {
    transcript,
    interimTranscript,
    resetTranscript,
  } = useSpeechRecognition();

  useEffect(() => {
    if (interimTranscript === "" && transcript !== "") {
      console.log(transcript);
      const url = "/get_response_from_user_input";
      fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          input_text: transcript,
        }),
      }).then((response) => {
        response.json().then((data) => {
          const { response, next_text } = data;
          if (response === "") {
            console.log("ERROR!");
          } else {
            console.log(next_text);
          }
          setChats([...chats, transcript, next_text]);
        });
      });
      resetTranscript();
    }
  }, [transcript, interimTranscript]);

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
            <p>{transcript}</p>
          </div>
        </div>
        <div style={styles.chat}>
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
            conversation with a GPT language model using your voice! To get
            started, just click the button and begin talking!
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={() => onCloseModal()}>Start Conversation!</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default App;
