$(function() {

    var messenger = io('http://localhost:9609/messenger', {
        query: {
            _xsrf: Cookies.get('_xsrf')
        }
    });
	var $messages = $('.chat-list');

	var Guid = (function() {
        var Guid = {};
        Guid.newGuid = function() {
            return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
                return v.toString(16);
            });
        };
        return Guid;
    }());

	function updateMessagesAreaHeight() {
	    $messages.attr('style', 'min-height: 0px');
		var availableHeight = $(window).height() - $('.page-container').offset().top - $('.content-group').outerHeight();
        $messages.attr('style', 'min-height:' + availableHeight + 'px');
        // Scroll to bottom of the chat. Mainly for demo.
        $messages.scrollTop($messages[0].scrollHeight);
    }

    updateMessagesAreaHeight();

	// Nice scroll
    // ------------------------------

	// Setup
	function initScroll() {
	    $messages.niceScroll({
			cursoropacitymax: 0.7,
	        mousescrollstep: 40,
            scrollspeed: 10,
            cursorcolor: '#ccc',
            cursorborder: '',
            cursorwidth: 6,
            hidecursordelay: 100,
	        autohidemode: true,
	        horizrailenabled: false,
	        preservenativescrolling: false,
	        railpadding: {
	        	right: 0.5,
	        	top: 1.5,
	        	bottom: -1.5
	        }
	    });
	}

    // Initialize
    initScroll();

	$(window).on('resize', function() {
        setTimeout(function() {
            if($(window).width() <= 768) {
                $('body').addClass('sidebar-mobile-secondary');
                $('.content-group').hide();
            }
            else {
                $('body').removeClass('sidebar-mobile-secondary');
                $('.content-group').show();
            }
        }, 100);
    }).resize();

	$(window).on('resize', function() {
        setTimeout(function() {
            if($(window).width() > 768) {
                updateMessagesAreaHeight();
            }
        }, 100);
    });

	// Keyboard typing listener
    var typing_timer;
    function typing_started(group) {
        messenger.emit('typing_started', {group: group});
    }
    function typing_stopped(group) {
        typing_timer = 0;
        messenger.emit('typing_stopped', {group: group});
    }
    $("#message-form [name=text-message]").on("keyup keydown", function (event) {
        var current_group = 'test';
        if (typing_timer) {
            clearTimeout(typing_timer);
        } else {
            typing_started(current_group);
        }
        typing_timer = setTimeout(function() {
            typing_stopped(current_group);
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
        var form = this, $form = $(this),
            data = $form.find("[name=text-message]").val().trim();
        var group = 'test';
        if (data) {
            typing_stopped(group); // Force stop typing
            messenger.emit('create_message', {
                group: group,
                data: data,
                content_type: 'text/plain',
                event_id: Guid.newGuid()
            });
            $form.find("[name=text-message]").val(null);
        }
    });

    // Scroll messages
    $messages.on("scroll", function(event) {
        // code here
    });

    // Select group
    $(document).on("click", ".sidebar-category li.media", function(event) {
        if (!$(this).hasClass('active')) {
            // code here
        }
    });

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

    // General event handlers
    messenger.on('connect', function () {
        // ¯\_(ツ)_/¯
    });
    messenger.on('disconnect', function () {
        // ¯\_(ツ)_/¯
    });

    // Group event handlers
    messenger.on('create_group', function (data) {
        console.log(data);
    });
    messenger.on('update_group', function (data) {
        console.log(data);
    });
    messenger.on('delete_group', function (data) {
        console.log(data);
    });
    messenger.on('join_group', function (data) {
        console.log(data);
    });
    messenger.on('leave_group', function (data) {
        console.log(data);
    });

    // Message event handlers
    messenger.on('create_message', function (data) {
        console.log(data);
    });
    messenger.on('enumerate_group', function (data) {
        console.log(data);
    });
    messenger.on('list_messages', function (data) {
        console.log(data);
    });
    messenger.on('delete_messages', function (data) {
        console.log(data);
    });
    messenger.on('update_messages', function (data) {
        console.log(data);
    });
    messenger.on('read_messages', function (data) {
        console.log(data);
    });

    // System event handlers
    messenger.on('typing_started', function (data) {
        console.log(data);
    });
    messenger.on('typing_stopped', function (data) {
        console.log(data);
    });
    messenger.on('sending_file_started', function (data) {
        console.log(data);
    });
    messenger.on('sending_file_stopped', function (data) {
        console.log(data);
    });
    messenger.on('online', function (data) {
        console.log(data);
    });
    messenger.on('offline', function (data) {
        console.log(data);
    });

});