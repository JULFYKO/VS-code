const valueDisplay = document.getElementById("valueDisplay");
document.getElementById("increase").onclick = () => {
  valueDisplay.value = parseInt(valueDisplay.value) + 1;
};
document.getElementById("decrease").onclick = () => {
  valueDisplay.value = parseInt(valueDisplay.value) - 1;
};

document.getElementById("addBlock").onclick = () => {
  const block = document.createElement("div");
  block.className = "color-block";
  block.style.backgroundColor = '#' + Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0');
  block.onclick = () => block.remove();
  document.getElementById("container").appendChild(block);
};

const text = document.getElementById("text");
document.querySelectorAll(".color-cell").forEach(cell => {
  cell.onclick = () => {
    text.style.color = cell.dataset.color;
  };
});
