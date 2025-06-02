let arr = [];
for (let i = 0; i <= 20; i++) {
    arr.push(Math.floor(Math.random() * 100));
}
console.log(arr);

arr.forEach((val, i) => console.log(`[${i}] ${val}`));

arr.forEach((val, i) => {
    if (val % 7 === 0) console.log(`Divisible by 7: [${i}] ${val}`);
});

let sortedArr = [...arr].sort((a, b) => b - a);
console.log("Sorted array:", sortedArr);

let modifiedArr = [...arr];
modifiedArr.fill(0, Math.floor(modifiedArr.length / 2));
console.log("Modified array:", modifiedArr);

let splicedArr = arr.slice(3);
console.log("Array:", splicedArr);

arr.forEach((val, i) => {
    arr.slice(i + 1).forEach((v, j) => {
        if (val === v) console.log(`Duplicate: [${i}] ${val} and [${i + 1 + j}] ${v}`);
    });
});

let Newarr = arr.slice(1, -1);
console.log("New array:", Newarr, "\nold array:", arr);

let sum = arr.filter(x => x % 2 === 0).length;
console.log("Sum:", sum);
