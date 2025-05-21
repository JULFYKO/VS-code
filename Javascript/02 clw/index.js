function MinofTwo(a, b) {
    return a < b ? a : b;
}

function numToPowerOf(num, power) {
    let result = 1;
    for (let i = 0; i < power; i++) {
        result *= num;
    }
    return result;
}

function calculatetwoNumbers(num1, num2, operator) {
    switch (operator) {
        case "+":
            return num1 + num2;
        case "-":
            return num1 - num2;
        case "*":
            return num1 * num2;
        case "/":
            return num1 / num2;
        default:
            return "Invalid operator";
    }
}
function isEven(num) {
    return num % 2 === 0;
}

function PrintMultiplicationTable(num) {
    for (let i = 1; i <= 10; i++) {
        console.log(`${num} * ${i} = ${num * i}`);
    }
}

console.log(MinofTwo(5, 10));
console.log(numToPowerOf(2, 3));
console.log(calculatetwoNumbers(5, 10, "+"));
console.log(isEven(4));
PrintMultiplicationTable(5);