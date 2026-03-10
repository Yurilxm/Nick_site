class BaseGateway:

    def criar_pix(self, pedido):
        raise NotImplementedError()

    def criar_cartao(self, pedido):
        raise NotImplementedError()

    def criar_boleto(self, pedido):
        raise NotImplementedError()