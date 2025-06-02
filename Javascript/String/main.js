function countSpaces(str) {
    return str.split(' ').length - 1;
}

function FirstSymbolToUpperCase(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
function NumberWords(str) {
    return str.split(' ').length;
}
function ToAbreviation(str) {
    return str.split(' ').map(word => word.charAt(0).toUpperCase()).join('');
}
function IsPalindrome(str) {
    const lowerStr = str.toLowerCase();
    return lowerStr === lowerStr.split('').reverse().join('');
}
function InformationOfUrl(url) {
    const urlObj = new URL(url);
    return {
        protocol: urlObj.protocol,
        host: urlObj.host,
        pathname: urlObj.pathname
    };
}
console.log(countSpaces("Lorem ipsum dolor sit amet."));
console.log(FirstSymbolToUpperCase("lorem ipsum dolor sit amet.")); 
console.log(NumberWords("Lorem ipsum dolor sit amet."));
console.log(ToAbreviation("Lorem ipsum dolor sit amet."));
console.log(IsPalindrome("qwertyuioppoiuytrewq"));
console.log(IsPalindrome("Lorem ipsum dolor sit amet."));
console.log(InformationOfUrl("https://itstep.org/ua/about"));

