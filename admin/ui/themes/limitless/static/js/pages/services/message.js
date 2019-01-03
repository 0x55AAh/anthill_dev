$(function() {

	// Scroll to bottom of the chat on page load. Mainly for demo
	var $messages = $('.chat-list, .chat-stacked');
	$messages.scrollTop($messages[0].scrollHeight);


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

});