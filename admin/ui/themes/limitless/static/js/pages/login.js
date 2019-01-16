/* ------------------------------------------------------------------------------
*
*  # Login page
*
*  Specific JS code additions for login and registration pages
*
*  Version: 1.0
*  Latest update: Aug 1, 2015
*
* ---------------------------------------------------------------------------- */

$(function () {

    // Style checkboxes and radios
    $('.styled').uniform();

    $('ul.social-auth > li > a').on('click', function () {
        var social_auth_name = $(this).data('social-auth-name');
        var popup_size = $(this).data('popup-size').split(',');
        if (popup_size.length === 2) {
            popup_size = popup_size.map(function (value) {
                return parseInt(value);
            });
        } else {
            popup_size = [450, 500]; // Default size
        }
        var width = popup_size[0], height = popup_size[1];
        var login_location = 'http://localhost:9607/social/login/';
        var url = login_location + social_auth_name;
        window.popup(url, 'Authenticate', width, height);
    });

});
