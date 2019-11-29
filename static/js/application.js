$(document).ready(function() {
    $('div.lazy-load').each(function(i, e) {
        $.get($(e).data('url'), function(data) {
            $(e).html(data);
        });
    });
});
