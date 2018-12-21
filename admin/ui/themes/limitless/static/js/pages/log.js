/* ------------------------------------------------------------------------------
*
*  # Service log page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */

$(function() {

    var LOG_RE = /^(\[.*?\])\s+(.+)$/;

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
    var url = 'ws://localhost:9600/log/';
    var client = new ReconnectingWebSocket(url, [], options);
    client.addEventListener('message', function(event) {
        var parsed = event.data.match(LOG_RE);
        var prefix = parsed[1], message = parsed[2];
        var prefix_parts = prefix.match(/^\[(.+)\]$/)[1].split(/\s+/);
        var mode = prefix_parts[0],
            date = prefix_parts[1],
            time = prefix_parts[2],
            user = null;
        if (prefix_parts.length === 5) {
            user = prefix_parts[3];
        }
        term.echo([prefix, message].join(' '));
    });
    client.addEventListener('error', function(event) {
        // ¯\_(ツ)_/¯
    });

});