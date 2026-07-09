// ======================================
// SEARCH RECIPE
// ======================================

async function searchRecipe() {

    const recipe = document.getElementById("searchInput").value.trim();

    if (recipe === "") {
        alert("Please enter a recipe name.");
        return;
    }

    try {

        const response = await fetch(`/search?query=${encodeURIComponent(recipe)}`);

        const data = await response.json();

        if (!data.results || data.results.length === 0) {
            alert("Recipe not found.");
            return;
        }

        const recipeId = data.results[0].id;

        window.location.href = `/recipe?id=${recipeId}`;

    } catch (error) {

        console.error(error);
        alert("Unable to connect to the server.");

    }

}


// ======================================
// LOGIN
// ======================================

function loginUser() {

    let username = prompt("Enter your username:");

    if (!username || username.trim() === "") {
        alert("Login cancelled.");
        return;
    }

    localStorage.setItem("recipeUser", username);

    document.querySelector(".login-btn").innerHTML = "👤 " + username;

    alert("Welcome " + username + " 🎉");

}


// ======================================
// LOGOUT
// ======================================

function logoutUser() {

    localStorage.removeItem("recipeUser");

    document.querySelector(".login-btn").innerHTML = "Login";

    alert("Logged out successfully.");

}


// ======================================
// FAVORITES
// ======================================

async function viewFavorites() {

    const response = await fetch("/get_favorites");
    const favorites = await response.json();

    if (favorites.length === 0) {
        alert("No favorite recipes.");
        return;
    }

    let list = "❤️ Favorite Recipes\n\n";

    favorites.forEach((recipe, index) => {
        list += (index + 1) + ". " + recipe + "\n";
    });

    list += "\nEnter the number of the recipe to remove.";

    const choice = prompt(list);

    if (!choice) return;

    const index = parseInt(choice) - 1;

    if (index < 0 || index >= favorites.length) {
        alert("Invalid choice.");
        return;
    }

    const formData = new FormData();
    formData.append("recipe_name", favorites[index]);

    const result = await fetch("/remove_favorite", {
        method: "POST",
        body: formData
    });

    const data = await result.json();

    if (data.success) {
        alert("Recipe removed from Favorites.");
    }
}


// ======================================
// SHOPPING LIST
// ======================================

async function viewShoppingList() {

    const response = await fetch("/get_shopping");

    const shoppingList = await response.json();

    if (shoppingList.length === 0) {

        alert("Shopping list is empty.");

        return;

    }

    let list = "🛒 Shopping List\n\n";

    shoppingList.forEach((item, index) => {

        list += (index + 1) + ". " + item + "\n";

    });

    list += "\nEnter the number of the item to remove.";

    const choice = prompt(list);

    if (!choice) return;

    const index = parseInt(choice) - 1;

    if (index < 0 || index >= shoppingList.length) {

        alert("Invalid choice.");

        return;

    }

    const formData = new FormData();

    formData.append("item", shoppingList[index]);

    const result = await fetch("/remove_shopping", {
        method: "POST",
        body: formData
    });

    const data = await result.json();

    if (data.success) {

        alert("Item removed successfully 🗑️");

    }

}
// ======================================
// DARK MODE
// ======================================

function toggleDarkMode() {

    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {

        localStorage.setItem("theme", "dark");

    } else {

        localStorage.setItem("theme", "light");

    }

}


// ======================================
// LOAD SAVED THEME
// ======================================

window.addEventListener("load", () => {

    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {

        document.body.classList.add("dark-mode");

    }

});


// ======================================
// PRESS ENTER TO SEARCH
// ======================================

document.addEventListener("DOMContentLoaded", function () {

    const searchInput = document.getElementById("searchInput");

    if (searchInput) {

        searchInput.addEventListener("keypress", function (event) {

            if (event.key === "Enter") {

                searchRecipe();

            }

        });

    }

});


// ======================================
// RESTORE LOGIN
// ======================================

window.addEventListener("load", function () {

    const username = localStorage.getItem("recipeUser");

    const loginBtn = document.querySelector(".login-btn");

    if (username && loginBtn) {

        loginBtn.innerHTML = "👤 " + username;

    }

});


// ======================================
// LOGIN BUTTON
// ======================================

document.addEventListener("DOMContentLoaded", function () {

    const loginBtn = document.querySelector(".login-btn");

    if (!loginBtn) return;

    loginBtn.addEventListener("click", function () {

        const username = localStorage.getItem("recipeUser");

        if (username) {

            if (confirm("Logout from Recipe Basket?")) {

                logoutUser();

            }

        } else {

            loginUser();

        }

    });

});


// ======================================
// SCROLL TO TOP
// ======================================

window.onscroll = function () {

    const topBtn = document.getElementById("topBtn");

    if (!topBtn) return;

    if (document.body.scrollTop > 300 ||
        document.documentElement.scrollTop > 300) {

        topBtn.style.display = "block";

    } else {

        topBtn.style.display = "none";

    }

};

function topFunction() {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}


// ======================================
// WELCOME MESSAGE
// ======================================

window.addEventListener("load", function () {

    const username = localStorage.getItem("recipeUser");

    if (username) {

        console.log("Welcome back " + username);

    }

});


// ======================================
// APPLICATION READY
// ======================================

console.log("Recipe Basket Loaded Successfully");