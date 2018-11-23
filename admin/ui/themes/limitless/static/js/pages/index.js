/* ------------------------------------------------------------------------------
*
*  # Index page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */


$(function() {

    var AJAX_INTERVAL = 10;

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('_xsrf'));
            }
        }
    });

    function filter_service_cards(q, animation) {
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

    var services_metadata_query = " \
        query {                     \
            servicesMetadata {      \
              name,                 \
              title,                \
              description,          \
              iconClass,            \
              color,                \
              version,              \
              debug,                \
            }                       \
        }";

    // Build services cards and main sidebar services section.
    function update_services_registry() {
        $.ajax({
            url: '/api/',
            type: 'POST',
            dataType: 'json',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({query: services_metadata_query}),
            success: function(result) {
                var html_card_data = '', html_card_entry;
                var entries = result.data['servicesMetadata'];
                $.each(entries, function(index, entry) {
                    html_card_entry = '' +
                        '<div class="col-lg-2 col-md-3 col-sm-6" style="display: none" data-name="' + entry.name +'">' +
                        '    <div class="panel" style="height: 290px;">' +
                        '        <span class="label pull-right ' + ((entry.debug) ? 'bg-success' : 'bg-danger') + '" style="font-weight: 400;font-size: 9px;line-height: normal;">debug</span>' +
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
                $('.content-wrapper .content .row').html(html_card_data);
                $('.page-header .page-title span.badge-warning').text(entries.length);
                filter_service_cards($('input[name=search]').val().toUpperCase());
            },
            error: function(jqXHR, textStatus, errorThrown) {
                // ¯\_(ツ)_/¯
            }
        });
    }

    setInterval(update_services_registry, AJAX_INTERVAL * 1000);

    $('input[name=search]').keyup(function() {
        filter_service_cards($(this).val().toUpperCase(), true);
    });

});