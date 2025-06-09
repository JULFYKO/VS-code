document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("github-form");
    const usernameInput = document.getElementById("username");
    const resultDiv = document.getElementById("result");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const username = usernameInput.value.trim();
        if (username) {
            try {
                const response = await fetch(`https://api.github.com/users/${username}`);
                if (!response.ok) throw new Error("User not found");
                const userData = await response.json();
                displayUserData(userData);
            } catch (error) {
                resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
            }
        } else {
            resultDiv.innerHTML = "<p>Please enter a username.</p>";
        }
    });

    function displayUserData(user) {
        const {
            avatar_url, login, name, html_url, blog, location, email, followers, following
        } = user;
        const country = location ? location.split(",").pop().trim() : "Not specified";
        resultDiv.innerHTML = `
            <img src="${avatar_url}" alt="${login}'s avatar" width="100">
            <h2>${name || login}</h2>
            <p><strong>Login:</strong> ${login}</p>
            <p><strong>Profile URL:</strong> <a href="${html_url}" target="_blank">${html_url}</a></p>
            <p><strong>Blog URL:</strong> ${blog ? `<a href="${blog}" target="_blank">${blog}</a>` : "Not specified"}</p>
            <p><strong>Location:</strong> ${location || "Not specified"}</p>
            <p><strong>Country:</strong> ${country}</p>
            <p><strong>Email:</strong> ${email || "Not specified"}</p>
            <p><strong>Followers:</strong> ${followers}</p>
            <p><strong>Following:</strong> ${following}</p>
        `;
    }
});