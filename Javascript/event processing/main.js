const field = document.createElement('div');
field.className = 'field';

const ball = document.createElement('div');
ball.className = 'ball';

field.appendChild(ball);
document.body.appendChild(field);

field.addEventListener('click', function(e) {
    const rect = field.getBoundingClientRect();
    let x = e.clientX - rect.left - ball.offsetWidth / 2;
    let y = e.clientY - rect.top - ball.offsetHeight / 2;
    x = Math.max(0, Math.min(x, field.clientWidth - ball.offsetWidth));
    y = Math.max(0, Math.min(y, field.clientHeight - ball.offsetHeight));
    ball.style.left = x + 'px';
    ball.style.top = y + 'px';
});

const traffic = document.createElement('div');
traffic.className = 'traffic';

const colors = ['red', 'yellow', 'green'];
const lights = colors.map(color => {
    const l = document.createElement('div');
    l.className = 'light';
    traffic.appendChild(l);
    return l;
});
lights[0].classList.add('active', 'red');

const btn = document.createElement('button');
btn.textContent = 'Next color';
btn.className = 'traffic-btn';

let current = 0;
btn.onclick = function() {
    lights.forEach(l => l.className = 'light');
    current = (current + 1) % 3;
    lights[current].classList.add('active', colors[current]);
};

document.body.appendChild(traffic);
document.body.appendChild(btn);
