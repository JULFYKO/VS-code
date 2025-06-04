class Car {
    constructor(model, year, color, isElectric) {
        this.model = model;
        this.year = year;
        this.color = color;
        this.isElectric = isElectric;
        
    }
    get isElectricStatus() {
        return this.isElectric ? "Yes" : "No";
    }
    toHTMLRow() {
        return `<tr>
                    <td>${this.model}</td>
                    <td>${this.year}</td>
                    <td>${this.color}</td>
                    <td>${this.isElectricStatus}</td>
                </tr>`;
    }
}

function capitalizeFirstLetter(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}