$(function() {

    var AJAX_INTERVAL = 10;
    var page_id = $('body').data('page-id');

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
                  iconClass,            \
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
                var new_html_sidebar_data = '', new_html_sidebar_entry;
                var entries = result.data['servicesMetadata'];
                $.each(entries, function (index, entry) {
                    new_html_sidebar_entry = '' +
                        '<li class="navigation-service">' +
                        '    <a href="#"><i class="' + entry.iconClass + '"></i> <span>' + entry.title + '</span></a>' +
                        '</li>';
                    new_html_sidebar_data += new_html_sidebar_entry;
                });
                $('.sidebar-main ul.navigation-main li.navigation-service').remove();
                $('.sidebar-main ul.navigation-main li.navigation-header').after(new_html_sidebar_data);
            },
            error: function (jqXHR, textStatus, errorThrown) {

            }
        });
    }

    setInterval(update_services_registry, AJAX_INTERVAL * 1000);

});