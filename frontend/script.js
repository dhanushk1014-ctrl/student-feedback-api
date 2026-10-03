let editingId = null;

let isRegisterMode = false;


// ================= AUTH MODE =================

function switchAuth() {

    isRegisterMode = !isRegisterMode;

    const title = document.getElementById("authTitle");
    const button = document.getElementById("authButton");
    const switchText = document.getElementById("switchText");
    const switchButton = document.getElementById("switchButton");

    document.getElementById("authResult").innerText = "";

    if (isRegisterMode) {

        title.innerText = "Register";

        button.innerText = "Register";

        switchText.innerText = "Already have an account?";

        switchButton.innerText = "Login";

    } else {

        title.innerText = "Login";

        button.innerText = "Login";

        switchText.innerText = "Don't have an account?";

        switchButton.innerText = "Register";
    }
}


// ================= LOGIN / REGISTER =================

function handleAuth() {

    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value.trim();

    const result =
        document.getElementById("authResult");


    if (username === "" || password === "") {

        result.innerText =
            "Please enter username and password.";

        return;
    }


    // REGISTER

    if (isRegisterMode) {

        fetch("http://127.0.0.1:5000/api/register", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username: username,
                password: password
            })

        })

        .then(response => response.json())

        .then(data => {

            if (data.error) {

                result.innerText = data.error;

                return;
            }

            result.innerText =
                "Registration successful! Please login.";

            document.getElementById("username").value = "";
            document.getElementById("password").value = "";

            // Switch back to login

            isRegisterMode = true;

            switchAuth();

        })

        .catch(error => {

            console.error(error);

            result.innerText =
                "Unable to connect to server.";

        });

    }


    // LOGIN

    else {

        fetch("http://127.0.0.1:5000/api/login", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                username: username,
                password: password
            })

        })

        .then(response => response.json())

        .then(data => {

            if (data.error) {

                result.innerText = data.error;

                return;
            }


            // Save JWT token

            localStorage.setItem(
                "token",
                data.token
            );


            result.innerText =
                "Login successful!";


            // Hide authentication

            document.getElementById(
                "authCard"
            ).style.display = "none";


            // Show feedback

            document.getElementById(
                "feedbackSection"
            ).style.display = "block";


            loadFeedback();

        })

        .catch(error => {

            console.error(error);

            result.innerText =
                "Unable to connect to server.";

        });
    }
}


// ================= ADD FEEDBACK =================

function sendFeedback() {

    const name =
        document.getElementById("name").value.trim();

    const message =
        document.getElementById("message").value.trim();


    if (name === "" || message === "") {

        showMessage("Please fill all fields.");

        return;
    }


    if (editingId !== null) {

        updateFeedback(name, message);

        return;
    }


    const token =
        localStorage.getItem("token");


    fetch(
        "http://127.0.0.1:5000/api/feedback",
        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json",

                "Authorization":
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                name: name,
                message: message
            })
        }
    )

    .then(response => response.json())

    .then(data => {

        if (data.error) {

            showMessage(data.error);

            return;
        }

        showMessage(data.message);

        clearForm();

        loadFeedback();

    })

    .catch(error => {

        console.error(error);

        showMessage(
            "Something went wrong."
        );

    });
}


// ================= GET FEEDBACK =================

function loadFeedback() {

    const token =
        localStorage.getItem("token");


    fetch(
        "http://127.0.0.1:5000/api/feedback",
        {

            method: "GET",

            headers: {

                "Authorization":
                    `Bearer ${token}`
            }

        }
    )

    .then(response => response.json())

    .then(data => {

        if (data.error) {

            console.log(data.error);

            return;
        }


        const list =
            document.getElementById(
                "feedbackList"
            );


        list.innerHTML = "";


        const feedbackData =
            data.feedback;


        if (feedbackData.length === 0) {

            list.innerHTML =
                '<p class="empty">No feedback available.</p>';

            return;
        }


        feedbackData.forEach(feedback => {

            const item =
                document.createElement("div");


            item.className =
                "feedback-item";


            item.innerHTML = `

                <div class="feedback-name">
                    ${escapeHTML(feedback.name)}
                </div>

                <div class="feedback-message">
                    ${escapeHTML(feedback.message)}
                </div>

                <button
                    class="edit"
                    onclick="startEdit(${feedback.id})"
                >
                    Edit
                </button>

                <button
                    class="delete"
                    onclick="deleteFeedback(${feedback.id})"
                >
                    Delete
                </button>

            `;


            list.appendChild(item);

        });

    })

    .catch(error =>
        console.error(error)
    );
}


// ================= EDIT =================

function startEdit(id) {

    const token =
        localStorage.getItem("token");


    fetch(
        "http://127.0.0.1:5000/api/feedback",
        {

            headers: {

                "Authorization":
                    `Bearer ${token}`
            }

        }
    )

    .then(response => response.json())

    .then(data => {

        const feedback =
            data.feedback.find(
                item => item.id === id
            );


        if (!feedback) return;


        editingId = id;


        document.getElementById(
            "name"
        ).value = feedback.name;


        document.getElementById(
            "message"
        ).value = feedback.message;


        document.getElementById(
            "formTitle"
        ).innerText = "Edit Feedback";


        document.getElementById(
            "submitButton"
        ).innerText = "Update Feedback";


        document.getElementById(
            "cancelButton"
        ).style.display = "inline-block";


        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    });
}


// ================= UPDATE =================

function updateFeedback(name, message) {

    const token =
        localStorage.getItem("token");


    fetch(
        `http://127.0.0.1:5000/api/feedback/${editingId}`,
        {

            method: "PUT",

            headers: {

                "Content-Type":
                    "application/json",

                "Authorization":
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                name: name,
                message: message
            })

        }
    )

    .then(response => response.json())

    .then(data => {

        if (data.error) {

            showMessage(data.error);

            return;
        }


        showMessage(data.message);

        clearForm();

        loadFeedback();

    })

    .catch(error =>
        console.error(error)
    );
}


// ================= DELETE =================

function deleteFeedback(id) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this feedback?"
        );


    if (!confirmed) return;


    const token =
        localStorage.getItem("token");


    fetch(
        `http://127.0.0.1:5000/api/feedback/${id}`,
        {

            method: "DELETE",

            headers: {

                "Authorization":
                    `Bearer ${token}`
            }

        }
    )

    .then(response => response.json())

    .then(data => {

        if (data.error) {

            showMessage(data.error);

            return;
        }


        showMessage(data.message);

        loadFeedback();

    })

    .catch(error =>
        console.error(error)
    );
}


// ================= CANCEL EDIT =================

function cancelEdit() {

    clearForm();

}


// ================= CLEAR FORM =================

function clearForm() {

    document.getElementById(
        "name"
    ).value = "";


    document.getElementById(
        "message"
    ).value = "";


    editingId = null;


    document.getElementById(
        "formTitle"
    ).innerText = "Submit Feedback";


    document.getElementById(
        "submitButton"
    ).innerText = "Submit Feedback";


    document.getElementById(
        "cancelButton"
    ).style.display = "none";

}


// ================= LOGOUT =================

function logout() {

    localStorage.removeItem("token");


    document.getElementById(
        "feedbackSection"
    ).style.display = "none";


    document.getElementById(
        "authCard"
    ).style.display = "block";


    document.getElementById(
        "username"
    ).value = "";


    document.getElementById(
        "password"
    ).value = "";


    document.getElementById(
        "authResult"
    ).innerText =
        "Logged out successfully.";
}


// ================= MESSAGE =================

function showMessage(message) {

    document.getElementById(
        "result"
    ).innerText = message;

}


// ================= SECURITY =================

function escapeHTML(text) {

    const div =
        document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


// ================= AUTO LOGIN =================

window.onload = function () {

    const token =
        localStorage.getItem("token");


    if (token) {

        document.getElementById(
            "authCard"
        ).style.display = "none";


        document.getElementById(
            "feedbackSection"
        ).style.display = "block";


        loadFeedback();
    }

};
// ================= SENTIMENT PREDICTION =================

function predictSentiment() {

    const text =
        document.getElementById("sentimentText").value.trim();

    const result =
        document.getElementById("predictionResult");


    if (text === "") {

        result.innerText =
            "Please enter some text.";

        return;
    }


    const token =
        localStorage.getItem("token");


    fetch(
        "http://127.0.0.1:5000/api/predict",
        {

            method: "POST",

            headers: {

                "Content-Type":
                    "application/json",

                "Authorization":
                    `Bearer ${token}`
            },

            body: JSON.stringify({
                text: text
            })

        }
    )

    .then(response => response.json())

    .then(data => {

        if (data.error) {

            result.innerText =
                data.error;

            return;
        }


        result.innerText =
            "Prediction: " + data.prediction;

    })

    .catch(error => {

        console.error(error);

        result.innerText =
            "Unable to connect to prediction API.";

    });
}