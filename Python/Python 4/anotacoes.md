# Anotações Aula Python 4

* Quando threads compartilham acesso a variáveis, é necessário tratar isso
    * Deve-se identificar as 'seções críticas' onde esse compartilhamento ocorre e garantir que as instruções de uma thread nessa seção crítica não possam ser interrompidas por outra thread
    * Utiliza-se o objeto lock
        * lock.acquire bloqueia a seção crítica, de modo que outras threads não consigam entrar nela
        * lock.release libera o recurso para que outra thread possa, por sua vez, entrar nessa seção crítica
        * Garante que na seção crítica, apenas uma thread execute por vez