$(document).ready(function () {
    $('.exposurefilenote.opencor').append(
        '<div class="popover">Please note that this option requires ' +
        '<a href="http://opencor.ws/downloads">OpenCOR</a> ' +
        'to be installed onto your computer and opened at least once.' +
        '</div>'
    );
    $('<style>').prop('type', 'text/css').html(
        '.exposurefilenote.opencor div a { ' +
        '    display: inline ! important; ' +
        '}' +
        '.exposurefilenote.opencor div { ' +
        '    display: none; position: absolute; padding: 8px; ' +
        '    background: white; width: 200px; top: auto; left: auto;' +
        '}' +
        '.exposurefilenote.opencor:hover div { ' +
        '    display: block; ' +
        '}').appendTo('head');
});
