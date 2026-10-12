// Light/dark toggle. The <head> of every page sets data-theme before first
// paint; this only wires the button and keeps the label in sync.
(function () {
    var root = document.documentElement;
    var btn = document.querySelector(".theme-toggle");
    if (!btn) return;

    function read() {
        try { return localStorage.getItem("theme"); } catch (e) { return null; }
    }

    function sync() {
        var dark = root.getAttribute("data-theme") === "dark";
        btn.setAttribute("aria-label", dark ? "Switch to light theme" : "Switch to dark theme");
        btn.setAttribute("aria-pressed", String(dark));
    }

    btn.addEventListener("click", function () {
        var dark = root.getAttribute("data-theme") !== "dark";
        root.setAttribute("data-theme", dark ? "dark" : "light");
        try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch (e) { /* private mode */ }
        sync();
    });

    // keep following the system until the visitor makes a choice of their own
    var media = window.matchMedia("(prefers-color-scheme: dark)");
    var onSystemChange = function (e) {
        if (read()) return;
        root.setAttribute("data-theme", e.matches ? "dark" : "light");
        sync();
    };
    if (media.addEventListener) media.addEventListener("change", onSystemChange);
    else if (media.addListener) media.addListener(onSystemChange);

    sync();
})();
