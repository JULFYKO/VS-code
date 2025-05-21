let numbert1 = prompt("Enter a number");
if (numbert1 > 0) {
    console.log("positive");
}
else if (number < 0) {
    console.log("negative");
}
else {
    console.log("zero");
}
//----------------------------
let age = prompt("Enter your age");
if (age >= 0 && age <= 120) {
    console.log("ok");
}
else {
    console.log("not ok");
}

//----------------------------
let numbersforabs = prompt("Enter a number");
console.log(Math.abs(numbers));

//----------------------------
let hours = prompt("Enter hours");
let minutes = prompt("Enter minutes");
let seconds = prompt("Enter seconds");

if (hours >= 0 && hours < 24 && minutes >= 0 && minutes < 60 && seconds >= 0 && seconds < 60) {
    console.log("ok");
} else {
    console.log("not ok");
}
//----------------------------
let x = prompt("Enter x");
let y = prompt("Enter y");
if (x > 0 && y > 0) {
    console.log("1");
} else if (x < 0 && y > 0) {
    console.log("2");
} else if (x < 0 && y < 0) {
    console.log("3");
} else if (x > 0 && y < 0) {
    console.log("4");
} else if (x === 0 && y === 0) {
    console.log("0");
} else if (x === 0) {
    console.log("X");
} else {
    console.log("Y");
}
//----------------------------
let month = prompt("Enter month number");
switch (month) {
    case "1":
        console.log("January");
        break;
    case "2":
        console.log("February");
        break;
    case "3":
        console.log("March");
        break;
    case "4":
        console.log("April");
        break;
    case "5":
        console.log("May");
        break;
    case "6":
        console.log("June");
        break;
    case "7":
        console.log("July");
        break;
    case "8":
        console.log("August");
        break;
    case "9":
        console.log("September");
        break;
    case "10":
        console.log("October");
        break;
    case "11":
        console.log("November");
        break;
    case "12":
        console.log("December");
        break;
    default:
        console.log("Invalid month");
}
//----------------------------
let numbcalc = parseFloat(prompt("Enter first number"));
let numbcalc2 = parseFloat(prompt("Enter second number"));
let operator = prompt("Enter operator (+, -, *, /)");
let result;
switch (operator) {
    case "+":
        result = numbcalc + numbcalc2;
        break;
    case "-":
        result = numbcalc - numbcalc2;
        break;
    case "*":
        result = numbcalc * numbcalc2;
        break;
    case "/":
        result = numbcalc / numbcalc2;
        break;
    default:
        console.log("Invalid operator");
}
//-----------------------------
let numgr1 = parseFloat(prompt("Enter first number"));
let numgr2 = parseFloat(prompt("Enter second number"));
if (numgr1 > numgr2) {
    console.log("Greater number is: " + numgr1);
} else {
    console.log("Greater number is: " + num2);
}
//-----------------------------
let numberss = parseFloat(prompt("Enter a number"));
if (numberss % 5 === 0) {
    console.log(numberss + " is divisible by 5");
} else {
    console.log(numberss + " is not divisible by 5");
}
//-----------------------------
let planet = prompt("Enter the name of the planet");
if (planet === "Earth" || planet === "earth") {
    console.log("Hello, Earthling!");
} else {
    console.log("Hello, Alien!");
}