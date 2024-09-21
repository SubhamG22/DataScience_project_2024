function togglePasswordVisibility() {
    const passwordField = document.getElementById('password');
    const toggleEyeIcon = document.getElementById('toggle-eye');
    
    if (passwordField.type === "password") {
        passwordField.type = "text";
        toggleEyeIcon.classList.remove('fa-eye');
        toggleEyeIcon.classList.add('fa-eye-slash');
    } else {
        passwordField.type = "password";
        toggleEyeIcon.classList.remove('fa-eye-slash');
        toggleEyeIcon.classList.add('fa-eye');
    }
}


function togglePasswordVisibility(inputId, eyeIconId) {
    var passwordField = document.getElementById(inputId);
    var eyeIcon = document.getElementById(eyeIconId);

    if (passwordField.type === "password") {
        passwordField.type = "text";
        eyeIcon.classList.remove("fa-eye");
        eyeIcon.classList.add("fa-eye-slash");
    } else {
        passwordField.type = "password";
        eyeIcon.classList.remove("fa-eye-slash");
        eyeIcon.classList.add("fa-eye");
    }
}


 




