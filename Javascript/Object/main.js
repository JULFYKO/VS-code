const Car ={
    brand: "Toyota",
    model: "Camry",
    year: 2020,
    averageSpeed: 120,
}
function showCarInfo(car) {
    console.log(`Brand: ${car.brand}`);
    console.log(`Model: ${car.model}`);
    console.log(`Year: ${car.year}`);
    console.log(`Average Speed: ${car.averageSpeed} km/h`);
}
function calculateTravelTime(distance, car) {
    let time = distance / car.averageSpeed;
    let breaks = Math.floor(time / 4);
    return time + breaks;
}




const fraction1 ={
    numerator:3,
    denominator:4,

}
const fraction2 ={
    numerator:2,
    denominator:5,
}
function addFraction(fraction1, fraction2) {
    const commonDenominator = fraction1.denominator * fraction2.denominator;
    const newNumerator1 = fraction1.numerator * fraction2.denominator;
    const newNumerator2 = fraction2.numerator * fraction1.denominator;
    const resultNumerator = newNumerator1 + newNumerator2;

    return {
        numerator: resultNumerator,
        denominator: commonDenominator
    };
}
function subtractFraction(fraction1, fraction2) {
    const commonDenominator = fraction1.denominator * fraction2.denominator;
    const newNumerator1 = fraction1.numerator * fraction2.denominator;
    const newNumerator2 = fraction2.numerator * fraction1.denominator;
    const resultNumerator = newNumerator1 - newNumerator2;

    return {
        numerator: resultNumerator,
        denominator: commonDenominator
    };
}
function multiplyFraction(fraction1, fraction2) {
    return {
        numerator: fraction1.numerator * fraction2.numerator,
        denominator: fraction1.denominator * fraction2.denominator
    };
}
function divideFraction(fraction1, fraction2) {
    return {
        numerator: fraction1.numerator * fraction2.denominator,
        denominator: fraction1.denominator * fraction2.numerator
    };
}
function reduceFraction(fraction) {
    function gcd(a, b) {
        return b === 0 ? a : gcd(b, a % b);
    }
    const divisor = gcd(fraction.numerator, fraction.denominator);
    return {
        numerator: fraction.numerator / divisor,
        denominator: fraction.denominator / divisor
    };
}



const Time = {
    hours: 2,
    minutes: 30,
    seconds: 45,
};
function showTimeInfo(time) {
    console.log(`Hours: ${time.hours}`);
    console.log(`Minutes: ${time.minutes}`);
    console.log(`Seconds: ${time.seconds}`);
}
function convertFromSecondsToTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    seconds %= 3600;
    const minutes = Math.floor(seconds / 60);
    seconds %= 60;
    return {
        hours: hours,
        minutes: minutes,
        seconds: seconds
    };
}
function convertFromMinutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    minutes %= 60;
    return {
        hours: hours,
        minutes: minutes,
        seconds: 0
    };
}
function convertFromHoursToTime(hours) {
    return {
        hours: hours,
        minutes: 0,
        seconds: 0
    };
}

showCarInfo(Car);
console.log(calculateTravelTime(960, Car));
console.log(addFraction(fraction1, fraction2));
console.log(subtractFraction(fraction1, fraction2));
console.log(multiplyFraction(fraction1, fraction2));
console.log(divideFraction(fraction1, fraction2));
console.log(reduceFraction(addFraction(fraction1, fraction2)));
showTimeInfo(Time);
console.log(convertFromSecondsToTime(10000));
console.log(convertFromMinutesToTime(150));
console.log(convertFromHoursToTime(3));
