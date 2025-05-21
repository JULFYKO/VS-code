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

function customDividing(num1, num2) {
    let result = 0;
    while (num1 >= num2) {
        num1 -= num2;
        result++;
    }
    return num1;
}

function Sum(num1, num2=0, num3=0, num4=0, num5=0) {
    return num1 + num2 + num3 + num4 + num5;
}

function Biggernumber(num1, num2=0, num3=0, num4=0, num5=0) {
    let max = num1;
    const nums = [num2, num3, num4, num5];
    for (let i = 0; i < nums.length; i++) {
        if (nums[i] > max) {
            max = nums[i];
        }
    }
    return max;
    
}
console.log(MinofTwo(5, 10));
console.log(numToPowerOf(2, 3));
console.log(calculatetwoNumbers(5, 10, "+"));
console.log(isEven(4));
PrintMultiplicationTable(5);
console.log(customDividing(10, 3));
console.log(Sum(1, 2, 3, 4));
console.log(Biggernumber(1, 2, 6, 4, 5));
