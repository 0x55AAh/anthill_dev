$(function() {

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('_xsrf'));
            }
        }
    });

    // Build services cards and main sidebar services section.
    function update_services_registry() {
        var services_metadata_query = " \
            query {                     \
                servicesMetadata {      \
                  title,                \
                  description,          \
                  iconClass,            \
                  color,                \
                  version               \
                }                       \
            }                           \
        ";
        $.ajax({
            url: '/api/',
            type: 'POST',
            dataType: 'json',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({query: services_metadata_query}),
            success: function (result) {
                // Build services cards.
                var new_html_card_data = '', new_html_card_entry;
                $.each(result.data.servicesMetadata, function (index, entry) {
                    new_html_card_entry = '' +
                        '<div class="col-lg-2 col-md-3 col-sm-6">' +
                        '    <div class="panel" style="height: 320px;">' +
                        '        <div class="panel-body text-center">' +
                        '            <a href="#" class="icon-object border-' + entry.color + ' text-' + entry.color + ' btn btn-flat">' +
                        '                <i class="' + entry.iconClass + '"></i>' +
                        '            </a>' +
                        '            <h5 class="text-semibold">' + entry.title + '</h5>' +
                        '            <p class="mb-15">' + entry.description + '</p>' +
                        '            <span class="label text-grey-300">version ' + entry.version + '</span>' +
                        '        </div>' +
                        '    </div>' +
                        '</div>';
                    new_html_card_data += new_html_card_entry;
                });
                $('.content-wrapper .content .row').html(new_html_card_data);
            },
            error: function (jqXHR, textStatus, errorThrown) {

            }
        });
    }

    setInterval(update_services_registry, 10 * 1000);

});