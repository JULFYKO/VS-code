const board = document.getElementById("game-board");
const scoreEl = document.getElementById("score");
const timerEl = document.getElementById("timer");
const restartBtn = document.getElementById("restart-btn");

const CARD_PAIRS = 8;
let cards = [];
let openCards = [];
let matchedCards = 0;
let score = 0;
let timer = 60;
let timerInterval = null;
let lockBoard = false;

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function generateCards() {
    const values = [];
    for (let i = 1; i <= CARD_PAIRS; i++) {
        values.push(i, i);
    }
    shuffle(values);
    cards = values.map((value, idx) => ({
        id: idx,
        value,
        matched: false
    }));
}

function renderBoard() {
    board.innerHTML = "";
    cards.forEach(card => {
        const cardDiv = document.createElement("div");
        cardDiv.className = "card";
        cardDiv.dataset.id = card.id;
        if (card.matched) cardDiv.classList.add("matched");
        if (openCards.includes(card.id) || card.matched) {
            cardDiv.classList.add("open");
            cardDiv.textContent = card.value;
        } else {
            cardDiv.textContent = "";
        }
        cardDiv.addEventListener("click", onCardClick);
        board.appendChild(cardDiv);
    });
}

function onCardClick(e) {
    if (lockBoard) return;
    const id = Number(e.currentTarget.dataset.id);
    const card = cards.find(c => c.id === id);
    if (card.matched || openCards.includes(id)) return;

    openCards.push(id);
    renderBoard();

    if (openCards.length === 2) {
        lockBoard = true;
        setTimeout(checkMatch, 800);
    }
}

function checkMatch() {
    const [id1, id2] = openCards;
    const card1 = cards.find(c => c.id === id1);
    const card2 = cards.find(c => c.id === id2);

    if (card1.value === card2.value) {
        card1.matched = true;
        card2.matched = true;
        matchedCards += 2;
        score += 10;
    } else {
        score = Math.max(0, score - 2);
    }
    openCards = [];
    updateScore();
    renderBoard();
    lockBoard = false;

    if (matchedCards === cards.length) {
        clearInterval(timerInterval);
        setTimeout(() => alert("Congratulations! You win! Your score: ${score}"), 100);
    }
}

function updateScore() {
    scoreEl.textContent = "Score: ${score}";
}

function updateTimer() {
    timerEl.textContent = "Time: ${timer}";
    if (timer <= 0) {
        clearInterval(timerInterval);
        lockBoard = true;
        setTimeout(() => alert("Time's up!"), 100);
    }
}

function startTimer() {
    timer = 60;
    updateTimer();
    timerInterval = setInterval(() => {
        timer--;
        updateTimer();
        if (timer <= 0) clearInterval(timerInterval);
    }, 1000);
}

function restartGame() {
    clearInterval(timerInterval);
    matchedCards = 0;
    score = 0;
    openCards = [];
    lockBoard = false;
    generateCards();
    renderBoard();
    updateScore();
    startTimer();
}

restartBtn.addEventListener("click", restartGame);

restartGame();