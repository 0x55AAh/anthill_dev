$(function () {

    // Table setup
    // ------------------------------

    // Initialize
    $('.table-customers').DataTable({
        autoWidth: false,
        columnDefs: [
            {
                targets: 0,
                width: 40
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
            search: '<span>Search event:</span> _INPUT_',
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
                // extend: 'pdfHtml5',
                text: 'Create event <i class="icon-plus22 position-right"></i>',
                className: 'btn bg-blue',
                orientation: 'landscape',
                customize: function (doc) {
                    doc.content[1].table.widths = Array(doc.content[1].table.body[0].length + 1).join('*').split('');
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

    // Initialize with options
    var $picker = $('.daterange-predefined').daterangepicker(
        {
            timePicker: true,
            timePickerIncrement: 1,
            timePicker24Hour: true,

            opens: 'left',
            applyClass: 'btn-small bg-slate',
            cancelClass: 'btn-small btn-default',
            locale: {
                format: 'MM/DD/YYYY h:mm'
            }
        },
        function(start, end) {
            $('.daterange-predefined span').html(
                start.format('MMMM D, YYYY, h:mm') + ' &nbsp; - &nbsp; ' + end.format('MMMM D, YYYY, h:mm'));
            $.jGrowl('Date range has been changed', { header: 'Update', theme: 'bg-primary', position: 'center', life: 1500 });
        }
    );

    $picker.on('show.daterangepicker', function (ev, picker) {
	if (picker.element.offset().top - $(window).scrollTop() + picker.container.outerHeight() > $(window).height()) {
		picker.drops = 'up';
	} else {
		picker.drops = 'down';
	}
	picker.move();
});

    // Display date format
    $('.daterange-predefined span').html(moment().subtract(29, 'days')
        .format('MMMM D, YYYY, h:mm a') + ' &nbsp; - &nbsp; ' + moment().format('MMMM D, YYYY, h:mm a'));

});