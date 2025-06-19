document.querySelectorAll('#linksList a').forEach(a => {
    if (a.getAttribute('href').startsWith('http://') || a.getAttribute('href').startsWith('https://')) {
        a.style.borderBottom = '1.5px dashed #e67e22';
    }
});

document.querySelectorAll('.tree li').forEach(li => {
    if (li.querySelector('ul')) {
        li.style.cursor = 'pointer';
        li.addEventListener('click', function(e) {
            if (e.target === li) {
                const childUl = li.querySelector('ul');
                if (childUl) {
                    childUl.style.display = (childUl.style.display === 'none') ? '' : 'none';
                }
            }
        });
        li.querySelector('ul').style.display = 'none';
    }
});

let lastSelectedIdx = null;
const books = document.querySelectorAll('#booksList .book');
books.forEach((li, idx) => {
    li.addEventListener('click', function(e) {
        if (e.ctrlKey) {
            li.classList.toggle('ctrl-selected');
        } else if (e.shiftKey && lastSelectedIdx !== null) {
            const start = Math.min(lastSelectedIdx, idx);
            const end = Math.max(lastSelectedIdx, idx);
            for (let i = start; i <= end; i++) {
                books[i].classList.add('selected');
            }
        } else {
            books.forEach(b => b.classList.remove('selected', 'ctrl-selected'));
            li.classList.add('selected');
            lastSelectedIdx = idx;
        }
    });
});

document.querySelectorAll('#peopleTable th').forEach((th, colIdx) => {
    th.style.cursor = 'pointer';
    th.onclick = function() {
        const tbody = document.querySelector('#peopleTable tbody');
        const rows = Array.from(tbody.rows);
        const isNumber = !isNaN(rows[0].cells[colIdx].textContent.trim());
        rows.sort((a, b) => {
            let v1 = a.cells[colIdx].textContent.trim();
            let v2 = b.cells[colIdx].textContent.trim();
            if (isNumber) {
                return Number(v1) - Number(v2);
            } else {
                return v1.localeCompare(v2);
            }
        });
        if (th.dataset.sorted === 'asc') {
            rows.reverse();
            th.dataset.sorted = 'desc';
        } else {
            th.dataset.sorted = 'asc';
        }
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    };
});

const resizer = document.getElementById('resizer');
const block = document.getElementById('resizeBlock');
let isResizing = false, startX, startY, startW, startH;
resizer.addEventListener('mousedown', function(e) {
    isResizing = true;
    startX = e.clientX;
    startY = e.clientY;
    startW = block.offsetWidth;
    startH = block.offsetHeight;
    document.body.style.userSelect = 'none';
});
document.addEventListener('mousemove', function(e) {
    if (!isResizing) return;
    const newW = Math.max(80, startW + (e.clientX - startX));
    const newH = Math.max(40, startH + (e.clientY - startY));
    block.style.width = newW + 'px';
    block.style.height = newH + 'px';
});
document.addEventListener('mouseup', function() {
    isResizing = false;
    document.body.style.userSelect = '';
});
