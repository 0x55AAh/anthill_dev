$(function() {

    // Table setup
    // ------------------------------

    // Initialize
    var updates_dt = $('.table-updates').DataTable({
        autoWidth: false,
        columnDefs: [
            {
                orderable: false,
                width: 200,
                targets: 1
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
            paginate: { 'first': 'First', 'last': 'Last', 'next': '&rarr;', 'previous': '&larr;' },
            emptyTable: 'No updates'
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
                text: '<span class="ladda-label">History</span>',
                name: 'updatesHistoryBtn',
                className: 'btn bg-blue',
                action: function ( e, dt, node, config ) {

                }
            },
            {
                text: '<span class="ladda-label">Update all</span>',
                name: 'updateAllBtn',
                className: 'btn bg-blue btn-ladda btn-ladda-spinner border-left-white',
                action: function ( e, dt, node, config ) {
                    dt.rows().every(function (rowIdx, tableLoop, rowLoop) {
                        var row = $(this.node());
                        var btn = row.find('button.update-action');
                        update(btn);
                    });
                    // console.log(dt.rows().count());
                    // dt.button('updateAllBtn:name').nodes().attr('disabled', 'disabled');
                    dt.clear().draw();
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

    updates_dt.button('updateAllBtn:name').nodes().attr('data-spinner-color', '#fff');
    updates_dt.button('updateAllBtn:name').nodes().attr('data-style', 'fade');
    if (updates_dt.rows().count() === 0)
        updates_dt.button('updateAllBtn:name').nodes().attr('disabled', 'disabled');

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
                closeOnConfirm: true,
                closeOnCancel: true
            },
            function (isConfirm) {
                if (isConfirm) {

                }
            });
    });

    $(document).on('click', '.table-updates .view-update-info', function (e) {
        e.preventDefault();
        swal({
            title: "What's new?",
            type: "info",
            text: "<div class=\"panel panel-body\">" +
            "                            <ul class=\"list-feed list-feed-rhombus list-feed-solid\">" +
            "                                <li><a href=\"#\">David Linner</a> requested refund for a double bank card charge</li>" +
            "                                <li>User <a href=\"#\">Christopher Wallace</a> from Google is awaiting for staff reply</li>" +
            "                                <li>Ticket <strong>#43683</strong> has been resolved by <a href=\"#\">Victoria Wilson</a></li>" +
            "                                <li><a href=\"#\">Eugene Kopyov</a> merged <strong>Master</strong>, <strong>Demo</strong> and <strong>Dev</strong> branches</li>" +
            "                                <li>All sellers have received payouts for December, 2016!</li>" +
            "                                <li><a href=\"#\">Chris Arney</a> created a new ticket <strong>#43136</strong> and assigned to <a href=\"#\">John Nod</a></li>" +
            "                            </ul>" +
            "                        </div>",
            html: true,
            confirmButtonColor: "#2196F3"
        });
    });

    function update(btn) {
        var row = btn.closest('tbody tr');
        btn.button('loading');
        setTimeout(function () {
            btn.button('reset');
            var animation = "fadeOutDownBig";
            row.addClass("animated " + animation).one("webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend", function () {
                updates_dt.row(row).remove().draw();
            });
        }, 3000)
    }

    // Initialize on button click
    $(document).on('click', '.btn-loading', function () {
        update($(this));
    });

    // Button with spinner
    Ladda.bind('.btn-ladda-spinner', {
        dataSpinnerSize: 16,
        timeout: 2000
    });

});