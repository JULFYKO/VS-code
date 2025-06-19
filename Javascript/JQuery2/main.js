// Створення Map з товарами (назва -> кількість)
const products = new Map([
    ["Apple", 5],
    ["Banana", 2],
    ["Orange", 8],
    ["Milk", 1],
    ["Bread", 4],
    ["Cheese", 7],
    ["Tomato", 3],
    ["Potato", 10],
    ["Eggs", 6],
    ["Juice", 2]
]);

products.forEach((qty, name) => {
    if (qty > 3) {
        console.log(`${name}: ${qty}`);
    }
});

const sorted = Array.from(products)
    .sort((a, b) => b[1] - a[1]);

sorted.forEach(([name, qty]) => {
    console.log(`${name}: ${qty}`);
});
