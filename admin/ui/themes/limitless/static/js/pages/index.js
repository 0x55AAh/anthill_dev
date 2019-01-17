/* ------------------------------------------------------------------------------
*
*  # Index page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */


$(function () {

    var UPDATE_INTERVAL = 1;
    var services_metadata_key = 'servicesMetadata';

    function setCardsSameHeight() {
        var $panels = $('.services-cards__entry .panel');
        var card_heights = $panels.map(function () {
            var h1 = $(this).find('.panel-heading').outerHeight(),
                h2 = $(this).find('.panel-body').outerHeight();
            return h1 + h2;
        });
        $panels.height(Math.max.apply(null, card_heights));
    }

    function updateCardHeight($panel) {
        var h1 = $panel.find('.panel-heading').outerHeight(),
            h2 = $panel.find('.panel-body').outerHeight();
        $panel.height(h1 + h2);
    }

    function filter_services_cards(q, animation) {
        $('.services-cards__entry').each(function () {
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
        $('.panel-title').parent()
            .has('> .heading-elements:not(.not-collapsible)')
            .children('.panel-title')
            .append('<a class="heading-elements-toggle"><i class="icon-more"></i></a>');
    }

    // Build services cards and main sidebar services section.
    function update_services_cards() {
        var html_cards_list = '', html_card_entry;
        var entries = anthill_storage.getItem(services_metadata_key);

        $.each(entries, function (index, entry) {
            html_card_entry =
                '<div class="col-lg-2 col-md-3 col-sm-6 services-cards__entry" style="display: none" data-name="' + entry.name + '">' +
                '    <div class="panel panel-flat">' +
                '        <div class="panel-heading">' +
                '            <div class="panel-title">' +
                ((entry.debug) ? '<span class="label bg-success" style="font-weight: 400;font-size: 9px;line-height: normal;">debug</span>' : '') +
                '            </div>' +
                '            <div class="heading-elements">' +
                '                <ul class="icons-list text-muted">' +
                '                    <li class="dropdown">' +
                '                        <a href="#" class="dropdown-toggle" data-toggle="dropdown"><i class="icon-cog3"></i> <span class="caret"></span></a>' +
                '                        <ul class="dropdown-menu dropdown-menu-right">' +
                '                            <li class="update_service"><a href="#"><i class="icon-download"></i> Update</a></li>' +
                '                        </ul>' +
                '                    </li>' +
                '                </ul>' +
                '            </div>' +
                '        </div>' +
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
            $('.page-header .page-title .badge').text(entries.length);
            var query = $('input[name=search]').val().toUpperCase();
            filter_services_cards(query);
        }
    }

    $('input[name=search]').keyup(function () {
        var query = $(this).val().toUpperCase();
        filter_services_cards(query, true);
    });

    $(document).on('click', '.heading-elements-toggle', function () {
        updateCardHeight($(this).closest('.panel'));
    });

    $(window).on('resize', setCardsSameHeight).resize();

    $(".services-cards__entry").each(function () {
        var name = $(this).data("name");
        var uptime = $(this).data("uptime");

        var timer = new easytimer.Timer();

        function updateUptime() {
            var newValue = timer.getTimeValues().toString();
            var data = '<i class="icon-history text-warning position-left"></i>';
            var $item = $('#' + "services-cards__entry__" + name + "_uptime");
            $item.html(data).attr('title', newValue);
        }

        timer.start({precision: 'seconds', startValues: {seconds: uptime}});

        updateUptime();
        timer.addEventListener('minutesUpdated', function (e) {
            updateUptime();
        });
    });

    setInterval(update_services_cards, UPDATE_INTERVAL * 1000);

});