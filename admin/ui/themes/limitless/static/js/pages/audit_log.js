$(function() {

    // Table setup
    // ------------------------------

    // Initialize
    $('.table-audit-log-records').DataTable({
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
            search: '<span>Search records:</span> _INPUT_',
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
        buttons: [],
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

    // Recover model object
    $(document).on('click', '.table-audit-log-records .recover-object-action', function (e) {
        e.preventDefault();
        var row = $(this).closest('tr');
        swal({
                title: "Are you sure?",
                text: "Object will be recovered to the previous version.",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#EF5350",
                confirmButtonText: "Recover",
                cancelButtonText: "Cancel",
                closeOnConfirm: false,
                closeOnCancel: true,
                showLoaderOnConfirm: true
            },
            function (isConfirm) {
                if (isConfirm) {
                    setTimeout(function() {
                        swal({
                            title: "Recovered!",
                            text: "Object has been recovered.",
                            confirmButtonColor: "#66BB6A",
                            type: "success"
                        }, function () {

                        });
                    }, 2000);
                }
            });
    });

});