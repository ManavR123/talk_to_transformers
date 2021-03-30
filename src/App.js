import React from "react";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

function App() {
  const {
    transcript,
    interimTranscript,
    resetTranscript,
  } = useSpeechRecognition();

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

  return (
    <>
      <div>Talk To Transformers</div>
      <div>
        <button onClick={SpeechRecognition.startListening}>Start</button>
        <button onClick={SpeechRecognition.stopListening}>Stop</button>
        <button onClick={resetTranscript}>Reset</button>
        <p>{transcript}</p>
      </div>
    </>
  );
}

export default App;
