const usernameField = document.querySelector("#usernameField");
const FeedBackArea = document.querySelector(".invalid-feedback");

usernameField.addEventListener("keyup", (e) => {
    console.log("777777", 7777777);
    const usernameVal = e.target.value;

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
            if(data.username_error) {
                usernameField.classList.add("is-invalid");
                FeedBackArea.style.display = "block";
                FeedBackArea.innerHTML =`<p>${data.username_error}</p>`
            }
        });
    }
});
    