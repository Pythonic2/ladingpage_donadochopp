(function () {
    function componentToHex(value) {
        var hex = Number(value).toString(16);
        return hex.length === 1 ? "0" + hex : hex;
    }

    function rgbToHex(value) {
        var match = String(value).match(/rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})/i);
        if (!match) {
            return "";
        }
        var r = Math.max(0, Math.min(255, parseInt(match[1], 10)));
        var g = Math.max(0, Math.min(255, parseInt(match[2], 10)));
        var b = Math.max(0, Math.min(255, parseInt(match[3], 10)));
        return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
    }

    function normalizeToHex(value) {
        value = String(value || "").trim();
        if (/^#[0-9a-f]{6}$/i.test(value)) {
            return value;
        }
        if (/^#[0-9a-f]{3}$/i.test(value)) {
            return "#" + value.slice(1).split("").map(function (char) {
                return char + char;
            }).join("");
        }
        return rgbToHex(value) || "#169b4f";
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".color-css-input").forEach(function (textInput) {
            var picker = document.createElement("input");
            picker.type = "color";
            picker.value = normalizeToHex(textInput.value);
            picker.style.marginLeft = "10px";
            picker.style.verticalAlign = "middle";
            picker.title = "Selecionar cor";

            picker.addEventListener("input", function () {
                textInput.value = picker.value;
            });

            textInput.addEventListener("input", function () {
                var hex = normalizeToHex(textInput.value);
                if (hex) {
                    picker.value = hex;
                }
            });

            textInput.insertAdjacentElement("afterend", picker);
        });
    });
}());
