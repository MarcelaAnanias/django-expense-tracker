const usernameField = document.querySelector("#usernameField");
const FeedBackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");
const usernameSucessOutput = document.querySelector(".usernameSucessOutput")
const passwordField = document.querySelector("#passwordField")
const showPassword = document.querySelector(".showPassword")
const registerBtn = document.querySelector(".register-btn")

const togglePasswordVisibility = () => {
    if (showPassword.textContent === "SHOW"){
        showPassword.textContent = "HIDE"
        passwordField.setAttribute("type", "text")
    } else {
        showPassword.textContent = "SHOW"
        passwordField.setAttribute("type", "password")
    }
};

showPassword.addEventListener("click", togglePasswordVisibility)

usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    
    usernameSucessOutput.style.display = 'block';
    usernameSucessOutput.textContent = `Checking the name, please wait...`

    usernameField.classList.remove("is-valid");
    usernameField.classList.remove("is-invalid");
    FeedBackArea.style.display = "none";

    if (usernameVal.length > 4) {
        fetch("/authentication/validate-username", {
          body: JSON.stringify({ username: usernameVal }),
          method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
            console.log('data', data)
            usernameSucessOutput.style.display = 'none';
            usernameField.classList.add("is-valid");
            if(data.username_error) {
                usernameField.classList.add("is-invalid");
                FeedBackArea.style.display = "block";
                FeedBackArea.innerHTML =`<p>${data.username_error}</p>`
                registerBtn.disabled = true;
            } else {
                registerBtn.removeAttribute("disabled");
            }
        });
    } else {
        usernameSucessOutput.style.display = 'none';
    }
});

emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;

    emailField.classList.remove("is-valid");
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = "none";

    if (emailVal.length > 0) {
        fetch("/authentication/validate-email", {
          body: JSON.stringify({ email: emailVal }),
          method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
            console.log('data', data)
            emailField.classList.add("is-valid");
            if(data.email_error) {
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display = "block";
                emailFeedBackArea.innerHTML =`<p>${data.email_error}</p>`
                registerBtn.disabled = true;
            } else {
                registerBtn.removeAttribute("disabled");
            }
        });
    }
});
    