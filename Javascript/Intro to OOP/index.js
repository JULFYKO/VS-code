class Selector {
    constructor(name) {
        this.name = name;
        this.styles = {};
    }
    addProperty(name, value) {
        this.styles[name] = value;
    }
    removeProperty(name) {
        delete this.styles[name];
    }
    getCSS() {
        const props = Object.entries(this.styles)
            .map(([k, v]) => `    ${k}: ${v};`)
            .join('\n');
        return `.${this.name} {\n${props}\n}`;
    }
}

class Button {
    constructor(width, height, text) {
        this.width = width;
        this.height = height;
        this.text = text;
    }
    showBtn() {
        document.write(
            `<button style="width:${this.width}px;height:${this.height}px;">${this.text}</button>`
        );
    }
}

class BootstrapButton extends Button {
    constructor(width, height, text, color) {
        super(width, height, text);
        this.color = color;
    }
    showBtn() {
        document.write(
            `<button style="width:${this.width}px;height:${this.height}px;background:${this.color};color:#fff;border:none;border-radius:4px;padding:6px 16px;">${this.text}</button>`
        );
    }
}
