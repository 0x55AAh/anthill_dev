$(function() {
	var $messages = $('.chat-list');

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
    $messages.on("scroll", function(event) {
        // code here
    });

    // Select group
    $(document).on("click", ".sidebar-category li.media", function(event) {
        if (!$(this).hasClass('active')) {
            // code here
        }
    });

});