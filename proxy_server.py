import socket, sys
from thread import *

try:
    listening_port = int(raw_input("[*] Digite o numero da porta: [*]"))
except KeyboardInterrupt:
    print "\n[*] Interrompido pelo usuario [*]"
    sys.exit()

max_conn = 5
buffer_size = 4096

def start():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Inicia socket
        print "[*] Iniciando sockets... [*]"
        s.bind(('', listening_port)) #Bind socket
        print "[*] Sockets vinculados com sucesso [*]"
        s.listen(max_conn) #Comeca a esperar conexoes

        print ("[*] Servidor iniciado com sucesso [ %d ][*]\n" % (listening_port))

    except Exception, e:
        # Esse bloco eh executado se qualquer coisa falhar
        print "[*] Nao foi possivel iniciar o socket [*]"
        sys.exit(2)

    while 1:
        try:
            conn, addr = s.accept() #Aceita conexao do browser
            data = conn.recv(buffer_size) #Recebe dados do browser
            start_new_thread(conn_string, (conn, data, addr)) #Inicia uma thread

        except KeyboardInterrupt:
            # Esse bloco eh executado se o socket do client falhar
            s.close()
            print"\n[*] Encerrando servidor proxy [*]"
            sys.exit(1)

    s.close()

def conn_string(conn, data, addr):
    #Browser requests
    try:
        first_line = data.split('\n')[0]
        url = first_line.split('')[1]
        http_pos = url.find("://") #Encontra a posicao do ://

        if http_pos == -1:
            temp = url
        else:
            temp = url[(http_pos+3):] #Pega o resto da url

        port_pos = temp.find(":") #Encontra a posicao da porta (se tiver)
        webserver_pos = temp.find("/") #Encontra o final do web server

        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1

        if (port_pos == -1 or webserver_pos < port_pos): #Porta default
            port = 80
            webserver = temp[:webserver_pos]
        else:
            #Porta especifica
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]

        proxy_server(webserver, port, conn, addr, data)

    except Exception, e:
        pass

def proxy_server(webserver, port, conn, addr, data):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(data)

        while 1:
            #Le a resposta ou os dados do web server final
            reply = s.recv(buffer_size)

            if len(reply) > 0:
                conn.send(reply) #Manda resposta de volta pro client
                #Manda notificacao para o servidor proxy
                dar = float(len(reply))
                dar = float(dar / 1024)
                dar = "%.3s" % (str(dar))
                dar = "%s KB" % (dar)
                print "[*] Requisicao completa: %s => %s <=" % (str(addr[0]),str(dar))
            else:
                #Encerra conexao se houver falha no recebimento dos dados
                break

        #Fecha os sockets do servidor
        s.close()
        #Fecha os sockets do client
        conn.close()

    except socket.error, (value, message):
        s.close()
        conn.close()
        sys.exit(1)

start()




