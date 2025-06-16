function getRandomColor() {
    return '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0');
}
$('#addBlockBtn').on('click', function() {
    const color = getRandomColor();
    const $block = $('<div class="color-block"></div>').css('background', color);
    $('#blocksArea').append($block);
});
$('#blocksArea').on('click', '.color-block', function() {
    $(this).remove();
});

let lightIdx = 0;
const $lights = $('#trafficLight .light');
function updateTrafficLight(idx) {
    $lights.removeClass('active');
    $lights.each(function(i) {
        if (i === idx) {
            $(this).addClass('active');
        }
    });
}
updateTrafficLight(lightIdx);
$('#switchBtn').on('click', function() {
    lightIdx = (lightIdx + 1) % 3;
    updateTrafficLight(lightIdx);
});
