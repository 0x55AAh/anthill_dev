jQuery(function($, undefined) {
    $('#console').terminal(function(command) {
        // if (command !== '') {
        //     var result = window.eval(command);
        //     if (result !== undefined) {
        //         this.echo(String(result));
        //     }
        // }
    }, {
        greetings: 'Debug console. Type `help` for supported commands.',
        name: 'debug',
        height: 522,
        width: 'auto',
        prompt: '> '
    });
});