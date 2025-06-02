let arr = [];
for (let i = 0; i <= 20; i++) {
    arr.push(Math.floor(Math.random() * 100));
}
console.log(arr);

for (let i = 0; i < arr.length; i++) {
    console.log(`[${i}] ${arr[i]}`);
}

for (let i = 0; i < arr.length; i++) {
    if (arr[i] % 7 === 0) {
        console.log(`Divisible by 7: [${i}] ${arr[i]}`);
    }
}

arr.sort((a, b) => b - a);
console.log("Sorted array:", arr);

for (let i = Math.floor(arr.length / 2); i < arr.length; i++) {
    arr[i] = 0;
}
console.log("Modified array:", arr);

arr.splice(0, 3);
console.log("Array:", arr);

for (let i = 0; i < arr.length; i++) {
    for (let j = i + 1; j < arr.length; j++) {
        if (arr[i] === arr[j]) {
            console.log(`Duplicate: [${i}] ${arr[i]} and [${j}] ${arr[j]}`);
        }
    }
}


Newarr = arr.slice(1, -1);
console.log("New array:", Newarr,"\nold array:", arr);

let sum = 0;
for (let i = 0; i < arr.length; i++) {
    if (arr[i] % 2 === 0) {
        sum++;
    }
}
console.log("Sum:", sum);
