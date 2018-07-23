/* ------------------------------------------------------------------------------
*
*  # Dropzone multiple file uploader
*
*  Specific JS code additions for uploader_dropzone.html page
*
*  Version: 1.0
*  Latest update: Aug 1, 2015
*
* ---------------------------------------------------------------------------- */

$(function() {

    // Parse the cookie value for a CSRF token
    var xsrftoken;
    var cookies = ('; ' + document.cookie).split('; _xsrf=');
    if (cookies.length === 2)
        xsrftoken = cookies.pop().split(';').shift();

    // Defaults
    Dropzone.autoDiscover = false;

    var url = '/upload/';
    var headers = {'X-CSRFToken': xsrftoken};


    // Single file
    $("#dropzone_single").dropzone({
        paramName: "file", // The name that will be used to transfer the file
        maxFilesize: 1024, // MB
        maxFiles: 1,
        dictDefaultMessage: 'Drop file to upload <span>or CLICK</span>',
        autoProcessQueue: false,
        init: function() {
            this.on('addedfile', function(file){
                if (this.fileTracker) {
                this.removeFile(this.fileTracker);
            }
                this.fileTracker = file;
            });
        },
        headers: headers,
        url: url
    });


    // Multiple files
    $("#dropzone_multiple").dropzone({
        paramName: "file", // The name that will be used to transfer the file
        dictDefaultMessage: 'Drop files to upload <span>or CLICK</span>',
        maxFilesize: 1024, // MB
        headers: headers,
        url: url
    });


    // Accepted files
    $("#dropzone_accepted_files").dropzone({
        paramName: "file", // The name that will be used to transfer the file
        dictDefaultMessage: 'Drop files to upload <span>or CLICK</span>',
        maxFilesize: 1024, // MB
        acceptedFiles: 'image/*',
        headers: headers,
        url: url
    });


    // Removable thumbnails
    $("#dropzone_remove").dropzone({
        paramName: "file", // The name that will be used to transfer the file
        dictDefaultMessage: 'Drop files to upload <span>or CLICK</span>',
        maxFilesize: 1024, // MB
        addRemoveLinks: true,
        headers: headers,
        url: url
    });


    // File limitations
    $("#dropzone_file_limits").dropzone({
        paramName: "file", // The name that will be used to transfer the file
        dictDefaultMessage: 'Drop files to upload <span>or CLICK</span>',
        maxFilesize: 1024, // MB
        maxFiles: 4,
        maxThumbnailFilesize: 1,
        addRemoveLinks: true,
        headers: headers
    });
    
});
