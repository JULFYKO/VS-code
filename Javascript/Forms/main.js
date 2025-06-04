const addBtn = document.getElementById("addBtn");
const tableBody = document.getElementById("cars-list");
const clearBtn = document.getElementById("clearAllBtn");

const form = document.forms.carForm;
const modelInput = form.model;
const yearInput = form.year;
const colorInput = form.color;
const electricInput = form.electric;

addBtn.onclick = (event) => {
    event.preventDefault();

    if (
        !modelInput.value.trim() ||
        !yearInput.value ||
        !colorInput.value
    ) {
        alert("Please fill in all fields!");
        return;
    }

    const car = new Car(
        modelInput.value.trim(),
        yearInput.value,
        colorInput.value,
        electricInput.checked
    );

    tableBody.innerHTML += car.toHTMLRow();
    form.reset();
}

clearBtn.onclick = () => {
    tableBody.innerHTML = "";
}