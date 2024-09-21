// JavaScript for handling the file upload and preview
document.addEventListener('DOMContentLoaded', () => {
  // Get references to the DOM elements
  const uploadButton = document.getElementById('uploadButton');
  const imageUpload = document.getElementById('imageUpload');
  const previewImage = document.getElementById('preview');
  const getAnalysisButton = document.querySelector('.get-analysis');

  // Event listener for the upload button
  uploadButton.addEventListener('click', () => {
    imageUpload.click(); // Trigger file input click
  });

  // Event listener for file input change
  imageUpload.addEventListener('change', () => {
    const file = imageUpload.files[0];
    if (file) {
      const reader = new FileReader();

      // On successful file read
      reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block'; // Show the image preview
      };

      reader.readAsDataURL(file); // Read the file as data URL
    }
  });

  // Event listener for the Get Analysis button
  getAnalysisButton.addEventListener('click', () => {
    if (previewImage.src) {
      // Placeholder for analysis functionality
      // Typically, you would send the image to a server or AI model here
      // alert('Analysis functionality is not implemented yet.');
    } else {
      alert('Please upload an image first.');
    }
  });
});
