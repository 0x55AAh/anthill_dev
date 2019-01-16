function popup(url, title, w, h) {
    var dualScreenLeft = window.screenLeft !== undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop !== undefined ? window.screenTop : screen.top;

    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth
        ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight
        ? document.documentElement.clientHeight : screen.height;

    var left = width / 2 - w / 2 + dualScreenLeft;
    var top = height / 2 - h / 2 + dualScreenTop;

    var params = [
        'scrollbars=no',
        'width=' + w,
        'height=' + h,
        'top=' + top,
        'left=' + left
    ];

    var newWindow = window.open(url, title, params.join());

    if (window.focus && newWindow !== undefined) {
        newWindow.focus();
    }

    return newWindow;
}
