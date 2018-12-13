$(function() {

    var AJAX_INTERVAL = 10;
    var UPDATE_INTERVAL = 1;
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
              description,          \
              iconClass,            \
              color,                \
              version,              \
              debug,                \
              publicApiUrl          \
            }                       \
        }";

    var services_metadata_key = 'servicesMetadata';

    function update_services_registry() {
        $.ajax({
            url: window.public_api_url,
            type: 'POST',
            dataType: 'json',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({query: services_metadata_query}),
            success: function(result) {
                anthill_storage.setItem(services_metadata_key, result.data['servicesMetadata']);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                anthill_storage.setItem(services_metadata_key, []); // ¯\_(ツ)_/¯
            }
        });
    }

    // Build main sidebar services section.
    function update_sidebar_services() {
        var html_sidebar_data = '', html_sidebar_entry;
        var entries = anthill_storage.getItem(services_metadata_key);
        $.each(entries, function(index, entry) {
            var active = service_match(entry.name) ? 'active' : '';
            html_sidebar_entry =
                '<li class="navigation-service ' + active + '" data-name="' + entry.name +'">' +
                '    <a href="/services/' + entry.name + '/"><i class="' + entry.iconClass + '"></i> <span>' + entry.title + '</span></a>' +
                '</li>';
            html_sidebar_data += html_sidebar_entry;
        });
        if (anthill_storage.changed('html_sidebar_data', html_sidebar_data)) {
            $('.sidebar-main ul.navigation-main li.navigation-service').remove();
            $('.sidebar-main ul.navigation-main li.navigation-header-services').after(html_sidebar_data);
        }
    }

    update_services_registry();
    setInterval(update_services_registry, AJAX_INTERVAL * 1000);
    setInterval(update_sidebar_services, UPDATE_INTERVAL * 1000);

});