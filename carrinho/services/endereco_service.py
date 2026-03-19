def validar_endereco(endereco):
    """
    Valida um endereço antes de salvar.
    Retorna (é_válido, lista_de_erros)
    """
    erros = []
    
    # CEP
    cep = endereco.get("cep", "").replace("-", "").strip()
    if not cep:
        erros.append("CEP é obrigatório")
    elif len(cep) != 8 or not cep.isdigit():
        erros.append("CEP deve ter 8 dígitos")
    
    # Rua
    rua = endereco.get("rua", "").strip()
    if not rua:
        erros.append("Rua é obrigatória")
    elif len(rua) < 3:
        erros.append("Rua deve ter pelo menos 3 caracteres")
    
    # Número
    numero = endereco.get("numero", "").strip()
    if not numero:
        erros.append("Número é obrigatório")
    elif len(numero) > 20:
        erros.append("Número muito longo")
    
    # Bairro
    bairro = endereco.get("bairro", "").strip()
    if not bairro:
        erros.append("Bairro é obrigatório")
    elif len(bairro) < 2:
        erros.append("Bairro inválido")
    
    # Cidade
    cidade = endereco.get("cidade", "").strip()
    if not cidade:
        erros.append("Cidade é obrigatória")
    elif len(cidade) < 2:
        erros.append("Cidade inválida")
    
    # Estado (UF)
    estado = endereco.get("estado", "").strip().upper()
    ufs_validas = [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
        "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
        "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ]
    if not estado:
        erros.append("Estado é obrigatório")
    elif estado not in ufs_validas:
        erros.append("Estado inválido")
    
    return len(erros) == 0, erros