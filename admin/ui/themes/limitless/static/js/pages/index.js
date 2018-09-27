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

    var services_metadata_query = " \
        query {                     \
            servicesMetadata {      \
              name,                 \
              title,                \
              description,          \
              iconClass,            \
              color,                \
              version               \
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
                        '<div class="col-lg-2 col-md-3 col-sm-6" data-name="' + entry.name +'">' +
                        '    <div class="panel" style="height: 320px;">' +
                        '        <div class="panel-body text-center">' +
                        '            <a href="/services/' + entry.name + '/" class="icon-object border-' + entry.color + ' text-' + entry.color + ' btn btn-flat">' +
                        '                <i class="' + entry.iconClass + '"></i>' +
                        '            </a>' +
                        '            <h5 class="text-semibold">' + entry.title + '</h5>' +
                        '            <p class="mb-15">' + entry.description + '</p>' +
                        '            <span class="label text-grey-300">version ' + entry.version + '</span>' +
                        '        </div>' +
                        '    </div>' +
                        '</div>';
                    html_card_data += html_card_entry;
                });
                $('.content-wrapper .content .row').html(html_card_data);
                $('.page-header .page-title span.badge-warning').text(entries.length);
            },
            error: function(jqXHR, textStatus, errorThrown) {

            }
        });
    }

    setInterval(update_services_registry, AJAX_INTERVAL * 1000);

});