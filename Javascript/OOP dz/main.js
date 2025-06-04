class Circle{
    radius;
    get radius() {
        return this.radius;
    }
    set radius(value) {
        if (value <= 0) throw new Error('Radius must be positive');
        this.radius = value;
    }
    get diameter() {
        return this.radius * 2;
    }
    area() {
        return Math.PI * this.radius ** 2;
    }
    perimeter() {
        return 2 * Math.PI * this.radius;
    }
}

const circle = new Circle();
circle.radius = 5;
console.log(`Radius: ${circle.radius}`);
console.log(`Diameter: ${circle.diameter}`);
console.log(`Area: ${circle.area()}`);
console.log(`Perimeter: ${circle.perimeter()}`);


class HtmlElement {
    tagName;
    autoClosedTagName;
    textContent;
    arrayOfAttributes;
    arrayOfStyles;
    arrayOfInlineTags;
    setAttributes(attributes) {
        this.arrayOfAttributes = attributes;
    }
    setStyles(styles) {
        this.arrayOfStyles = styles;
    }
    addInlineElementToEnd(inlineElement) {
        if (!this.arrayOfInlineTags) {
            this.arrayOfInlineTags = [];
        }
        this.arrayOfInlineTags.push(inlineElement);
    }
    addInlineElementToStart(inlineElement) {
        if (!this.arrayOfInlineTags) {
            this.arrayOfInlineTags = [];
        }
        this.arrayOfInlineTags.unshift(inlineElement);
    }
    getHtml() {
        let attributesString = '';
        if (this.arrayOfAttributes) {
            attributesString = this.arrayOfAttributes.map(attr => ` ${attr.name}="${attr.value}"`).join('');
        }
        
        let stylesString = '';
        if (this.arrayOfStyles) {
            stylesString = ` style="${this.arrayOfStyles.map(style => `${style.name}:${style.value}`).join(';')}"`;
        }
        
        let inlineTagsString = '';
        if (this.arrayOfInlineTags) {
            inlineTagsString = this.arrayOfInlineTags.join('');
        }
        
        return `<${this.tagName}${attributesString}${stylesString}>${inlineTagsString}${this.textContent}</${this.tagName}>`;
    }
}
const div1 = new HtmlElement();
div1.tagName = "div";
div1.setStyles([{ name: "width", value: "300px" }, { name: "margin", value: "10px" }]);

const h3 = new HtmlElement();
h3.tagName = "h3";
h3.textContent = "What is Lorem Ipsum?";

const img = new HtmlElement();
img.tagName = "img";
img.setStyles([{ name: "width", value: "100%" }]);
img.setAttributes([
    { name: "src", value: "lipsum.jpg" },
    { name: "alt", value: "Lorem Ipsum" }
]);
img.textContent = "";m

const p = new HtmlElement();
p.tagName = "p";
p.setStyles([{ name: "text-align", value: "justify" }]);
p.textContent = `"Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."`;

const a = new HtmlElement();
a.tagName = "a";
a.setAttributes([
    { name: "href", value: "https://www.lipsum.com/" },
    { name: "target", value: "_blank" }
]);
a.textContent = "More...";

p.addInlineElementToEnd(a.getHtml());

div1.addInlineElementToEnd(h3.getHtml());
div1.addInlineElementToEnd(img.getHtml());
div1.addInlineElementToEnd(p.getHtml());

document.write(div1.getHtml());