function updateImages() {
    const selectedTimestamp = document.getElementById('image-select').value;
    window.location.href = `/dashboard?timestamp=${selectedTimestamp}`;
}

function openimgmodel(imageSrc) {
    const imgmodel = document.getElementById('image-imgmodel');
    const imgmodelImage = document.getElementById('imgmodel-image');
    imgmodel.style.display = 'block';
    imgmodelImage.src = imageSrc;
}

function closeimgmodel() {
    const imgmodel = document.getElementById('image-imgmodel');
    imgmodel.style.display = 'none';
}

window.onclick = function(event) {
    const imgmodel = document.getElementById('image-imgmodel');
    if (event.target == imgmodel) {
        imgmodel.style.display = 'none';
    }
}