document.addEventListener('DOMContentLoaded', function () {
    const elements = document.querySelectorAll('.choices-single-default');
    elements.forEach(element => {
        new Choices(element, {
            searchEnabled: true,
            position: 'bottom' // Ensures the options dropdown opens downwards
        });
    });
});
