import React, { useEffect, useState } from "react";
import Modal from "react-bootstrap/Modal";
import Button from "react-bootstrap/Button";
import "bootstrap/dist/css/bootstrap.min.css";

import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

const styles = {
  app: {
    display: "grid",
    padding: 16,
    textAlign: "center",
    justifyContent: "center",
  },
  title: {
    fontSize: "32px",
    textAlign: "center",
  },
};

function App() {
  const [modalOpen, setModalOpen] = useState(true);

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
        <div style={styles.title}>Talk To Transformers</div>
        <div>
          <p>{transcript}</p>
        </div>
      </div>
      <Modal
        show={modalOpen}
        size="lg"
        aria-labelledby="contained-modal-title-vcenter"
        centered
      >
        <Modal.Header closeButton>
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
