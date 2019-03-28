$(function () {

    // Table setup
    // ------------------------------

    // Initialize
    var datatable = $('.table-commits').DataTable({
        autoWidth: false,
        columnDefs: [
            // {
            //     targets: 0,
            //     width: 400
            // },
            {
                orderable: false,
                width: 16,
                targets: 5
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
            search: '<span>Search commit:</span> _INPUT_',
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
                text: '<span class="ladda-label">Sync <i class="icon-loop3 position-right"></i></span>',
                className: 'btn bg-blue btn-ladda btn-ladda-spinner',
                name: 'syncBtn'
            }
        ],
        drawCallback: function (settings) {
            $(this).find('tbody tr').slice(-3).find('.dropdown, .btn-group').addClass('dropup');
        },
        preDrawCallback: function(settings) {
            $(this).find('tbody tr').slice(-3).find('.dropdown, .btn-group').removeClass('dropup');
        }
    });

    datatable.button('syncBtn:name').nodes().attr('data-spinner-color','#fff');
    datatable.button('syncBtn:name').nodes().attr('data-style','zoom-in');


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

    // Apply commit
    $(document).on('click', '.table-commits .apply-commit-action', function (e) {
        e.preventDefault();
        swal({
                title: "Are you sure?",
                text: "Commit will be applied.",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#EF5350",
                confirmButtonText: "Apply",
                cancelButtonText: "Cancel",
                closeOnConfirm: false,
                closeOnCancel: true
            },
            function (isConfirm) {
                if (isConfirm) {

                }
            });
    });

    // Button with spinner
    Ladda.bind('.btn-ladda-spinner', {
        dataSpinnerSize: 16,
        timeout: 2000
    });

});