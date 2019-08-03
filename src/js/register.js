
function handleRegister(){
    var username = document.forms['register']['username'].value;
    var password = document.forms['register']['password'].value;
    var passwordAgain = document.forms['register']['password_again'].value;

    if (username.length == 0) {
        var status = document.getElementById("status");
        status.innerHTML = "enter username";
        status.style.display = "block";
        return false;
    }
    if (password.length == 0) {
        var status = document.getElementById("status");
        status.innerHTML = "enter password";
        status.style.display = "block";
        return false;
    }
    if (password != passwordAgain) {
        var status = document.getElementById("status");
        status.innerHTML = "password mismatch";
        status.style.display = "block";
        return false;
    }

    return true;
}

window.handleRegister = handleRegister;