
                    var parametros = new window.URLSearchParams(window.location.search);    
                    var idUsuario = parametros.get('idUsuario');
                    console.log('idUsuario cargado: ',idUsuario);
                    var fecha_actual = new Date();
                    var strFecha_actual = fecha_actual.getFullYear() + "/" + (fecha_actual.getMonth()+1) + "/" + fecha_actual.getDate();
                    
                    url_empresas = "{{ url_for('usuarios_blueprint.empresasAjax') }}";
                    console.log('url carga:', url_empresas);
                    //var peticionData = {null};

                    var table = $('#tablaEmpresas').DataTable
                    ({
                        language: {
                            "decimal": "",
                            "emptyTable": "No hay información",
                            "info": "Mostrando _START_ a _END_ de _TOTAL_ Entradas",
                            "infoEmpty": "Mostrando 0 to 0 of 0 Entradas",
                            "infoFiltered": "(Filtrado de _MAX_ total entradas)",
                            "infoPostFix": "",
                            "thousands": ",",
                            "lengthMenu": "Mostrar _MENU_ Entradas",
                            "loadingRecords": "Cargando...",
                            "processing": "Procesando...",
                            "search": "Buscar:",
                            "zeroRecords": "Sin resultados encontrados",
                            "paginate": {
                                "first": "Primero",
                                "last": "Ultimo",
                                "next": "Siguiente",
                                "previous": "Anterior"
                            }
                        },

                        "ajax": {
                            "method": "POST",
                            "url": url_empresas,
                            "data": null
                        },
                        "columns": [
                            {"data":"id"},
                            {"data":"nombre"},
                            {"data":"cif"},
                            {"data":"plancontratado"},
                            {"data": "administrar",
                             "render": function(data, type, row) {
                                return "<button type='button' class='btn btn-primary' id='botonAdmin' data-id="+row['id']+" >Administrar</button>"
                                }
                            }
                        ]
                    });

                    $('#tablaEmpresas tbody').on('click', '#botonAdmin', function () {
                        
                        console.log("id de la empresa: ", this.dataset.id);
                        var id = this.dataset.id;

                        window.location.href = "{{ url_for('home') }}" + "?idEmpresa=" + id;
                    });
