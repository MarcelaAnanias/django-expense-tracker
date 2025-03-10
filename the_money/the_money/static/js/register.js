const usernameField = document.querySelector("#usernameField");
const FeedBackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");
const usernameSucessOutput = document.querySelector(".usernameSucessOutput")

usernameField.addEventListener("keyup", (e) => {
    console.log("777777", 7777777);
    const usernameVal = e.target.value;
    
    usernameSucessOutput.style.display = 'block';
    usernameSucessOutput.textContent = `Checking ${usernameVal}`

    usernameField.classList.remove("is-invalid");
    FeedBackArea.style.display = "none";

    if (usernameVal.length > 0) {
        fetch("/authentication/validate-username", {
          body: JSON.stringify({ username: usernameVal }),
          method: "POST",
        })
            .then((res) => res.json())
            .then((data) => {
            console.log('data', data)
            usernameSucessOutput.style.display = 'none';
            if(data.username_error) {
                usernameField.classList.add("is-invalid");
                FeedBackArea.style.display = "block";
                FeedBackArea.innerHTML =`<p>${data.username_error}</p>`
            }
        });
    } else {
        usernameSucessOutput.style.display = 'none';
    }
});

emailField.addEventListener("keyup", (e) => {
    const emailVal = e.target.value;

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
            if(data.email_error) {
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display = "block";
                emailFeedBackArea.innerHTML =`<p>${data.email_error}</p>`
            }
        });
    }
});
    