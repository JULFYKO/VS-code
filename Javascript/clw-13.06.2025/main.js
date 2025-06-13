const API_KEY = "20f8bd72";
const API_URL = "https://www.omdbapi.com/";

const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const moviesDiv = document.getElementById("movies");
const paginationDiv = document.getElementById("pagination");

let currentPage = 1;
let currentQuery = "";

async function fetchMovies(query, page = 1) {
    moviesDiv.innerHTML = "Loading...";
    paginationDiv.innerHTML = "";
    const url = `${API_URL}?apikey=${API_KEY}&s=${encodeURIComponent(query)}&page=${page}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.Response === "True") {
        renderMovies(data.Search);
        renderPagination(page, Math.ceil(data.totalResults / 10));
    } else {
        moviesDiv.innerHTML = `<div>No results found.</div>`;
    }
}

function renderMovies(movies) {
    moviesDiv.innerHTML = "";
    movies.forEach(movie => {
        const card = document.createElement("div");
        card.className = "movie-card";
        card.innerHTML = `
            <img src="${movie.Poster !== "N/A" ? movie.Poster : "https://via.placeholder.com/200x300?text=No+Image"}" alt="${movie.Title}">
            <div class="movie-title">${movie.Title}</div>
            <div class="movie-year">${movie.Year}</div>
        `;
        moviesDiv.appendChild(card);
    });
}

function renderPagination(page, totalPages) {
    paginationDiv.innerHTML = "";
    if (totalPages <= 1) return;
    const prevBtn = document.createElement("button");
    prevBtn.textContent = "Prev";
    prevBtn.disabled = page === 1;
    prevBtn.onclick = () => changePage(page - 1);
    paginationDiv.appendChild(prevBtn);
    const pageInfo = document.createElement("span");
    pageInfo.textContent = `Page ${page} of ${totalPages}`;
    pageInfo.style.margin = "0 8px";
    paginationDiv.appendChild(pageInfo);
    const nextBtn = document.createElement("button");
    nextBtn.textContent = "Next";
    nextBtn.disabled = page === totalPages;
    nextBtn.onclick = () => changePage(page + 1);
    paginationDiv.appendChild(nextBtn);
}

function changePage(page) {
    currentPage = page;
    fetchMovies(currentQuery, currentPage);
}

searchBtn.onclick = () => {
    const query = searchInput.value.trim();
    if (!query) return;
    currentQuery = query;
    currentPage = 1;
    fetchMovies(currentQuery, currentPage);
};
