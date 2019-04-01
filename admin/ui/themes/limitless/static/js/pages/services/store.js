$(function () {

    // Table setup
    // ------------------------------

    // Initialize
    var datatable = $('.table-items').DataTable({
        autoWidth: false,
        columnDefs: [
            {
                targets: 0,
                width: 400
            },
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
            search: '<span>Search item:</span> _INPUT_',
            searchPlaceholder: 'Type to filter...',
            lengthMenu: '<span>Show:</span> _MENU_',
            paginate: { 'first': 'First', 'last': 'Last', 'next': '&rarr;', 'previous': '&larr;' },
            emptyTable: 'No data available in table'
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
                text: 'Create item <i class="icon-plus22 position-right"></i>',
                className: 'btn bg-blue',
                action: function ( e, dt, node, config ) {

                }
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


    // Switchery toggles
    // ------------------------------

    var switches = Array.prototype.slice.call(document.querySelectorAll('.switch'));
    switches.forEach(function(html) {
        var switchery = new Switchery(html, {color: '#4CAF50'});
    });

    // Remove store item
    $(document).on('click', '.table-items .remove-item-action', function (e) {
        e.preventDefault();
        var row = $(this).closest('tbody tr');
        swal({
                title: "Are you sure?",
                text: "Store item will be removed.",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#EF5350",
                confirmButtonText: "Remove",
                cancelButtonText: "Cancel",
                closeOnConfirm: false,
                closeOnCancel: true,
                showLoaderOnConfirm: true
            },
            function (isConfirm) {
                if (isConfirm) {
                    setTimeout(function() {
                        swal({
                            title: "Removed!",
                            text: "Store item has been removed.",
                            confirmButtonColor: "#66BB6A",
                            type: "success"
                        }, function () {
                            // Remove entry from UI
                            var animation = "fadeOutUpBig";
                            row.addClass("animated " + animation).one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend", function () {
                                datatable.row(row).remove().draw();
                            });
                        });
                    }, 2000);
                }
            });
    });

});