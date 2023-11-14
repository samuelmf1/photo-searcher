$(document).ready(function () {

});

function callSearchApi(message) {
  return sdk.searchGet(
    {
      'q': message,
      "x-api-key": "QL6woWNLMu2i9JTLo3ZLJ5M2XezYT4I560cNrv2k",
      "sam": "QL6woWNLMu2i9JTLo3ZLJ5M2XezYT4I560cNrv2k"
    },
    {},
    {}
  );
}

document.getElementById("searchButton").addEventListener("click", function () {
  var msg = document.getElementById("searchInput").value;
  console.log('srch msg:',msg);

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
  console.log('tt', tags);
  var file = document.getElementById("imageInput").files[0];
  console.log('tf', file);
  file.constructor = () => file;

  sdk.uploadBucketObjectPut(
      {
        bucket: 'columbia-hw2-b2',
        object: file.name,
        'Content-Type': file.type,
        'x-amz-meta-customLabels': tags
      },
      file,
      {}
    )
    .then(res => {
      console.log(res)
    });
}

document.getElementById("uploadButton").addEventListener("click", function () {
  var msg = document.getElementById("uploadInput").value;
  if (msg === undefined || msg === "") {
    document.getElementById("uploadInput").innerHTML = 'Must enter tags';
  }
  console.log('msg:', typeof msg);
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