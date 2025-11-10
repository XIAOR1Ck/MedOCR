

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const snap = document.getElementById('snap');
const ctx = canvas.getContext('2d');
const container = document.getElementById('container')

const bufferHTML = `<div id="buffering" class="buffering">
            <div class="spinner"></div>
            <div class="buffering-text">Processing...</div>
        </div>`
// Request 720p camera stream (fallbacks handled automatically)
navigator.mediaDevices.getUserMedia({
  video: {
    width: { ideal: 600},
    height: { ideal: 600 },
    facingMode: "environment"
  }
})
.then(stream => {
  video.srcObject = stream;
})
.catch(err => {
  console.error("Camera error:", err.name, err.message);
  alert("Camera access failed: " + err.message);});

// Capture and send image to Flask
snap.addEventListener('click', () => {
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  const dataUrl = canvas.toDataURL('image/png');

  fetch('/uploadImage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: dataUrl })
  })
  .then(res => res.json())
  .then(data => {
            if (data.setid) {
                window.location.href = `/medicine/${data.setid}`
            }
        })

  container.innerHTML = bufferHTML;
 });

