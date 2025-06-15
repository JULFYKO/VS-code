// Photo Tournament Organizer (JS version)
// Author: JulfyKo (ported to JS)

// --- Settings and State ---
const KEY_LEFT = 'd';
const KEY_RIGHT = 'f';
const KEY_OPTION3 = 'j';
const KEY_OPTION4 = 'k';
const KEY_UNDO = 'z';
const KEY_SHOW_TREE = 't';
const KEY_SETTINGS = 's';

const PHOTO_SIZE = 300;
const FINAL_PHOTO_SIZE = 500;
const AUTO_SAVE_KEY = 'photo_tournament_autosave';

let tournamentType = "Single Elimination";
let numChoices = 2;
let allowSkip = true;
let autoAdvance = false;
let shuffle = true;

// --- Default: Top N = всі фото ---
let topNEnabled = true;
let topNValue = 0; // 0 означає "всі фото"

let allPhotos = [];
let photoPaths = [];
let round = 1;
let matchNumber = 0;
let winners = [];
let currentChoices = [];
let history = [];
let matchLog = [];
let matchStartTime = 0;
let stats = {
    totalDecisionTime: 0,
    numDecisions: 0,
    numUndos: 0,
    selectionCounts: { [KEY_LEFT]: 0, [KEY_RIGHT]: 0, [KEY_OPTION3]: 0, [KEY_OPTION4]: 0 }
};

// --- DOM Elements ---
const fileInput = document.getElementById('fileInput');
const loadImagesBtn = document.getElementById('loadImagesBtn');
const imageGrid = document.getElementById('imageGrid');
const infoDiv = document.getElementById('info');
const progressBar = document.getElementById('progressBar');
const progressBarInner = document.getElementById('progressBarInner');
const choiceButtonsSpan = document.getElementById('choiceButtons');
const undoBtn = document.getElementById('undoBtn');
const treeBtn = document.getElementById('treeBtn');
const settingsBtn = document.getElementById('settingsBtn');
const manualSaveBtn = document.getElementById('manualSaveBtn');
const restartBtn = document.getElementById('restartBtn');
const logBtn = document.getElementById('logBtn');
const modal = document.getElementById('modal');
const tournamentTypeSpan = document.getElementById('tournamentType');
const topNInfoSpan = document.getElementById('topNInfo');
const timerSpan = document.getElementById('timer');
const themeToggleBtn = document.getElementById('themeToggleBtn');

// --- Utility Functions ---
function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
}

function saveState() {
    history.push({
        round, matchNumber, winners: [...winners], photoPaths: [...photoPaths],
        currentChoices: [...currentChoices], matchLog: [...matchLog], stats: JSON.parse(JSON.stringify(stats))
    });
}

function restoreState() {
    if (!history.length) return;
    const snap = history.pop();
    round = snap.round;
    matchNumber = snap.matchNumber;
    winners = snap.winners;
    photoPaths = snap.photoPaths;
    currentChoices = snap.currentChoices;
    matchLog = snap.matchLog;
    stats = snap.stats;
    displayCurrentChoices();
    updateInfo();
    updateProgress();
}

function autoSave() {
    const state = {
        round, matchNumber, winners, photoPaths, currentChoices, matchLog, stats,
        tournamentType, numChoices
    };
    localStorage.setItem(AUTO_SAVE_KEY, JSON.stringify(state));
}

function manualSave() {
    const state = {
        round, matchNumber, winners, photoPaths, currentChoices, matchLog, stats,
        tournamentType, numChoices
    };
    const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `manual_save_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

function restoreAutoSave() {
    const stateStr = localStorage.getItem(AUTO_SAVE_KEY);
    if (stateStr && confirm("A saved session was found. Restore?")) {
        try {
            const state = JSON.parse(stateStr);
            round = state.round || 1;
            matchNumber = state.matchNumber || 0;
            winners = state.winners || [];
            photoPaths = state.photoPaths || [];
            currentChoices = state.currentChoices || [];
            matchLog = state.matchLog || [];
            stats = state.stats || stats;
            tournamentType = state.tournamentType || tournamentType;
            numChoices = state.numChoices || numChoices;
            buildUI();
            alert("Session restored.");
        } catch (e) {
            alert("Failed to restore session: " + e);
        }
    }
}

// --- Theme toggle ---
themeToggleBtn.onclick = () => {
    const html = document.documentElement;
    const isLight = html.getAttribute('data-theme') === 'light';
    html.setAttribute('data-theme', isLight ? 'dark' : 'light');
    localStorage.setItem('theme', isLight ? 'dark' : 'light');
    themeToggleBtn.innerHTML = isLight
        ? '<i class="fa fa-moon"></i>'
        : '<i class="fa fa-sun"></i>';
};
(function () {
    const theme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', theme);
    themeToggleBtn.innerHTML = theme === 'light'
        ? '<i class="fa fa-sun"></i>'
        : '<i class="fa fa-moon"></i>';
})();

// --- Tournament Types ---
const TOURNAMENT_TYPES = [
    { value: "Single Elimination", label: "Single Elimination (Класика, короткий)" },
    { value: "Double Elimination", label: "Double Elimination (Два шанси, довший)" },
    { value: "Round Robin", label: "Round Robin (Кожен з кожним, найдовший)" },
    { value: "One Round", label: "One Round (Один тур, дуже короткий)" }
];

// --- Double Elimination State ---
let losersBracket = [];
let isLosersRound = false;

// --- UI Functions ---
function buildUI() {
    imageGrid.innerHTML = '';
    choiceButtonsSpan.innerHTML = '';

    // Якщо фото не завантажені — показати підказку
    if (!allPhotos.length) {
        const emptyDiv = document.createElement('div');
        emptyDiv.style.textAlign = 'center';
        emptyDiv.style.color = 'var(--color-text-secondary)';
        emptyDiv.style.fontSize = '1.2em';
        emptyDiv.style.padding = '48px 0';
        emptyDiv.innerHTML = '<i class="fa fa-image" style="font-size:2em;opacity:.3"></i><br>Завантажте фото для старту турніру';
        imageGrid.appendChild(emptyDiv);
        // Вимкнути кнопки вибору
        choiceButtonsSpan.innerHTML = '';
        return;
    }

    // Визначаємо currentChoices для першого показу, якщо ще не визначено
    if (photoPaths.length && currentChoices.length !== numChoices) {
        currentChoices = photoPaths.slice(0, numChoices);
    }

    // Image grid/cards
    for (let i = 0; i < numChoices; i++) {
        const card = document.createElement('figure');
        card.className = 'photo-card';
        card.style.transition = 'opacity .25s, transform .25s';
        card.style.opacity = currentChoices[i] ? '1' : '0.3';
        card.title = currentChoices[i]?.name || '';

        const img = document.createElement('img');
        img.className = 'tournament-img';
        img.alt = currentChoices[i]?.name || '';
        img.style.visibility = currentChoices[i] ? 'visible' : 'hidden';
        img.src = currentChoices[i]?.url || '';
        img.addEventListener('dblclick', () => viewOriginal(currentChoices[i]));
        img.title = "Двічі клікніть для перегляду оригіналу";
        card.appendChild(img);

        // Caption
        const caption = document.createElement('figcaption');
        caption.style.textAlign = 'center';
        caption.style.fontSize = '1em';
        caption.style.color = 'var(--color-text-secondary)';
        caption.style.padding = '4px 0 0 0';
        caption.textContent = currentChoices[i]?.name || '';
        card.appendChild(caption);

        // Actions
        const actions = document.createElement('div');
        actions.className = 'image-actions';
        const viewBtn = document.createElement('button');
        viewBtn.innerHTML = '<i class="fa fa-eye"></i> Оригінал';
        viewBtn.title = "Переглянути оригінал";
        viewBtn.onclick = () => viewOriginal(currentChoices[i]);
        viewBtn.disabled = !currentChoices[i];
        actions.appendChild(viewBtn);
        card.appendChild(actions);

        imageGrid.appendChild(card);
    }

    // Choice buttons
    let choices = [];
    if (numChoices === 2) {
        choices = [
            { text: `<i class="fa fa-arrow-left"></i> Ліве (D)`, key: KEY_LEFT },
            { text: `Праве (F) <i class="fa fa-arrow-right"></i>`, key: KEY_RIGHT }
        ];
    } else if (numChoices === 4) {
        choices = [
            { text: `Варіант 1 (D)`, key: KEY_LEFT },
            { text: `Варіант 2 (F)`, key: KEY_RIGHT },
            { text: `Варіант 3 (J)`, key: KEY_OPTION3 },
            { text: `Варіант 4 (K)`, key: KEY_OPTION4 }
        ];
    }
    // Кнопки активні лише якщо currentChoices.length === numChoices і всі currentChoices[i] існують
    const enableChoices = currentChoices.length === numChoices && currentChoices.every(Boolean);
    choices.forEach((c, idx) => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-primary';
        btn.innerHTML = c.text;
        btn.onclick = () => makeChoice(c.key);
        btn.title = "Гаряча клавіша: " + c.key.toUpperCase();
        btn.disabled = !enableChoices;
        choiceButtonsSpan.appendChild(btn);
    });
    displayCurrentChoices();
    updateInfo();
    updateProgress();
    updateTournamentInfo();
}

function updateTournamentInfo() {
    tournamentTypeSpan.textContent = `Тип: ${TOURNAMENT_TYPES.find(t => t.value === tournamentType)?.label || tournamentType}`;
    topNInfoSpan.textContent = topNEnabled ? `Top N: ${topNValue}` : '';
}

function updateInfo() {
    const totalMatches = Math.floor(photoPaths.length / numChoices);
    infoDiv.textContent = `Раунд ${round} | Матч ${matchNumber + 1} з ${totalMatches}`;
}

function updateProgress() {
    const totalMatches = Math.floor(photoPaths.length / numChoices);
    const percent = totalMatches ? (matchNumber / totalMatches) * 100 : 100;
    progressBarInner.style.width = percent + "%";
}

function displayCurrentChoices() {
    const cards = imageGrid.querySelectorAll('.photo-card');
    cards.forEach((card, i) => {
        const img = card.querySelector('img');
        const caption = card.querySelector('figcaption');
        if (currentChoices[i]) {
            img.src = currentChoices[i].url;
            img.style.visibility = 'visible';
            card.style.visibility = 'visible';
            card.style.opacity = '1';
            caption.textContent = currentChoices[i].name;
        } else {
            img.src = '';
            img.style.visibility = 'hidden';
            card.style.visibility = 'hidden';
            card.style.opacity = '0.3';
            caption.textContent = '';
        }
    });
}

// --- Winner/top N display ---
function showWinner() {
    imageGrid.innerHTML = '';
    infoDiv.textContent = topNEnabled && photoPaths.length > 1 ? "Top N Фото" : "Найкраще фото";
    let count = (topNEnabled && topNValue > 0) ? Math.min(topNValue, photoPaths.length) : photoPaths.length;
    if (!photoPaths.length) {
        imageGrid.innerHTML = '<div style="text-align:center;color:var(--color-text-secondary);padding:32px;">Немає фото для показу.</div>';
        return;
    }
    if (count > 1) {
        photoPaths.slice(0, count).forEach((p, i) => {
            if (!p) return;
            const card = document.createElement('figure');
            card.className = 'photo-card';
            const img = document.createElement('img');
            img.src = p.url;
            img.className = 'tournament-img';
            img.alt = p.name;
            img.title = `${i + 1} місце: ${p.name}`;
            card.appendChild(img);
            const caption = document.createElement('figcaption');
            caption.textContent = `${i + 1} місце: ${p.name}`;
            caption.style.textAlign = 'center';
            caption.style.fontWeight = 'bold';
            caption.style.color = 'var(--color-accent)';
            card.appendChild(caption);
            imageGrid.appendChild(card);
        });
    } else {
        const p = photoPaths[0];
        if (!p) {
            imageGrid.innerHTML = '<div style="text-align:center;color:var(--color-text-secondary);padding:32px;">Немає фото для показу.</div>';
            return;
        }
        const card = document.createElement('figure');
        card.className = 'photo-card';
        const img = document.createElement('img');
        img.src = p.url;
        img.className = 'tournament-img';
        img.alt = p.name;
        card.appendChild(img);
        const caption = document.createElement('figcaption');
        caption.textContent = p.name;
        caption.style.textAlign = 'center';
        caption.style.fontWeight = 'bold';
        caption.style.color = 'var(--color-accent)';
        card.appendChild(caption);
        imageGrid.appendChild(card);
    }
    showLogWindow();
}

function startTournament() {
    matchNumber = 0;
    winners = [];
    losersBracket = [];
    isLosersRound = false;
    currentChoices = [];
    if (shuffle && tournamentType !== "Round Robin" && tournamentType !== "One Round") {
        shuffleArray(photoPaths);
    }
    if (tournamentType === "Round Robin") {
        roundRobinInit();
    } else if (tournamentType === "One Round") {
        oneRoundInit();
    } else {
        nextMatch();
    }
}

function nextMatch() {
    if (tournamentType === "Single Elimination") {
        singleEliminationNext();
    } else if (tournamentType === "Double Elimination") {
        doubleEliminationNext();
    } else if (tournamentType === "Round Robin") {
        roundRobinNext();
    } else if (tournamentType === "One Round") {
        oneRoundNext();
    }
}

// --- Single Elimination (короткий) ---
function singleEliminationNext() {
    // ...перенести вашу логіку nextMatch() сюди...
    // ...existing code for single elimination from previous nextMatch...
    // ...замініть всі виклики nextMatch() на nextMatch() (бо тепер це роутер по типу турніру)
    // ...existing code...
    // (скопіюйте з вашого останнього nextMatch, але замініть setTimeout(nextMatch, 300) на setTimeout(() => nextMatch(), 300))
    // ...existing code...
}

// --- Double Elimination (довший) ---
function doubleEliminationNext() {
    // Основна сітка (winners), потім сітка "лузерів"
    let activeBracket = isLosersRound ? losersBracket : photoPaths;
    const total = activeBracket.length;
    const matchesThisRound = Math.floor(total / numChoices);
    const remainder = total % numChoices;

    if (matchNumber >= matchesThisRound) {
        // Бай
        if (remainder > 0 && matchNumber === matchesThisRound) {
            for (let i = total - remainder; i < total; i++) {
                winners.push(activeBracket[i]);
                matchLog.push({
                    round,
                    match: matchNumber + 1,
                    choices: [activeBracket[i].name],
                    winner: activeBracket[i].name,
                    decisionTime: 0,
                    bye: true,
                    bracket: isLosersRound ? "losers" : "winners"
                });
            }
        }
        // Якщо це winners, переходимо до losers
        if (!isLosersRound) {
            losersBracket = [];
            photoPaths.forEach((p, idx) => {
                if (!winners.includes(p)) losersBracket.push(p);
            });
            photoPaths = winners.slice();
            winners = [];
            matchNumber = 0;
            isLosersRound = true;
            if (photoPaths.length === 0 && losersBracket.length === 0) {
                showWinner();
                return;
            }
            doubleEliminationNext();
            return;
        } else {
            // Після losers раунду: об'єднати переможців winners і losers
            photoPaths = photoPaths.concat(winners);
            winners = [];
            matchNumber = 0;
            isLosersRound = false;
            if (photoPaths.length === 1 || (topNEnabled && photoPaths.length <= (topNValue > 0 ? topNValue : photoPaths.length))) {
                showWinner();
                return;
            }
            doubleEliminationNext();
            return;
        }
    }

    // Вибір фото для матчу
    const start = matchNumber * numChoices;
    currentChoices = [];
    for (let i = 0; i < numChoices; i++) {
        if (activeBracket[start + i]) currentChoices.push(activeBracket[start + i]);
    }
    if (currentChoices.length < numChoices) {
        currentChoices.forEach(photo => {
            winners.push(photo);
            matchLog.push({
                round,
                match: matchNumber + 1,
                choices: [photo.name],
                winner: photo.name,
                decisionTime: 0,
                bye: true,
                bracket: isLosersRound ? "losers" : "winners"
            });
        });
        matchNumber++;
        doubleEliminationNext();
        return;
    }
    displayCurrentChoices();
    updateInfo();
    updateProgress();
    updateTournamentInfo();
    matchNumber++;
}

// --- Round Robin (найдовший) ---
let roundRobinPairs = [];
let roundRobinResults = [];
let roundRobinIndex = 0;
function roundRobinInit() {
    roundRobinPairs = [];
    roundRobinResults = [];
    roundRobinIndex = 0;
    // Генеруємо всі унікальні пари
    for (let i = 0; i < photoPaths.length; i++) {
        for (let j = i + 1; j < photoPaths.length; j++) {
            roundRobinPairs.push([photoPaths[i], photoPaths[j]]);
        }
    }
    nextMatch();
}
function roundRobinNext() {
    if (roundRobinIndex >= roundRobinPairs.length) {
        // Підрахунок перемог
        let winCount = {};
        photoPaths.forEach(p => winCount[p.name] = 0);
        roundRobinResults.forEach(res => {
            winCount[res.winner.name]++;
        });
        // Сортуємо фото за кількістю перемог
        photoPaths.sort((a, b) => winCount[b.name] - winCount[a.name]);
        showWinner();
        return;
    }
    currentChoices = roundRobinPairs[roundRobinIndex];
    displayCurrentChoices();
    updateInfo();
    updateProgress();
    updateTournamentInfo();
    roundRobinIndex++;
}

// --- One Round (дуже короткий) ---
function oneRoundInit() {
    // Всі фото показати одразу, вибрати топ N
    showWinner();
}
function oneRoundNext() {
    // нічого не робити
}

// --- Modified makeChoice для підтримки різних типів ---
function makeChoice(key) {
    saveState();
    const decisionTime = 0;
    stats.totalDecisionTime += decisionTime;
    stats.numDecisions += 1;
    if (stats.selectionCounts[key] !== undefined) stats.selectionCounts[key] += 1;
    let idx = 0;
    if (numChoices === 2) idx = key === KEY_LEFT ? 0 : 1;
    else if (numChoices === 4) {
        const mapping = { [KEY_LEFT]: 0, [KEY_RIGHT]: 1, [KEY_OPTION3]: 2, [KEY_OPTION4]: 3 };
        idx = mapping[key] || 0;
    }
    const winnerPhoto = currentChoices[idx];
    if (!winnerPhoto) return;
    if (tournamentType === "Round Robin") {
        roundRobinResults.push({ winner: winnerPhoto, choices: currentChoices.map(p => p.name) });
        matchLog.push({
            round, match: roundRobinIndex, choices: currentChoices.map(p => p.name), winner: winnerPhoto.name, decisionTime
        });
        setTimeout(() => nextMatch(), 300);
    } else if (tournamentType === "Double Elimination") {
        matchLog.push({
            round, match: matchNumber, choices: currentChoices.map(p => p?.name || ''), winner: winnerPhoto.name, decisionTime,
            bracket: isLosersRound ? "losers" : "winners"
        });
        winners.push(winnerPhoto);
        setTimeout(() => nextMatch(), 300);
    } else {
        matchLog.push({
            round, match: matchNumber, choices: currentChoices.map(p => p?.name || ''), winner: winnerPhoto.name, decisionTime
        });
        winners.push(winnerPhoto);
        setTimeout(() => nextMatch(), 300);
    }
}

// --- Event Handlers ---
document.addEventListener('keydown', (e) => {
    // --- FIX: не реагувати якщо фокус у input, textarea, select або контент-редакторі ---
    const tag = (e.target && e.target.tagName) ? e.target.tagName.toLowerCase() : '';
    if (['input', 'textarea', 'select'].includes(tag) || e.target.isContentEditable) return;

    const key = e.key.toLowerCase();
    if (key === KEY_UNDO) {
        e.preventDefault();
        restoreState();
    }
    else if (key === KEY_SHOW_TREE) {
        e.preventDefault();
        showTree();
    }
    else if (key === KEY_SETTINGS) {
        e.preventDefault();
        openSettings();
    }
    else if (numChoices === 2 && (key === KEY_LEFT || key === KEY_RIGHT)) {
        e.preventDefault();
        makeChoice(key);
    }
    else if (numChoices === 4 && [KEY_LEFT, KEY_RIGHT, KEY_OPTION3, KEY_OPTION4].includes(key)) {
        e.preventDefault();
        makeChoice(key);
    }
});

undoBtn.onclick = restoreState;
treeBtn.onclick = showTree;
settingsBtn.onclick = openSettings;
manualSaveBtn.onclick = manualSave;
restartBtn.onclick = () => {
    if (confirm("Ви впевнені, що хочете перезапустити турнір? Прогрес буде втрачено.")) {
        restartTournament();
    }
};
logBtn.onclick = showLogWindow;

loadImagesBtn.onclick = () => fileInput.click();
fileInput.onchange = (e) => {
    allPhotos = [];
    photoPaths = [];
    const files = Array.from(e.target.files).filter(f => f.type.startsWith('image/'));
    if (files.length < 2) {
        alert("Not enough valid photos for the tournament.");
        return;
    }
    files.forEach(f => {
        const url = URL.createObjectURL(f);
        allPhotos.push({ name: f.name, url });
    });
    photoPaths = allPhotos.slice();
    round = 1;
    matchNumber = 0;
    winners = [];
    currentChoices = [];
    history = [];
    matchLog = [];
    stats = {
        totalDecisionTime: 0,
        numDecisions: 0,
        numUndos: 0,
        selectionCounts: { [KEY_LEFT]: 0, [KEY_RIGHT]: 0, [KEY_OPTION3]: 0, [KEY_OPTION4]: 0 }
    };
    buildUI();
    // --- FIX: Викликати nextMatch() замість startRound() ---
    matchNumber = 0;
    winners = [];
    currentChoices = [];
    startTournament();
    autoSave();
};

function restartTournament() {
    photoPaths = allPhotos.slice();
    round = 1;
    matchNumber = 0;
    winners = [];
    currentChoices = [];
    history = [];
    matchLog = [];
    stats = {
        totalDecisionTime: 0,
        numDecisions: 0,
        numUndos: 0,
        selectionCounts: { [KEY_LEFT]: 0, [KEY_RIGHT]: 0, [KEY_OPTION3]: 0, [KEY_OPTION4]: 0 }
    };
    buildUI();
    // --- Викликати nextMatch() замість startRound() ---
    matchNumber = 0;
    winners = [];
    currentChoices = [];
    startTournament();
    autoSave();
}

// --- Modal/Settings/Tree/Log ---
function showTree() {
    showModal("Tournament Tree", matchLog.map(e =>
        `R${e.round} M${e.match}: [${e.choices.join(', ')}] -> Winner: ${e.winner}`
    ).join('\n'));
}

function showLogWindow() {
    // Покажемо топ фото у вигляді картинок, а лог — лише по кнопці
    let html = `<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:18px;">`;
    let count = (topNEnabled && topNValue > 0) ? Math.min(topNValue, photoPaths.length) : photoPaths.length;
    photoPaths.slice(0, count).forEach((p, i) => {
        html += `
        <figure class="photo-card" style="margin:0;">
            <img src="${p.url}" class="tournament-img" alt="${p.name}" title="${i + 1} місце: ${p.name}">
            <figcaption style="text-align:center;font-weight:bold;color:var(--color-accent);padding:6px 0 0 0;">
                ${i + 1} місце: ${p.name}
            </figcaption>
        </figure>`;
    });
    html += `</div>
    <div style="text-align:center;margin-top:18px;">
        <button id="showLogBtn" class="btn" style="margin-top:8px;"><i class="fa fa-list"></i> Показати лог виборів</button>
    </div>`;

    showModal("Tournament Top", html, true);

    setTimeout(() => {
        const btn = document.getElementById('showLogBtn');
        if (btn) {
            btn.onclick = () => {
                showModal("Tournament Log",
                    matchLog.map(e =>
                        `Round ${e.round}, Match ${e.match}: [${e.choices.join(', ')}] -> Winner: ${e.winner}${e.bye ? " (bye)" : ""}`
                    ).join('\n')
                );
            };
        }
    }, 0);
}

// --- Settings Modal ---
function openSettings() {
    let allPhotosCount = allPhotos.length || 1;
    let maxTopN = allPhotosCount;
    let topNVal = topNEnabled ? (topNValue > 0 ? topNValue : allPhotosCount) : 1;

    showModal("Налаштування", `
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:center;">
            <label for="numChoicesInput"><i class="fa fa-th-large"></i> Кількість фото у матчі:</label>
            <input id="numChoicesInput" type="number" min="2" max="4" value="${numChoices}" style="width:60px;">
            
            <label for="tournamentTypeInput"><i class="fa fa-trophy"></i> Тип турніру:</label>
            <select id="tournamentTypeInput" style="width:100%;">
                ${TOURNAMENT_TYPES.map(t => `<option value="${t.value}"${tournamentType === t.value ? " selected" : ""}>${t.label}</option>`).join('')}
            </select>
            
            <label for="topNEnabledInput"><i class="fa fa-star"></i> Відображати Top N:</label>
            <span>
                <input id="topNEnabledInput" type="checkbox" ${topNEnabled ? "checked" : ""}>
                <label for="topNEnabledInput" style="font-size:.98em;">Увімкнути</label>
            </span>
            
            <label for="topNInput"><i class="fa fa-list-ol"></i> Top N (0 = всі):</label>
            <input id="topNInput" type="number" min="0" max="${maxTopN}" value="${topNVal}" style="width:60px;">
            
            <label for="shuffleInput"><i class="fa fa-random"></i> Перемішувати кожен раунд:</label>
            <input id="shuffleInput" type="checkbox" ${shuffle ? "checked" : ""}>
        </div>
        <div style="margin-top:18px;text-align:right;">
            <button id="saveSettingsBtn" class="btn btn-primary"><i class="fa fa-check"></i> Зберегти</button>
        </div>
        <div style="margin-top:10px;font-size:.95em;color:var(--color-text-secondary)">
            <i class="fa fa-info-circle"></i> 
            Single Elimination — класичний турнір на виліт.<br>
            Double Elimination — два шанси (довше).<br>
            Round Robin — кожен з кожним (найдовший).<br>
            One Round — один тур, всі фото одразу (дуже короткий).
        </div>
    `, true);

    const topNEnabledInput = document.getElementById('topNEnabledInput');
    const topNInput = document.getElementById('topNInput');
    function updateTopNState() {
        topNInput.disabled = !topNEnabledInput.checked;
        topNInput.style.opacity = topNEnabledInput.checked ? '1' : '.5';
    }
    topNEnabledInput.onchange = updateTopNState;
    updateTopNState();

    document.getElementById('saveSettingsBtn').onclick = () => {
        numChoices = parseInt(document.getElementById('numChoicesInput').value) || 2;
        shuffle = document.getElementById('shuffleInput').checked;
        tournamentType = document.getElementById('tournamentTypeInput').value;
        topNEnabled = topNEnabledInput.checked;
        let n = parseInt(topNInput.value) || 0;
        if (topNEnabled) {
            topNValue = n > 0 ? Math.min(n, allPhotos.length) : 0;
        } else {
            topNValue = 1;
        }
        buildUI();
        matchNumber = 0;
        winners = [];
        currentChoices = [];
        // --- Викликати старт турніру ---
        startTournament();
        closeModal();
    };
}

function viewOriginal(photo) {
    if (!photo) return;
    showModal("View Original", `<img src="${photo.url}" style="max-width:90vw;max-height:80vh;">`);
}

function showModal(title, content, isHTML) {
    modal.innerHTML = `<div class="modal-content">
        <h2>${title}</h2>
        <div>${isHTML ? content : `<pre>${content}</pre>`}</div>
        <button onclick="document.getElementById('modal').style.display='none'">Close</button>
    </div>`;
    modal.style.display = 'block';
}
function closeModal() { modal.style.display = 'none'; }

// --- Auto-restore on load ---
window.onload = restoreAutoSave;
function showModal(title, content, isHTML) {
    modal.innerHTML = `<div class="modal-content">
        <h2>${title}</h2>
        <div>${isHTML ? content : `<pre>${content}</pre>`}</div>
        <button onclick="document.getElementById('modal').style.display='none'">Close</button>
    </div>`;
    modal.style.display = 'block';
}
function closeModal() { modal.style.display = 'none'; }

// --- Auto-restore on load ---
window.onload = restoreAutoSave;
