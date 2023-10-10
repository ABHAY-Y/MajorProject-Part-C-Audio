let uploadButton = document.getElementById("upload-button");
let container = document.querySelector(".container");
let error = document.getElementById("error");
let audioDisplay = document.getElementById("audio-display");

const fileHandler = (file, name, type) => {
  if (type !== "audio/wav") {
    //File Type Error
    error.innerText = "Please upload an audio file";
    return false;
  }
  error.innerText = "";
  let reader = new FileReader();
  reader.readAsArrayBuffer(file);
  reader.onloadend = () => {
    let formdt = new FormData();
    formdt.append("audio", new Blob([reader.result], { type: "audio/wav" }));
    fetch('http://127.0.0.1:5000//audiointerpage',{
      method:'POST',
      body:formdt,
    })
    .then(res=>res.json())
    .then(value=>{alert('Transcribed Text: '+JSON.stringify(value.transcribed)+'\nPrediction: '+JSON.stringify(value.predicted))})
};
};

//Upload Button
uploadButton.addEventListener("change", () => {
  audioDisplay.innerHTML = "";
  Array.from(uploadButton.files).forEach((file) => {
    fileHandler(file, file.name, file.type);
  });
});

container.addEventListener(
  "dragenter",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.add("active");
  },
  false
);

container.addEventListener(
  "dragleave",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.remove("active");
  },
  false
);

container.addEventListener(
  "dragover",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.add("active");
  },
  false
);

container.addEventListener(
  "drop",
  (e) => {
    e.preventDefault();
    e.stopPropagation();
    container.classList.remove("active");
    let draggedData = e.dataTransfer;
    let files = draggedData.files;
    audioDisplay.innerHTML = "";
    Array.from(files).forEach((file) => {
      fileHandler(file, file.name, file.type);
    });
  },
  false
);

window.onload = () => {
  error.innerText = "";
};