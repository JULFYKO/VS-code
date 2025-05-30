document.getElementById('generate-btn').onclick = function () {
    const randomNumber = Math.floor(Math.random() * 101);
    document.getElementById('result').textContent = randomNumber;
};

const toggleBtn = document.getElementById('toggle-btn');
const toggleText = document.getElementById('toggle-text');
toggleBtn.onclick = function () {
    if (toggleText.style.display === 'none') {
        toggleText.style.display = '';
    } else {
        toggleText.style.display = 'none';
    }
};
 