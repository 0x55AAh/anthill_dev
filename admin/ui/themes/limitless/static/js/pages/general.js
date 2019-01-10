$(function() {

    var AJAX_INTERVAL = 10;
    var UPDATE_INTERVAL = 1;

    var messenger_options = {
        connectionTimeout: 1000,
        maxRetries: 10,
        debug: window.debug
    };
    var messenger_url = ws_url('http://localhost:9609/messenger/');
    var messenger_client = new ReconnectingWebSocket(messenger_url, [], messenger_options);
    messenger_client.addEventListener('message', function(event) {
        // ¯\_(ツ)_/¯
    });
    messenger_client.addEventListener('error', function(event) {
        // ¯\_(ツ)_/¯
    });

    var utils_config = {
        hearbeat: 5000,
        sendCloseMessage: false,
        ws: {
            uri: ws_url('/utils-session/'),
            useSockJS: false,
            onconnected: function() {},
            ondisconnect: function() {},
            onreconnecting: function() {},
            onreconnected: function() {}
        },
        rpc: {
            requestTimeout: 15000
        }
    };

    var utils_client = new JsonRpcClient(utils_config);

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", Cookies.get('_xsrf'));
            }
        }
    });

    function api_request(query, success, error, url) {
        $.ajax({
            url: url || window.public_api_url,
            type: 'POST',
            dataType: 'json',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({query: query}),
            success: success,
            error: error
        });
    }

    function service_match(serviceName) {
        return serviceName === window.service_name;
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
              publicApiUrl,         \
              uptime,               \
              logUrl                \
            }                       \
        }";

    var services_metadata_key = 'servicesMetadata';

    function update_services_registry() {
        api_request(
            services_metadata_query,
            function(result) {
                anthill_storage.setItem(services_metadata_key, result.data['servicesMetadata']);
            },
            function(jqXHR, textStatus, errorThrown) {
                anthill_storage.setItem(services_metadata_key, []); // ¯\_(ツ)_/¯
            }
        );
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

    // Update service
    $(document).on('click', '.services-cards__entry .update_service a, .sidebar-main .update_service a', function(e) {
        e.preventDefault();
        var service_name = $(this).closest('.services-cards__entry').data('name') || window.service_name;
        swal({
                title: "Are you sure?",
                text: "Service " + service_name.toUpperCase() + " will be updated!",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#EF5350",
                confirmButtonText: "Update",
                cancelButtonText: "Cancel",
                closeOnConfirm: false,
                closeOnCancel: true
            },
            function(isConfirm) {
                if (isConfirm) {
                    var args = {service_name: service_name, version: null};
                    utils_client.send('update', args, function(error, response) {
                        if (error) { // ¯\_(ツ)_/¯
                            swal({
                                title: "Error",
                                text: error.message,
                                confirmButtonColor: "#2196F3",
                                type: "error"
                            });
                        } else {
                            swal({
                                title: "Updated",
                                text: response.message,
                                confirmButtonColor: "#66BB6A",
                                type: "success"
                            });
                        }
                    });
                }
            });
    });

    update_services_registry();
    setInterval(update_services_registry, AJAX_INTERVAL * 1000);
    setInterval(update_sidebar_services, UPDATE_INTERVAL * 1000);

    ion.sound({
        sounds: [
            {
                name: "button_tiny",
                alias: "incoming_message"
            }
        ],
        volume: 0.5,
        path: "/static/js/plugins/sounds/ion.sound/sounds/",
        preload: true
    });

    // Keyboard typing listener
    var timer;
    $("#message-form [name=text-message]").on("keyup keydown", function (event) {
        if (timer) {
            clearTimeout(timer);
        } else {
            // code here
        }
        timer = setTimeout(function() {
            timer = 0;
            // code here
        }, 3000);
    });

    $("#message-form [name=text-message]").on("keydown", function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            $("#message-form").trigger('submit');
        }
    });
    $("#message-form").on("focusout", function (event) {
        var $form = $(this);
        setTimeout(function () {
            if (!$form.find(':focus').length) {
                $form.trigger('submit', [event.type]);
            }
        }, 0);
    });

    // Send text message
    $("#message-form").on("submit", function (event, parentEvent) {
        event.preventDefault();
        var form = this, $form = $(this);
    });

    // Scroll messages
    $(".chat-list").on("scroll", function(event) {
        var $history = $(this);
        // code here
    });

    // Select group
    $(document).on("click", ".sidebar-category li.media", function(event) {
        var $history = $('.chat-list');
        if (!$(this).hasClass('active')) {
            // code here
        }
    });

});