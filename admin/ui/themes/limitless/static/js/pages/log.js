/* ------------------------------------------------------------------------------
*
*  # Service log page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */

$(function() {

    var LOG_RE = /^(\[.*?\])\s+(.+)$/;
    var LOG_STRIPPED_PREFIX_RE = /^\[(.+)\]$/;

    var term = $('.console').terminal(function() {}, {
        enable: false,
        greetings: null,
        name: 'log',
        height: 522,
        width: 'auto',
        prompt: ''
    });
    var options = {
        connectionTimeout: 1000,
        maxRetries: 10,
        debug: window.debug
    };
    var url = ws_url(window.log_url);
    var client = new ReconnectingWebSocket(url, [], options);
    client.addEventListener('message', function(event) {
        var parsed = event.data.match(LOG_RE);
        var prefix = parsed[1],
            prefix_stripped = prefix.match(LOG_STRIPPED_PREFIX_RE)[1],
            message = parsed[2];
        var prefix_parts = prefix_stripped.split(/\s+/);
        var level = prefix_parts[0],
            date = prefix_parts[1],
            time = prefix_parts[2],
            user = null;
        if (prefix_parts.length === 5) {
            user = prefix_parts[3];
        }
        var colors = {
            'D': 'blue',   // Blue
            'I': 'green',  // Green
            'W': 'yellow', // Yellow
            'E': 'red'     // Red
        };
        var prefix_stripped_colored = "[[;" + colors[level] + ";] " + prefix_stripped + "]";
        term.echo(prefix_stripped_colored + " " + message);
    });
    client.addEventListener('error', function(event) {
        // ¯\_(ツ)_/¯
    });

});