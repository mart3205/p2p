// List of authorized users and passwords
const authorizedUsers = {
  admin: "admin",
  luzinfante: "holcim",
};
// Variable to store the logged-in username
let loggedInUsername = "";

document
  .getElementById("loginForm")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form submission

    // Retrieve entered username and password
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("errorMessage");

    // Hide error message initially
    errorMessage.style.display = "none";

    // Check if username and password match an authorized user
    if (authorizedUsers[username] === password) {
      loggedInUsername = username;
      // Redirect to new page if credentials are correct
      window.location.href = "/static/chatbot.html"; // Change to the URL of your desired page
    } else {
      // Display error message if credentials are incorrect
      errorMessage.style.display = "block";
    }
  });
