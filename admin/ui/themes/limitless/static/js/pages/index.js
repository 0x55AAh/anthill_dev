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

    function filter_services_cards(q, animation) {
        $('.services-cards > div').each(function() {
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
    }

    // Build services cards and main sidebar services section.
    function update_services_cards() {
        var html_card_data = '', html_card_entry;
        var entries = anthill_storage.getItem(services_metadata_key);
        $.each(entries, function(index, entry) {
            html_card_entry = '' +
                '<div class="col-lg-2 col-md-3 col-sm-6" style="display: none" data-name="' + entry.name +'">' +
                '    <div class="panel" style="height: 290px;">' +
                     ((entry.debug) ? '<span class="label pull-right bg-success" style="font-weight: 400;font-size: 9px;line-height: normal;">debug</span>' : '') +
                '    <span class="label pull-left bg-grey-300" style="font-weight: 400;font-size: 9px;line-height: normal;">' + entry.version + '</span>' +
                '        <div class="panel-body text-center" style="padding: 15px;">' +
                '            <a href="/services/' + entry.name + '/" class="icon-object border-' + entry.color + ' text-' + entry.color + ' btn btn-flat">' +
                '                <i class="' + entry.iconClass + '"></i>' +
                '            </a>' +
                '            <h5 class="text-semibold">' + entry.title + '</h5>' +
                '            <p class="mb-15">' + entry.description + '</p>' +
                '        </div>' +
                '    </div>' +
                '</div>';
            html_card_data += html_card_entry;
        });
        if (anthill_storage.changed('html_card_data', html_card_data)) {
            $('.content-wrapper .content .row').html(html_card_data);
            $('.page-header .page-title span.badge-warning').text(entries.length);
            filter_services_cards($('input[name=search]').val().toUpperCase());
        }
    }

    $('input[name=search]').keyup(function() {
        filter_services_cards($(this).val().toUpperCase(), true);
    });

    setInterval(update_services_cards, UPDATE_INTERVAL * 1000);

});