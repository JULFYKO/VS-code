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

const trafficWrap = document.createElement('div');
trafficWrap.className = 'traffic-wrap';

const traffic = document.createElement('div');
traffic.className = 'traffic';

const lights = [];
['red', 'yellow', 'green'].forEach(color => {
    const l = document.createElement('div');
    l.className = 'light';
    traffic.appendChild(l);
    lights.push(l);
});

const btn = document.createElement('button');
btn.textContent = 'NEXT';
btn.className = 'traffic-btn';

const btnWrap = document.createElement('div');
btnWrap.className = 'btn-wrap';
btnWrap.appendChild(btn);

trafficWrap.appendChild(traffic);
trafficWrap.appendChild(btnWrap);

document.body.appendChild(trafficWrap);

let current = 0;
function updateLights() {
    lights.forEach((l, i) => {
        l.className = 'light';
        if (i === current) {
            l.classList.add('active');
            if (i === 0) l.classList.add('red');
            if (i === 1) l.classList.add('yellow');
            if (i === 2) l.classList.add('green');
        }
    });
}
updateLights();

btn.onclick = function() {
    current = (current + 1) % 3;
    updateLights();
};
