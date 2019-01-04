$(function() {
	var $messages = $('.chat-list, .chat-stacked');

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
	    $(".chat-list, .chat-stacked").niceScroll({
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

});