const ageInput = prompt('Age?');
const age = parseInt(ageInput, 10);

if (age < 12) {
  console.log('Child');
} else if (age < 18) {
  console.log('Teen');
} else if (age < 60) {
  console.log('Adult');
} else {
  console.log('Senior');
}

const digit = prompt('Digit?');
switch (digit) {
  case '1':
    console.log('!');
    break;
  case '2':
    console.log('@');
    break;
  case '3':
    console.log('#');
    break;
  case '4':
    console.log('$');
    break;
  case '5':
    console.log('%');
    break;
  case '6':
    console.log('^');
    break;
  case '7':
    console.log('&');
    break;
  case '8':
    console.log('*');
    break;
  case '9':
    console.log('(');
    break;
  case '0':
    console.log(')');
    break;
  default:
    console.log('Invalid');
    break;
}

const numInput = prompt('3-digit num?');
const [a, b, c] = numInput.split('');
if (a === b || b === c || a === c) {
  console.log('Match');
} else {
  console.log('Unique');
}

const yearInput = prompt('Year?');
const year = parseInt(yearInput, 10);
if (
  year % 400 === 0 ||
  (year % 4 === 0 && year % 100 !== 0)
) {
  console.log('Leap');
} else {
  console.log('Not leap');
}

const str = prompt('5-digit num?');
if (str[0] === str[4] && str[1] === str[3]) {
  console.log('Palindrome');
} else {
  console.log('Not pal');
}

const usdInput = prompt('USD?');
const usd = parseFloat(usdInput);
const currency = prompt('To EUR, UAH or AZN?').toUpperCase();
let result;

switch (currency) {
  case 'EUR':
    result = usd * 0.92;
    break;
  case 'UAH':
    result = usd * 36.7;
    break;
  case 'AZN':
    result = usd * 1.7;
    break;
  default:
    console.log('Unknown');
    throw new Error('Unknown currency');
}

console.log(`${result.toFixed(2)} ${currency}`);

const totalInput = prompt('Total?');
const total = parseFloat(totalInput);
let discount = 0;

if (total >= 500) {
  discount = 0.07;
} else if (total >= 300) {
  discount = 0.05;
} else if (total >= 200) {
  discount = 0.03;
}

const payable = total * (1 - discount);
console.log(`Pay: ${payable.toFixed(2)}`);

const circInput = prompt('Circ?');
const periInput = prompt('Peri?');
const circumference = parseFloat(circInput);
const perimeter = parseFloat(periInput);

const diameter = circumference / Math.PI;
const side = perimeter / 4;

if (diameter <= side) {
  console.log('Fit');
} else {
  console.log('No fit');
}

let score = 0;

const answer1 = prompt(
  '1. Capital of Ukraine? a) Kyiv b) Lviv c) Odesa'
).toLowerCase();
if (answer1 === 'a') {
  score += 2;
}

const answer2 = prompt(
  '2. Colors of flag? a) Blue and yellow b) Red and black c) Green and white'
).toLowerCase();
if (answer2 === 'a') {
  score += 2;
}

const answer3 = prompt(
  '3. Year of independence? a) 1991 b) 1994 c) 2000'
).toLowerCase();
if (answer3 === 'a') {
  score += 2;
}

console.log(`Score: ${score}`);

const dayInput = prompt('D?');
const monthInput = prompt('M?');
const year2Input = prompt('Y?');

let day = parseInt(dayInput, 10);
let month = parseInt(monthInput, 10);
let year2 = parseInt(year2Input, 10);

let daysInMonth;
if (month === 2) {
  if (year2 % 400 === 0 || (year2 % 4 === 0 && year2 % 100 !== 0)) {
    daysInMonth = 29;
  } else {
    daysInMonth = 28;
  }
} else if ([4, 6, 9, 11].includes(month)) {
  daysInMonth = 30;
} else {
  daysInMonth = 31;
}

if (day < daysInMonth) {
  day++;
} else {
  day = 1;
  if (month < 12) {
    month++;
  } else {
    month = 1;
    year2++;
  }
}

console.log(`Next: ${day}.${month}.${year2}`);
