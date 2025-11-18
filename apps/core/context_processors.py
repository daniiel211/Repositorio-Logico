def datos_globales(request):
    """Context processor para datos globales del sistema"""
    return {
        'nombre_sistema': 'LogiCo',
        'version_sistema': '1.0.0',
        'empresa_cliente': 'Discopro Ltda.',
        'cliente_final': 'Cruz Verde',
    }