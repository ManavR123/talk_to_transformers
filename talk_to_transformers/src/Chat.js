import React from "react";

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

  const extraStyle = index % 2 ? styles.gpt : styles.user;

  return <div style={{ ...styles.chat, ...extraStyle }}>{message}</div>;
}

export default Chat;
