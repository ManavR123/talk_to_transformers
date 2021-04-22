import React, { useCallback } from "react";
import Speech from "react-speech";
import SpeechRecognition from "react-speech-recognition";

const styles = {
  chat: {
    overflow: "wrap",
    maxWidth: "80%",
    padding: 8,
    borderRadius: "5px",
    margin: 8,
  },
  gpt: {
    backgroundColor: "lightgray",
    float: "left",
    textAlign: "left",
    alignSelf: "flex-start",
  },
  user: {
    backgroundColor: "lightblue",
    float: "right",
    textAlign: "right",
    alignSelf: "flex-end",
  },
};

function Chat(props) {
  const { index, message } = props;

  const speechRef = useCallback((node) => {
    if (index % 2 === 1) {
      SpeechRecognition.abortListening()
        .then(() => {
          node.play();
        })
        .then(() => {
          SpeechRecognition.startListening({ continuous: true });
        });
    }
  }, []);

  const extraStyle = index % 2 ? styles.gpt : styles.user;

  return (
    <div style={{ ...styles.chat, ...extraStyle }}>
      <Speech
        ref={speechRef}
        text={message}
        displayText={message}
        disabled={true}
      />
    </div>
  );
}

export default Chat;
