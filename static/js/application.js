function periodicallyReload(e) {
    $.get($(e).data('url'), function(data) {
        $(e).fadeOut(800, function() {
            $(e).html(data);
            $(e).fadeIn(400, function() {
                setTimeout(function() {
                    periodicallyReload(e);  // reschedule self
                }, $(e).data('period'));
            });
        });
    });
}

$(document).ready(function() {
    $('div.lazy-load').each(function(i, e) {
        $.get($(e).data('url'), function(data) {
            $(e).html(data);
        });
        if ($(e).data('period')) {
            setTimeout(function() {
                periodicallyReload(e);
            }, $(e).data('period'));
        }
    });
});
