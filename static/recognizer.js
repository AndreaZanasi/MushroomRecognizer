const imageUpload = document.getElementById('image-upload');
const selectedImage = document.getElementById('selected-image-name');
const resultDiv = document.getElementById('result');
const loader = document.getElementById('loader');
const predictionText = document.getElementById('prediction-text');
const imageContainer = document.getElementById('image-gallery');
const fileNameElement = document.getElementById('file-name');
const filePredictionElement = document.getElementById('file-prediction');
const fileConfidenceElement = document.getElementById('file-confidence');
let images = [];
let currentIndex = 0;

imageUpload.addEventListener('change', function() {
    const fileName = this.files.length > 0 ? this.files[0].name : 'No file selected';
    selectedImage.innerText = fileName;
});

document.getElementById('upload-form').onsubmit = async function(event) {
    event.preventDefault();
    loader.style.display = 'block';
    predictionText.innerHTML = ''; 
    const formData = new FormData(this);
    const response = await fetch('/recognizer', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    const predictions = result.predictions;
    const confidences = result.confidences;
    predictionText.innerHTML = `<p>${predictions}: ${confidences}%</p>`;
    loader.style.display = 'none';
};

/**
 * Fetches previously analyzed images from the server.
 */
async function fetchImages() {
        try {
                const response = await fetch('/get_analyzed_images');
                const data = await response.json();
                console.log(data)
                images = data.images || [];
                if (images.length > 0) {
                        displayImage(0);
                } else {
                        console.log('No previously analyzed images found.');
                }
        } catch (error) {
                console.error('Error fetching previously analyzed images:', error);
        }
}

/**
 * Displays the image at the specified index along with its prediction and confidence.
 * @param {number} index - The index of the image to display.
 */
function displayImage(index) {
        if (images.length > 0) {
                const image = images[index];
                imageContainer.innerHTML = `<img src="/uploads/${image.filename}" alt="${image.filename}" class="gallery-image">`;
                fileNameElement.innerText = `File Name: ${image.filename}`;
                filePredictionElement.innerText = `Prediction: ${image.prediction}`;
                fileConfidenceElement.innerText = `Confidence: ${image.confidence}%`;
        }
}

/**
 * Scrolls through the images in the specified direction.
 * @param {number} direction - The direction to scroll (1 for next, -1 for previous).
 */
function scrollImages(direction) {
        if (images.length > 0) {
                currentIndex = (currentIndex + direction + images.length) % images.length;
                displayImage(currentIndex);
        }
}

fetchImages();