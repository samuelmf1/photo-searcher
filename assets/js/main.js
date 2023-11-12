$(document).ready(function () {

});

function callSearchApi(message) {
  return sdk.searchGet({ q: message, "x-api-key": "Gccl6hy79F6dPVqPlRfAz1Jhai9uEqge3xS75Fkq",
  "myfirstkey": "Gccl6hy79F6dPVqPlRfAz1Jhai9uEqge3xS75Fkq"}, {}, {});
}

document.getElementById("searchButton").addEventListener("click", function () {
  var msg = document.getElementById("searchInput").value;

  displaySearchPhotos = document.getElementById("displaySearchPhotos");

  callSearchApi(msg)
    .then((response) => {
      console.log(response);
      displaySearchPhotos.innerHTML = response["data"];
    })
    .catch((error) => {
      console.log('an error occurred', error);
    });

})

function callUploadApi(tags) {
  var file = document.getElementById("imageInput").files[0];
  file.constructor = () => file;

  sdk.photosPut({ bucket: 'bucketb2', 'Content-Type': file.type, key: file.name, 'x-amz-meta-customLabels': tags }, file, {})
    .then(res => {
      console.log(res)
    });
}

document.getElementById("uploadButton").addEventListener("click", function () {
  var msg = document.getElementById("uploadInput").value;
  callUploadApi(msg);
})

function record() {

  var speech = true;
  window.SpeechRecognition = window.SpeechRecognition
    || window.webkitSpeechRecognition;

  const recognition = new SpeechRecognition();
  recognition.interimResults = true;
  const words = document.querySelector('.words');
  words.appendChild(p);

  recognition.addEventListener('result', e => {
    const transcript = Array.from(e.results)
      .map(result => result[0])
      .map(result => result.transcript)
      .join('')

    document.getElementById("searchInput").value = transcript;
    console.log(transcript);
  });


  if (speech == true) {
    recognition.start();
  }


}