import React, { useState, useEffect } from "react";
import VolumeMuteIcon from "@material-ui/icons/VolumeMute";
import VolumeDownIcon from "@material-ui/icons/VolumeDown";
import VolumeUpIcon from "@material-ui/icons/VolumeUp";

function AnimatedVolume() {
  const [count, setCount] = useState(0);

  useEffect(() => {
    setTimeout(() => {
      setCount(count + 1);
    }, 500);
  }, [count]);

  const icon = () => {
    if (count % 3 == 0) {
      return <VolumeMuteIcon fontSize="large" />;
    } else if (count % 3 == 1) {
      return <VolumeDownIcon fontSize="large" />;
    } else {
      return <VolumeUpIcon fontSize="large" />;
    }
  };

  return <>{icon()}</>;
}

export default AnimatedVolume;
