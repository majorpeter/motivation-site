function periodicallyReload(e) {
    $.get($(e).data('url'), function(data) {
        $(e).fadeOut(800, function() {
            $(e).html(data);
            $(e).fadeIn(400);
        });
    });
}

$(document).ready(function() {
    $('div.lazy-load, div.lazy-load-periodic').each(function(i, e) {
        $.get($(e).data('url'), function(data) {
            $(e).html(data);
            $(e).removeClass('lazy-load');
        });
        if ($(e).data('period')) {
            setInterval(function() {
                periodicallyReload(e);
            }, $(e).data('period'));
        }
    });
});
