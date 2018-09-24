/* ------------------------------------------------------------------------------
*
*  # Debug page
*
*  Version: 1.0
*
* ---------------------------------------------------------------------------- */

$(function() {

    var logo =
        "    _          _   _     _ _ _ \n"    +
        "   / \\   _ __ | |_| |__ (_) | |\n"   +
        "  / _ \\ | '_ \\| __| '_ \\| | | |\n" +
        " / ___ \\| | | | |_| | | | | | |\n"   +
        "/_/   \\_\\_| |_|\\__|_| |_|_|_|_|";

    var config = {
        hearbeat: 5000,
        sendCloseMessage: false,
        ws: {
            uri: ws_url('/debug-session/'),
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

    var client = new JsonRpcClient(config);

    function parse_command(raw_command) {
        var splitted_command = raw_command.trim().split(/\s+/);
        return {
            'command': splitted_command[0],
            'params': splitted_command.slice(1)
        }
    }

    $('.console').terminal(function(raw_command, term) {
        var parsed_command = parse_command(raw_command);
        var command = parsed_command.command,
            params = parsed_command.params;
        if (command !== '') {
            client.send(command, params, function(error, response) {
                if (error) {
                    term.echo(error.message);
                } else if (response) {
                    term.echo(String(response));
                }
            });
        }
    }, {
        greetings: logo + '\n\nDebug console. Type `help` for supported commands.',
        name: 'debug',
        height: 522,
        width: 'auto',
        prompt: 'anthill:~ '
    });

});