/* ------------------------------------------------------------------------------
*
*  # Index page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */


$(function() {

    var UPDATE_INTERVAL = 1;
    var services_metadata_key = 'servicesMetadata';

    function setCardsSameHeight() {
        var card_heights = $('.services-cards__entry .panel-body').map(function () {
            return $(this).outerHeight();
        });
        $('.services-cards__entry .panel').height(Math.max.apply(null, card_heights));
    }

    function filter_services_cards(q, animation) {
        $('.services-cards__entry').each(function() {
            var service_name = $(this).data('name').toUpperCase();
            if (service_name.indexOf(q) === 0) {
                if (animation) {
                    $(this).fadeIn(100, function () {
                        // ¯\_(ツ)_/¯
                    });
                } else {
                    $(this).show();
                }
            } else {
                if (animation) {
                    $(this).fadeOut(100, function () {
                        // ¯\_(ツ)_/¯
                    });
                } else {
                    $(this).hide();
                }
            }
        });
        setCardsSameHeight();
    }

    // Build services cards and main sidebar services section.
    function update_services_cards() {
        var html_cards_list = '', html_card_entry;
        var entries = anthill_storage.getItem(services_metadata_key);

        $.each(entries, function(index, entry) {
            html_card_entry =
                '<div class="col-lg-2 col-md-3 col-sm-6 services-cards__entry" style="display: none" data-name="' + entry.name +'">' +
                '    <div class="panel">' +
                     ((entry.debug) ? '<span class="label pull-right bg-success" style="font-weight: 400;font-size: 9px;line-height: normal;">debug</span>' : '') +
                '        <div class="panel-body text-center">' +
                '            <a href="/services/' + entry.name + '/" class="icon-object border-' + entry.color + ' text-' + entry.color + ' btn btn-flat">' +
                '                <i class="' + entry.iconClass + '"></i>' +
                '            </a>' +
                '            <h5 class="text-semibold">' + entry.title + '</h5>' +
                '            <p class="mb-15">' +
                '                <span class="label bg-success">updated</span>' +
                '                <span class="label bg-grey-300" style="margin-top: 3px;">' + entry.version + '</span>' +
                '            </p>' +
                '            <p class="mb-15">' + entry.description + '</p>' +
                '        </div>' +
                '    </div>' +
                '</div>';
            html_cards_list += html_card_entry;
        });

        if (anthill_storage.changed('html_cards_list', html_cards_list)) {
            $('.services-cards').html(html_cards_list);
            $('.page-header .page-title span.badge-warning').text(entries.length);
            var query = $('input[name=search]').val().toUpperCase();
            filter_services_cards(query);
        }
    }

    $('input[name=search]').keyup(function() {
        var query = $(this).val().toUpperCase();
        filter_services_cards(query, true);
    });

    $(window).on('resize', setCardsSameHeight).resize();

    setInterval(update_services_cards, UPDATE_INTERVAL * 1000);

});