$(function() {

    var url = ws_url('/debug-session/');

    var config = {
        hearbeat: 5000,
        sendCloseMessage: false,
        ws: {
            uri: url,
            useSockJS: false,
            onconnected: null,
            ondisconnect: null,
            onreconnecting: null,
            onreconnected: null
        },
        rpc: {
            requestTimeout: 15000,
            treeStopped: null,
            iceCandidate: null
        }
    };

    var client = new JsonRpcClient(config);

    function parse_params(command) {
        return {}
    }

    $('#console').terminal(function(command, term) {
        var params = parse_params(command);
        if (command !== '') {
            client.send(command, params, function(error, response) {
                if (error) {
                    term.echo(error.message);
                } else if (response !== undefined) {
                    term.echo(String(response));
                }
            });
        }
    }, {
        greetings: 'Debug console. Type `help` for supported commands.',
        name: 'debug',
        height: 522,
        width: 'auto',
        prompt: '> '
    });

});