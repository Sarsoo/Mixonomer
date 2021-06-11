
// login function for validating login data

function handleLogin(){
    var username = document.forms['login']['username'].value;
    var password = document.forms['login']['password'].value;

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

    return true;
}

window.handleLogin = handleLogin;