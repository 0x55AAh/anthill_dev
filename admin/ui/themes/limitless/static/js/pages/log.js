/* ------------------------------------------------------------------------------
*
*  # Service log page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */

$(function() {
    var debug = $('body').data('debug') === 1;
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
        debug: debug
    };
    var url = 'ws://localhost:9500/log/';
    var client = new ReconnectingWebSocket(url, [], options);
    client.addEventListener('message', function(event) {
        term.echo(event.data);
    });
    client.addEventListener('error', function(event) {

    });
});