function compareNumbers(a, b) {
  if (a < b) return -1;
  else if (a > b) return 1;
  else return 0;
}

function factorial(n) {
  if (n < 0) return null;
  let result = 1;
  for (let i = 2; i <= n; i++) {
    result *= i;
  }
  return result;
}

function combineDigits(d1, d2, d3) {
  return d1 * 100 + d2 * 10 + d3;
}

function area(length, width) {
  if (width === undefined) width = length;
  return length * width;
}

function isPerfect(n) {
  if (n < 2) return false;
  let sum = 1;
  for (let i = 2; i <= Math.sqrt(n); i++) {
    if (n % i === 0) {
      sum += i + (i === n / i ? 0 : n / i);
    }
  }
  return sum === n;
}

function listPerfect(min, max) {
  const results = [];
  for (let i = min; i <= max; i++) {
    if (isPerfect(i)) results.push(i);
  }
  return results;
}

function formatTime(hours, minutes = 0, seconds = 0) {
  const hh = String(hours).padStart(2, '0');
  const mm = String(minutes).padStart(2, '0');
  const ss = String(seconds).padStart(2, '0');
  return `${hh}:${mm}:${ss}`;
}

function timeToSeconds(hours, minutes = 0, seconds = 0) {
  return hours * 3600 + minutes * 60 + seconds;
}

function secondsToTime(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return formatTime(hours, minutes, seconds);
}

function dateDifference(h1, m1, s1, h2, m2, s2) {
  const t1 = timeToSeconds(h1, m1, s1);
  const t2 = timeToSeconds(h2, m2, s2);
  const diff = Math.abs(t2 - t1);
  return secondsToTime(diff);
}
console.log(compareNumbers(5, 10));
console.log(factorial(5));
console.log(combineDigits(1, 4, 9));
console.log(area(4, 5));
console.log(isPerfect(28));
console.log(listPerfect(1, 1000));
console.log(formatTime(2, 5, 7));
console.log(timeToSeconds(1, 1, 1));
console.log(secondsToTime(10000));
console.log(dateDifference(1, 1, 1, 2, 2, 2));
