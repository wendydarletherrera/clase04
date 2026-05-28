(function () {
    window.renderDataTable = function renderDataTable(selector, columns, rows) {
        const table = $(selector);
        if ($.fn.DataTable.isDataTable(selector)) {
            table.DataTable().clear().destroy();
        }
        table.empty();

        return table.DataTable({
            data: rows,
            columns: columns,
            pageLength: 10,
            order: [],
            scrollX: true,
            dom: '<"dt-toolbar"Bf>rt<"dt-footer"lip>',
            buttons: [
                { extend: "csvHtml5", text: '<i class="fa-solid fa-file-csv"></i> CSV', className: "btn btn-sm btn-export" },
                { extend: "excelHtml5", text: '<i class="fa-solid fa-file-excel"></i> Excel', className: "btn btn-sm btn-export" }
            ],
            language: {
                search: "Buscar:",
                lengthMenu: "Mostrar _MENU_ registros",
                info: "Mostrando _START_ a _END_ de _TOTAL_",
                infoEmpty: "Sin registros",
                zeroRecords: "No se encontraron datos",
                paginate: {
                    first: "Primero",
                    last: "Ultimo",
                    next: "Siguiente",
                    previous: "Anterior"
                }
            }
        });
    };
})();
