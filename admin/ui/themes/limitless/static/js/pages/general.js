$(function() {

    var AJAX_INTERVAL = 10;
    var current_service_name = $('body').data('service-name');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('_xsrf'));
            }
        }
    });

    function service_match(serviceName) {
        return current_service_name !== undefined
            && serviceName === current_service_name;
    }

    var services_metadata_query = " \
        query {                     \
            servicesMetadata {      \
              name,                 \
              title,                \
              iconClass             \
            }                       \
        }";

    // Build main sidebar services section.
    function update_services_registry() {
        $.ajax({
            url: '/api/',
            type: 'POST',
            dataType: 'json',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({query: services_metadata_query}),
            success: function(result) {
                var html_sidebar_data = '', html_sidebar_entry;
                var entries = result.data['servicesMetadata'];
                $.each(entries, function(index, entry) {
                    var active = service_match(entry.name) ? 'active' : '';
                    html_sidebar_entry = '' +
                        '<li class="navigation-service ' + active + '" data-name="' + entry.name +'">' +
                        '    <a href="/services/' + entry.name + '/"><i class="' + entry.iconClass + '"></i> <span>' + entry.title + '</span></a>' +
                        '</li>';
                    html_sidebar_data += html_sidebar_entry;
                });
                $('.sidebar-main ul.navigation-main li.navigation-service').remove();
                $('.sidebar-main ul.navigation-main li.navigation-header').after(html_sidebar_data);
            },
            error: function(jqXHR, textStatus, errorThrown) {

            }
        });
    }

    setInterval(update_services_registry, AJAX_INTERVAL * 1000);

});