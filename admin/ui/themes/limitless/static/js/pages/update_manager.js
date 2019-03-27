$(function() {

    // Table setup
    // ------------------------------

    // Initialize
    $('.table-updates').DataTable({
        autoWidth: false,
        columnDefs: [
            /*{
                targets: 0,
                width: 400
            },*/
            {
                orderable: false,
                width: 16,
                targets: 6
            },
            {
                className: 'control',
                orderable: false,
                targets: -1
            }
        ],
        order: [[ 0, 'asc' ]],
        dom: '<"datatable-header datatable-header-accent"fBl><""t><"datatable-footer"ip>',
        language: {
            search: '<span>Search update:</span> _INPUT_',
            searchPlaceholder: 'Type to filter...',
            lengthMenu: '<span>Show:</span> _MENU_',
            paginate: { 'first': 'First', 'last': 'Last', 'next': '&rarr;', 'previous': '&larr;' }
        },
        lengthMenu: [ 25, 50, 75, 100 ],
        displayLength: 50,
        responsive: {
            details: {
                type: 'column',
                target: -1
            }
        },
        buttons: [
            {
                text: 'Update all <i class="icon-spinner11 position-right"></i>',
                className: 'btn bg-blue',
                orientation: 'landscape'
            }
        ],
        drawCallback: function (settings) {
            $(this).find('tbody tr').slice(-3).find('.dropdown, .btn-group').addClass('dropup');
        },
        preDrawCallback: function(settings) {
            $(this).find('tbody tr').slice(-3).find('.dropdown, .btn-group').removeClass('dropup');
        }
    });


    // External table additions
    // ------------------------------

    // Enable Select2 select for the length option
    $('.dataTables_length select').select2({
        minimumResultsForSearch: Infinity,
        width: 'auto'
    });

    // Run update
    $(document).on('click', '.table-updates .run-update-action', function (e) {
        e.preventDefault();
        swal({
                title: "Are you sure?",
                text: "Service will be updated to the latest version.",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#EF5350",
                confirmButtonText: "Update",
                cancelButtonText: "Cancel",
                closeOnConfirm: false,
                closeOnCancel: true
            },
            function (isConfirm) {
                if (isConfirm) {

                }
            });
    });

});